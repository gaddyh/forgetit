from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.metrics import EvalMetrics


@dataclass
class RowResult:
    id: str
    message: str
    expected_action: str
    expected_item: str
    predicted_action: str
    predicted_item: str


def make_run_id() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def _metrics_block(metrics: EvalMetrics) -> str:
    lines: list[str] = []

    lines += [
        "**Overall**",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total | {metrics.total} |",
        f"| Action Accuracy | {metrics.action_accuracy:.4f} |",
        f"| Macro Precision | {metrics.macro_precision:.4f} |",
        f"| Macro Recall | {metrics.macro_recall:.4f} |",
        f"| Macro F1 | {metrics.macro_f1:.4f} |",
        "",
        "**Per Action**",
        "",
        "| Action | TP | FP | FN | Precision | Recall | F1 |",
        "|---|---|---|---|---|---|---|",
    ]

    for a in metrics.per_action:
        lines.append(
            f"| {a.action} | {a.tp} | {a.fp} | {a.fn} "
            f"| {a.precision:.4f} | {a.recall:.4f} | {a.f1:.4f} |"
        )

    lines += [
        "",
        "**Item**",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Exact Matches | {metrics.item.exact_matches} / {metrics.item.total} |",
        f"| Exact Accuracy | {metrics.item.exact_accuracy:.4f} |",
        f"| Average Token F1 | {metrics.item.avg_token_f1:.4f} |",
    ]

    if metrics.item.semantic_accuracy is not None:
        lines += [
            f"| Semantic Matches | {metrics.item.semantic_matches} / {metrics.item.total} |",
            f"| Semantic Accuracy | {metrics.item.semantic_accuracy:.4f} |",
        ]

    return "\n".join(lines)


def _rows_table(rows: list[RowResult]) -> str:
    lines = [
        "| ID | Message | Expected Action | Predicted Action | Expected Item | Predicted Item |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        action_ok = row.expected_action == row.predicted_action
        predicted_action = row.predicted_action if action_ok else f"**{row.predicted_action}**"
        lines.append(
            f"| {row.id} | {row.message} | {row.expected_action} "
            f"| {predicted_action} | {row.expected_item} | {row.predicted_item} |"
        )

    return "\n".join(lines)


def render_eval_report(
    run_id: str,
    dataset_path: str,
    split: str,
    model: str,
    rows: list[RowResult],
    metrics: EvalMetrics,
) -> str:
    sections: list[str] = [
        "# Eval Report",
        "",
        f"Run: `{run_id}`",
        f"Dataset: `{dataset_path}`",
        f"Split: `{split}`",
        f"Model: `{model}`",
        "",
        "---",
        "",
        "## Metrics",
        "",
        _metrics_block(metrics),
        "",
        "---",
        "",
        "## Results",
        "",
        _rows_table(rows),
    ]

    return "\n".join(sections)


def render_optimize_report(
    run_id: str,
    dataset_path: str,
    train_split: str,
    eval_split: str,
    model: str,
    optimizer: str,
    max_bootstrapped_demos: int,
    max_labeled_demos: int,
    artifact_path: str,
    baseline_rows: list[RowResult],
    baseline_metrics: EvalMetrics,
    optimized_rows: list[RowResult],
    optimized_metrics: EvalMetrics,
) -> str:
    delta_action = optimized_metrics.action_accuracy - baseline_metrics.action_accuracy
    delta_exact = optimized_metrics.item.exact_accuracy - baseline_metrics.item.exact_accuracy
    delta_token_f1 = optimized_metrics.item.avg_token_f1 - baseline_metrics.item.avg_token_f1

    delta_semantic = None
    if (
        optimized_metrics.item.semantic_accuracy is not None
        and baseline_metrics.item.semantic_accuracy is not None
    ):
        delta_semantic = optimized_metrics.item.semantic_accuracy - baseline_metrics.item.semantic_accuracy

    def fmt_delta(v: float) -> str:
        return f"+{v:.4f}" if v >= 0 else f"{v:.4f}"

    delta_rows = [
        "| Metric | Baseline | Optimized | Delta |",
        "|---|---|---|---|",
        f"| Action Accuracy | {baseline_metrics.action_accuracy:.4f} | {optimized_metrics.action_accuracy:.4f} | {fmt_delta(delta_action)} |",
        f"| Exact Accuracy | {baseline_metrics.item.exact_accuracy:.4f} | {optimized_metrics.item.exact_accuracy:.4f} | {fmt_delta(delta_exact)} |",
        f"| Avg Token F1 | {baseline_metrics.item.avg_token_f1:.4f} | {optimized_metrics.item.avg_token_f1:.4f} | {fmt_delta(delta_token_f1)} |",
    ]

    if delta_semantic is not None:
        delta_rows.append(
            f"| Semantic Accuracy | {baseline_metrics.item.semantic_accuracy:.4f} "
            f"| {optimized_metrics.item.semantic_accuracy:.4f} | {fmt_delta(delta_semantic)} |"
        )

    sections: list[str] = [
        "# Optimize Report",
        "",
        f"Run: `{run_id}`",
        f"Dataset: `{dataset_path}`",
        f"Train split: `{train_split}`",
        f"Eval split: `{eval_split}`",
        f"Model: `{model}`",
        f"Optimizer: `{optimizer}`",
        f"max_bootstrapped_demos: `{max_bootstrapped_demos}`",
        f"max_labeled_demos: `{max_labeled_demos}`",
        f"Artifact: `{artifact_path}`",
        "",
        "---",
        "",
        "## Baseline",
        "",
        _metrics_block(baseline_metrics),
        "",
        "---",
        "",
        "## Optimized",
        "",
        _metrics_block(optimized_metrics),
        "",
        "---",
        "",
        "## Delta",
        "",
        "\n".join(delta_rows),
        "",
        "---",
        "",
        "## Baseline Results",
        "",
        _rows_table(baseline_rows),
        "",
        "---",
        "",
        "## Optimized Results",
        "",
        _rows_table(optimized_rows),
    ]

    return "\n".join(sections)


def save_report(run_id: str, content: str, filename: str = "optimize_report.md") -> Path:
    run_dir = Path("artifacts") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    report_path = run_dir / filename
    report_path.write_text(content, encoding="utf-8")

    return report_path
