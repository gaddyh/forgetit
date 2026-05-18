from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Literal

import dspy
from dotenv import load_dotenv
from pydantic import BaseModel, TypeAdapter

from app.item_judge import ItemSemanticJudge
from app.metrics import evaluate_predictions, print_metrics
from app.program import MemoryRouter, MemoryRouterResult


Action = Literal["save", "retrieve"]


class DatasetInput(BaseModel):
    split: Literal["train", "val", "test"]
    message: str


class DatasetOutput(BaseModel):
    action: Action
    item: str


class DatasetRow(BaseModel):
    id: str
    input: DatasetInput
    output: DatasetOutput


class EvaluatedRow(BaseModel):
    id: str
    input: DatasetInput
    expected: DatasetOutput
    predicted: DatasetOutput


DatasetRowsAdapter = TypeAdapter(list[DatasetRow])


def configure_dspy() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to .env or export it in your shell."
        )

    lm = dspy.LM(
        "openai/gpt-4o-mini",
        api_key=api_key,
    )

    dspy.configure(
        lm=lm,
        adapter=dspy.JSONAdapter(),
    )


def load_jsonl(path: Path) -> list[DatasetRow]:
    raw_rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                raw_rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL at line {line_number}: {e}") from e

    return DatasetRowsAdapter.validate_python(raw_rows)


def filter_split(rows: list[DatasetRow], split: str) -> list[DatasetRow]:
    if split == "all":
        return rows

    return [row for row in rows if row.input.split == split]


def to_dspy_examples(rows: list[DatasetRow]) -> list[dspy.Example]:
    examples: list[dspy.Example] = []

    for row in rows:
        examples.append(
            dspy.Example(
                message=row.input.message,
                action=row.output.action,
                item=row.output.item,
            ).with_inputs("message")
        )

    return examples


def normalize_text(value: Any) -> str:
    return " ".join(str(value).strip().split())


def normalize_action(value: Any) -> str:
    return str(value).strip().lower()


def make_forgetit_metric(item_judge: ItemSemanticJudge):
    """
    Binary optimization metric.

    Score:
      0.0 if action is wrong
      1.0 if action is correct and item refers to the same memory object
      0.0 otherwise

    This is intentionally harsh.
    """

    def metric(example: dspy.Example, pred: dspy.Prediction, trace: Any | None = None) -> float:
        expected_action = normalize_action(example.action)
        predicted_action = normalize_action(pred.action)

        if expected_action != predicted_action:
            return 0.0

        expected_item = normalize_text(example.item)
        predicted_item = normalize_text(pred.item)

        if expected_item == predicted_item:
            return 1.0

        judgment = item_judge(
            expected_item=expected_item,
            predicted_item=predicted_item,
        )

        return 1.0 if judgment.is_match else 0.0

    return metric


def evaluate_program(
    program: MemoryRouter,
    rows: list[DatasetRow],
    item_judge: ItemSemanticJudge,
    title: str,
) -> None:
    print("\n" + "#" * 80)
    print(title)
    print("#" * 80)

    evaluated_rows: list[EvaluatedRow] = []

    for row in rows:
        prediction: MemoryRouterResult = program(message=row.input.message)

        predicted = DatasetOutput(
            action=prediction.action,
            item=prediction.item,
        )

        evaluated = EvaluatedRow(
            id=row.id,
            input=row.input,
            expected=row.output,
            predicted=predicted,
        )

        evaluated_rows.append(evaluated)

        print("\n" + "=" * 80)
        print(f"ID:        {evaluated.id}")
        print(f"MESSAGE:   {evaluated.input.message}")
        print(
            "EXPECTED:  "
            + json.dumps(evaluated.expected.model_dump(), ensure_ascii=False)
        )
        print(
            "PREDICTED: "
            + json.dumps(evaluated.predicted.model_dump(), ensure_ascii=False)
        )

    metrics_rows = [
        {
            "id": row.id,
            "input": row.input.model_dump(),
            "expected": row.expected.model_dump(),
            "predicted": row.predicted.model_dump(),
        }
        for row in evaluated_rows
    ]

    def semantic_scorer(expected_item: str, predicted_item: str) -> bool:
        if normalize_text(expected_item) == normalize_text(predicted_item):
            return True

        judgment = item_judge(
            expected_item=expected_item,
            predicted_item=predicted_item,
        )
        return judgment.is_match

    metrics = evaluate_predictions(
        metrics_rows,
        item_semantic_scorer=semantic_scorer,
    )

    print_metrics(metrics)


def save_compiled_program(program: MemoryRouter, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        program.save(str(output_path))
    except Exception as e:
        raise RuntimeError(
            f"Failed to save compiled DSPy program to {output_path}. "
            f"Underlying error: {e}"
        ) from e


def optimize(
    dataset_path: Path,
    output_path: Path,
    train_split: str,
    eval_split: str,
    max_bootstrapped_demos: int,
    max_labeled_demos: int,
) -> None:
    configure_dspy()

    rows = load_jsonl(dataset_path)
    train_rows = filter_split(rows, train_split)
    eval_rows = filter_split(rows, eval_split)

    if not train_rows:
        raise RuntimeError(f"No training rows found for split={train_split!r}")

    if not eval_rows:
        raise RuntimeError(f"No eval rows found for split={eval_split!r}")

    trainset = to_dspy_examples(train_rows)

    item_judge = ItemSemanticJudge()

    baseline = MemoryRouter()

    evaluate_program(
        program=baseline,
        rows=eval_rows,
        item_judge=item_judge,
        title=f"BASELINE ON {eval_split.upper()}",
    )

    metric = make_forgetit_metric(item_judge)

    optimizer = dspy.BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        max_rounds=1,
    )

    print("\n" + "#" * 80)
    print("OPTIMIZING")
    print("#" * 80)
    print(f"Train rows: {len(train_rows)}")
    print(f"Eval rows:  {len(eval_rows)}")
    print(f"Output:     {output_path}")

    compiled = optimizer.compile(
        student=baseline,
        trainset=trainset,
    )

    evaluate_program(
        program=compiled,
        rows=eval_rows,
        item_judge=item_judge,
        title=f"OPTIMIZED ON {eval_split.upper()}",
    )

    save_compiled_program(compiled, output_path)

    print("\nSAVED")
    print("=" * 80)
    print(f"Compiled program saved to: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optimize ForgetIt memory router.")

    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/forgetit_v0.jsonl"),
        help="Path to the JSONL dataset.",
    )

    parser.add_argument(
        "--train-split",
        choices=["train", "val", "test", "all"],
        default="train",
        help="Split used for DSPy optimization.",
    )

    parser.add_argument(
        "--eval-split",
        choices=["train", "val", "test", "all"],
        default="val",
        help="Split used for before/after evaluation.",
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/memory_router_bootstrap.json"),
        help="Where to save the compiled DSPy program.",
    )

    parser.add_argument(
        "--max-bootstrapped-demos",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--max-labeled-demos",
        type=int,
        default=8,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    optimize(
        dataset_path=args.data,
        output_path=args.out,
        train_split=args.train_split,
        eval_split=args.eval_split,
        max_bootstrapped_demos=args.max_bootstrapped_demos,
        max_labeled_demos=args.max_labeled_demos,
    )


if __name__ == "__main__":
    main()