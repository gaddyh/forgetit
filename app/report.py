import csv
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


METRIC_FIELDS = [
    "status_match",
    "false_complete",
    "false_incomplete",
    "missing_fields_f1",
    "mode_match",
    "anchor_match",
    "time_match",
    "context_exact_match",
    "context_token_f1",
    "link_match",
    "memory_field_score",
    "product_score",
]


def create_run_dir(run_id: str | None = None, base_dir: str | Path = "artifacts") -> Path:
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_dir = Path(base_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def to_jsonable(value: Any) -> Any:
    if value is None:
        return None

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if is_dataclass(value):
        return asdict(value)

    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}

    if isinstance(value, list):
        return [to_jsonable(v) for v in value]

    return value


def format_metric(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def build_row_record(
    index: int,
    row: dict[str, Any],
    predicted: dict[str, Any],
    metrics: Any,
    score: float | None = None,
) -> dict[str, Any]:
    expected = row["expected"]

    record = {
        "row": index,
        "message": row["message"],
        "existing_memory": row.get("existing_memory"),
        "expected": expected,
        "predicted": predicted,
        "score": score if score is not None else getattr(metrics, "product_score", None),
        "metrics": to_jsonable(metrics),
    }

    return record


def save_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(to_jsonable(value), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_row_metrics_csv(path: Path, row_records: list[dict[str, Any]]) -> None:
    fieldnames = [
        "row",
        "message",
        "expected_status",
        "predicted_status",
        "score",
        *METRIC_FIELDS,
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for record in row_records:
            expected = record["expected"]
            predicted = record["predicted"]
            metrics = record["metrics"]

            writer.writerow(
                {
                    "row": record["row"],
                    "message": record["message"],
                    "expected_status": expected.get("status"),
                    "predicted_status": predicted.get("status"),
                    "score": format_metric(record["score"]),
                    **{
                        field: format_metric(metrics.get(field))
                        for field in METRIC_FIELDS
                    },
                }
            )


def save_summary_csv(path: Path, summary: dict[str, float]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value"])
        writer.writeheader()

        for key, value in summary.items():
            writer.writerow({"metric": key, "value": format_metric(value)})


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        lines.append("| " + " | ".join(format_metric(v) for v in row) + " |")

    return "\n".join(lines)


def save_markdown_report(
    path: Path,
    *,
    title: str,
    run_id: str,
    dataset_path: str,
    row_records: list[dict[str, Any]],
    summary: dict[str, float],
    notes: list[str] | None = None,
) -> None:
    row_table = markdown_table(
        [
            "Row",
            "Message",
            "Expected",
            "Predicted",
            "Score",
            "Status",
            "False Complete",
            "False Incomplete",
            "Missing F1",
            "Context F1",
            "Product",
        ],
        [
            [
                r["row"],
                r["message"],
                r["expected"].get("status"),
                r["predicted"].get("status"),
                r["score"],
                r["metrics"].get("status_match"),
                r["metrics"].get("false_complete"),
                r["metrics"].get("false_incomplete"),
                r["metrics"].get("missing_fields_f1"),
                r["metrics"].get("context_token_f1"),
                r["metrics"].get("product_score"),
            ]
            for r in row_records
        ],
    )

    summary_table = markdown_table(
        ["Metric", "Value"],
        [[key, value] for key, value in summary.items()],
    )

    notes_text = ""
    if notes:
        notes_text = "\n\n## Notes\n\n" + "\n".join(f"- {note}" for note in notes)

    content = f"""# {title}

**Run ID:** `{run_id}`

**Dataset:** `{dataset_path}`

**Rows:** {len(row_records)}

## Row-Level Metrics

{row_table}

## Summary Metrics

{summary_table}

## Artifacts

- `rows.json`
- `summary.json`
- `row_metrics.csv`
- `summary.csv`
- `report.md`
{notes_text}
"""

    path.write_text(content, encoding="utf-8")


def save_run_report(
    *,
    run_id: str | None,
    title: str,
    dataset_path: str | Path,
    row_records: list[dict[str, Any]],
    summary: dict[str, float],
    notes: list[str] | None = None,
    base_dir: str | Path = "artifacts",
) -> Path:
    run_dir = create_run_dir(run_id=run_id, base_dir=base_dir)

    save_json(run_dir / "rows.json", row_records)
    save_json(run_dir / "summary.json", summary)
    save_row_metrics_csv(run_dir / "row_metrics.csv", row_records)
    save_summary_csv(run_dir / "summary.csv", summary)

    save_markdown_report(
        run_dir / "report.md",
        title=title,
        run_id=run_dir.name,
        dataset_path=str(dataset_path),
        row_records=row_records,
        summary=summary,
        notes=notes,
    )

    return run_dir