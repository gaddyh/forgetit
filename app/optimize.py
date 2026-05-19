import json
import os
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

from app.metrics import score_row, summarize
from app.program import ExtractMemoryProgram
from app.report import build_row_record, save_run_report


TRAIN_PATH = Path("data/save_memory_train.jsonl")
VAL_PATH = Path("data/save_memory_val.jsonl")
OUTPUT_PATH = Path("artifacts/compiled_memory_program.json")


def configure_dspy() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")

    lm = dspy.LM(
        "openai/gpt-4o-mini",
        api_key=api_key,
    )

    dspy.configure(lm=lm)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return rows


def to_examples(rows: list[dict[str, Any]]) -> list[dspy.Example]:
    examples = []

    for row in rows:
        example = dspy.Example(
            message=row["message"],
            existing_memory=row.get("existing_memory"),
            expected=row["expected"],
        ).with_inputs("message", "existing_memory")

        examples.append(example)

    return examples


def to_plain_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    raise TypeError(f"Cannot convert prediction to dict: {type(value)}")


def memory_optimization_metric(example: dspy.Example, pred: Any, trace=None) -> float:
    expected = example.expected

    try:
        if hasattr(pred, "extraction"):
            predicted = to_plain_dict(pred.extraction)
        else:
            predicted = to_plain_dict(pred)
    except Exception:
        return 0.0

    metrics = score_row(expected, predicted)

    # Dangerous: system says memory is complete when expected incomplete.
    if metrics.false_complete:
        return 0.0

    # Bad UX but not dangerous: system is too cautious.
    if metrics.false_incomplete:
        return 0.25 * (metrics.memory_field_score or 0.0)

    return metrics.product_score


def evaluate_program(
    program: dspy.Module, examples: list[dspy.Example], label: str
) -> tuple[list, list]:
    scores = []
    row_records = []
    results = []

    print("=" * 80)
    print(label)

    for i, example in enumerate(examples, start=1):
        pred = program(
            message=example.message,
            existing_memory=example.existing_memory,
        )

        score = memory_optimization_metric(example, pred)
        scores.append(score)

        try:
            if hasattr(pred, "extraction"):
                predicted = to_plain_dict(pred.extraction)
            else:
                predicted = to_plain_dict(pred)
        except Exception:
            predicted = {}

        metrics_obj = score_row(example.expected, predicted)
        results.append(metrics_obj)

        row = {
            "message": example.message,
            "existing_memory": example.existing_memory,
            "expected": example.expected,
        }
        row_records.append(
            build_row_record(index=i, row=row, predicted=predicted, metrics=metrics_obj, score=score)
        )

        print(f"ROW {i}: {score:.3f} | {example.message}")

    avg = sum(scores) / len(scores) if scores else 0.0

    print("-" * 80)
    print(f"{label} AVG: {avg:.3f}")

    return row_records, results


def main() -> None:
    configure_dspy()

    train_rows = load_jsonl(TRAIN_PATH)
    val_rows = load_jsonl(VAL_PATH)

    trainset = to_examples(train_rows)
    valset = to_examples(val_rows)

    baseline = ExtractMemoryProgram()

    row_records, results = evaluate_program(baseline, valset, "BASELINE VAL")
    run_dir = save_run_report(
        run_id=None,
        title="ForgetIt Optimization Report - Baseline",
        dataset_path=VAL_PATH,
        row_records=row_records,
        summary=summarize(results),
        notes=["Baseline pre-optimization evaluation."],
    )
    print(f"Saved report to: {run_dir / 'report.md'}")

    optimizer = dspy.MIPROv2(
        metric=memory_optimization_metric,
        auto="light",
    )

    compiled_program = optimizer.compile(
        baseline,
        trainset=trainset,
        valset=valset,
    )

    row_records, results = evaluate_program(compiled_program, valset, "COMPILED VAL")
    run_dir = save_run_report(
        run_id=None,
        title="ForgetIt Optimization Report - Compiled",
        dataset_path=VAL_PATH,
        row_records=row_records,
        summary=summarize(results),
        notes=["Post-optimization compiled program evaluation."],
    )
    print(f"Saved report to: {run_dir / 'report.md'}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    compiled_program.save(str(OUTPUT_PATH))

    print("=" * 80)
    print(f"Saved compiled program to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()