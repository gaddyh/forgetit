from dataclasses import dataclass
from typing import Any


def normalize(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())


def exact_match(expected: str | None, predicted: str | None) -> float:
    return 1.0 if normalize(expected) == normalize(predicted) else 0.0


def token_f1(expected: str | None, predicted: str | None) -> float:
    expected_tokens = set(normalize(expected).split())
    predicted_tokens = set(normalize(predicted).split())

    if not expected_tokens and not predicted_tokens:
        return 1.0

    if not expected_tokens or not predicted_tokens:
        return 0.0

    tp = len(expected_tokens & predicted_tokens)
    fp = len(predicted_tokens - expected_tokens)
    fn = len(expected_tokens - predicted_tokens)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0

    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def list_f1(expected: list[str], predicted: list[str]) -> float:
    expected_set = {normalize(x) for x in expected if normalize(x)}
    predicted_set = {normalize(x) for x in predicted if normalize(x)}

    if not expected_set and not predicted_set:
        return 1.0

    if not expected_set or not predicted_set:
        return 0.0

    tp = len(expected_set & predicted_set)
    fp = len(predicted_set - expected_set)
    fn = len(expected_set - predicted_set)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0

    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


@dataclass(frozen=True)
class RowMetrics:
    status_match: float

    false_complete: float
    false_incomplete: float

    missing_fields_f1: float | None

    mode_match: float | None
    anchor_match: float | None
    time_match: float | None
    context_exact_match: float | None
    context_token_f1: float | None
    link_match: float | None

    memory_field_score: float | None
    product_score: float


def get_memory(result: dict[str, Any]) -> dict[str, Any] | None:
    return result.get("memory")


def score_row(expected: dict[str, Any], predicted: dict[str, Any]) -> RowMetrics:
    expected_status = expected.get("status")
    predicted_status = predicted.get("status")

    expected_complete = expected_status == "complete"
    predicted_complete = predicted_status == "complete"

    status_match = 1.0 if expected_status == predicted_status else 0.0

    false_complete = 1.0 if not expected_complete and predicted_complete else 0.0
    false_incomplete = 1.0 if expected_complete and not predicted_complete else 0.0

    missing_fields_f1 = None
    if expected_status == "incomplete":
        missing_fields_f1 = list_f1(
            expected.get("missing_fields", []),
            predicted.get("missing_fields", []),
        )

    expected_memory = get_memory(expected)
    predicted_memory = get_memory(predicted)

    mode_match = None
    anchor_match = None
    time_match = None
    context_exact_match = None
    context_token_f1 = None
    link_match = None
    memory_field_score = None

    if expected_memory is not None and predicted_memory is not None:
        mode_match = exact_match(
            expected_memory.get("mode"),
            predicted_memory.get("mode"),
        )
        anchor_match = exact_match(
            expected_memory.get("anchor"),
            predicted_memory.get("anchor"),
        )
        time_match = exact_match(
            expected_memory.get("time"),
            predicted_memory.get("time"),
        )
        context_exact_match = exact_match(
            expected_memory.get("context"),
            predicted_memory.get("context"),
        )
        context_token_f1 = token_f1(
            expected_memory.get("context"),
            predicted_memory.get("context"),
        )
        link_match = exact_match(
            expected_memory.get("link"),
            predicted_memory.get("link"),
        )

        memory_field_score = (
            0.15 * mode_match
            + 0.20 * anchor_match
            + 0.20 * time_match
            + 0.35 * context_token_f1
            + 0.10 * link_match
        )

    # Product score: more honest than simple average.
    # Complete rows care mostly about status + usable memory.
    # Incomplete rows care mostly about status + missing fields.
    if expected_complete:
        product_score = (
            0.50 * status_match
            + 0.50 * (memory_field_score or 0.0)
        )
    else:
        product_score = (
            0.60 * status_match
            + 0.40 * (missing_fields_f1 or 0.0)
        )

    return RowMetrics(
        status_match=status_match,
        false_complete=false_complete,
        false_incomplete=false_incomplete,
        missing_fields_f1=missing_fields_f1,
        mode_match=mode_match,
        anchor_match=anchor_match,
        time_match=time_match,
        context_exact_match=context_exact_match,
        context_token_f1=context_token_f1,
        link_match=link_match,
        memory_field_score=memory_field_score,
        product_score=product_score,
    )


def average(values: list[float | None]) -> float:
    real_values = [v for v in values if v is not None]
    return sum(real_values) / len(real_values) if real_values else 0.0


def summarize(results: list[RowMetrics]) -> dict[str, float]:
    return {
        "status_match": average([r.status_match for r in results]),
        "false_complete_rate": average([r.false_complete for r in results]),
        "false_incomplete_rate": average([r.false_incomplete for r in results]),
        "missing_fields_f1": average([r.missing_fields_f1 for r in results]),
        "mode_match": average([r.mode_match for r in results]),
        "anchor_match": average([r.anchor_match for r in results]),
        "time_match": average([r.time_match for r in results]),
        "context_exact_match": average([r.context_exact_match for r in results]),
        "context_token_f1": average([r.context_token_f1 for r in results]),
        "link_match": average([r.link_match for r in results]),
        "memory_field_score": average([r.memory_field_score for r in results]),
        "product_score": average([r.product_score for r in results]),
    }