from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Literal

import dspy
from dotenv import load_dotenv
from pydantic import BaseModel, Field, TypeAdapter

from app.metrics import evaluate_predictions, print_metrics
from app.program import MemoryRouter, MemoryRouterResult
from app.item_judge import ItemSemanticJudge
from app.report import RowResult, make_run_id, render_eval_report, save_report

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


def to_metrics_row(row: EvaluatedRow) -> dict[str, Any]:
    return {
        "id": row.id,
        "input": row.input.model_dump(),
        "expected": row.expected.model_dump(),
        "predicted": row.predicted.model_dump(),
    }


def run_eval(dataset_path: Path, split: str) -> None:
    run_id = make_run_id()

    configure_dspy()

    dataset_rows = load_jsonl(dataset_path)
    dataset_rows = filter_split(dataset_rows, split)

    if not dataset_rows:
        raise RuntimeError(f"No rows found for split={split!r} in {dataset_path}")

    router = MemoryRouter()
    item_judge = ItemSemanticJudge()
    evaluated_rows: list[EvaluatedRow] = []

    for row in dataset_rows:
        prediction: MemoryRouterResult = router(message=row.input.message)

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

    metrics_rows = [to_metrics_row(row) for row in evaluated_rows]
    def semantic_scorer(expected_item: str, predicted_item: str) -> bool:
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

    row_results = [
        RowResult(
            id=row.id,
            message=row.input.message,
            expected_action=row.expected.action,
            expected_item=row.expected.item,
            predicted_action=row.predicted.action,
            predicted_item=row.predicted.item,
        )
        for row in evaluated_rows
    ]

    report_content = render_eval_report(
        run_id=run_id,
        dataset_path=str(dataset_path),
        split=split,
        model="gpt-4o-mini",
        rows=row_results,
        metrics=metrics,
    )

    report_path = save_report(run_id, report_content, filename="eval_report.md")
    print(f"Report saved to: {report_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate ForgetIt memory router.")

    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/forgetit_v0.jsonl"),
        help="Path to the JSONL dataset.",
    )

    parser.add_argument(
        "--split",
        choices=["train", "val", "test", "all"],
        default="val",
        help="Dataset split to evaluate.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_eval(dataset_path=args.data, split=args.split)


if __name__ == "__main__":
    main()