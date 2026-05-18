from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


SemanticScorer = Callable[[str, str], bool]


@dataclass(frozen=True)
class ActionMetrics:
    action: str
    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class ItemMetrics:
    exact_matches: int
    token_f1_sum: float
    semantic_matches: int | None
    total: int
    exact_accuracy: float
    avg_token_f1: float
    semantic_accuracy: float | None


@dataclass(frozen=True)
class EvalMetrics:
    total: int
    action_accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    per_action: list[ActionMetrics]
    item: ItemMetrics


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""

    return " ".join(value.strip().lower().split())


def tokenize(value: str | None) -> list[str]:
    normalized = normalize_text(value)
    if not normalized:
        return []

    return normalized.split()


def safe_get_action(row: dict[str, Any], key: str) -> str:
    return normalize_text(row[key]["action"])


def safe_get_item(row: dict[str, Any], key: str) -> str:
    return normalize_text(row[key]["item"])


def precision(tp: int, fp: int) -> float:
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)


def recall(tp: int, fn: int) -> float:
    if tp + fn == 0:
        return 0.0
    return tp / (tp + fn)


def f1_score(p: float, r: float) -> float:
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def token_f1(expected: str, predicted: str) -> float:
    expected_tokens = tokenize(expected)
    predicted_tokens = tokenize(predicted)

    if not expected_tokens and not predicted_tokens:
        return 1.0

    if not expected_tokens or not predicted_tokens:
        return 0.0

    expected_counts: dict[str, int] = {}
    predicted_counts: dict[str, int] = {}

    for token in expected_tokens:
        expected_counts[token] = expected_counts.get(token, 0) + 1

    for token in predicted_tokens:
        predicted_counts[token] = predicted_counts.get(token, 0) + 1

    overlap = 0

    for token, expected_count in expected_counts.items():
        predicted_count = predicted_counts.get(token, 0)
        overlap += min(expected_count, predicted_count)

    if overlap == 0:
        return 0.0

    p = overlap / len(predicted_tokens)
    r = overlap / len(expected_tokens)

    return f1_score(p, r)


def evaluate_predictions(
    rows: list[dict[str, Any]],
    *,
    expected_key: str = "expected",
    predicted_key: str = "predicted",
    item_semantic_scorer: SemanticScorer | None = None,
) -> EvalMetrics:
    """
    Expected row shape:

    {
        "input": {"message": "..."},
        "expected": {
            "action": "save",
            "item": "..."
        },
        "predicted": {
            "action": "save",
            "item": "..."
        }
    }

    item_semantic_scorer:
        Optional function that receives:
            expected_item: str
            predicted_item: str

        And returns:
            True  -> same memory object
            False -> different memory object
    """

    if not rows:
        return EvalMetrics(
            total=0,
            action_accuracy=0.0,
            macro_precision=0.0,
            macro_recall=0.0,
            macro_f1=0.0,
            per_action=[],
            item=ItemMetrics(
                exact_matches=0,
                token_f1_sum=0.0,
                semantic_matches=None,
                total=0,
                exact_accuracy=0.0,
                avg_token_f1=0.0,
                semantic_accuracy=None,
            ),
        )

    labels: set[str] = set()

    for row in rows:
        labels.add(safe_get_action(row, expected_key))
        labels.add(safe_get_action(row, predicted_key))

    counts = {
        label: {"tp": 0, "fp": 0, "fn": 0}
        for label in sorted(labels)
    }

    correct_actions = 0
    exact_item_matches = 0
    item_token_f1_sum = 0.0
    semantic_matches = 0 if item_semantic_scorer is not None else None

    for row in rows:
        expected_action = safe_get_action(row, expected_key)
        predicted_action = safe_get_action(row, predicted_key)

        expected_item = safe_get_item(row, expected_key)
        predicted_item = safe_get_item(row, predicted_key)

        if expected_action == predicted_action:
            correct_actions += 1
            counts[expected_action]["tp"] += 1
        else:
            counts[predicted_action]["fp"] += 1
            counts[expected_action]["fn"] += 1

        if expected_item == predicted_item:
            exact_item_matches += 1

        item_token_f1_sum += token_f1(expected_item, predicted_item)

        if item_semantic_scorer is not None:
            assert semantic_matches is not None
            if item_semantic_scorer(expected_item, predicted_item):
                semantic_matches += 1

    per_action: list[ActionMetrics] = []

    for action, values in counts.items():
        tp = values["tp"]
        fp = values["fp"]
        fn = values["fn"]

        p = precision(tp, fp)
        r = recall(tp, fn)
        f1 = f1_score(p, r)

        per_action.append(
            ActionMetrics(
                action=action,
                tp=tp,
                fp=fp,
                fn=fn,
                precision=p,
                recall=r,
                f1=f1,
            )
        )

    macro_precision = sum(m.precision for m in per_action) / len(per_action)
    macro_recall = sum(m.recall for m in per_action) / len(per_action)
    macro_f1 = sum(m.f1 for m in per_action) / len(per_action)

    total = len(rows)

    semantic_accuracy = None
    if semantic_matches is not None:
        semantic_accuracy = semantic_matches / total

    return EvalMetrics(
        total=total,
        action_accuracy=correct_actions / total,
        macro_precision=macro_precision,
        macro_recall=macro_recall,
        macro_f1=macro_f1,
        per_action=per_action,
        item=ItemMetrics(
            exact_matches=exact_item_matches,
            token_f1_sum=item_token_f1_sum,
            semantic_matches=semantic_matches,
            total=total,
            exact_accuracy=exact_item_matches / total,
            avg_token_f1=item_token_f1_sum / total,
            semantic_accuracy=semantic_accuracy,
        ),
    )


def print_metrics(metrics: EvalMetrics) -> None:
    print("\nOVERALL")
    print("=" * 80)
    print(f"Total:           {metrics.total}")
    print(f"Action Accuracy: {metrics.action_accuracy:.4f}")
    print(f"Macro Precision: {metrics.macro_precision:.4f}")
    print(f"Macro Recall:    {metrics.macro_recall:.4f}")
    print(f"Macro F1:        {metrics.macro_f1:.4f}")

    print("\nPER ACTION")
    print("=" * 80)
    print(
        f"{'Action':<12} "
        f"{'TP':>4} "
        f"{'FP':>4} "
        f"{'FN':>4} "
        f"{'Precision':>10} "
        f"{'Recall':>10} "
        f"{'F1':>10}"
    )
    print("-" * 80)

    for row in metrics.per_action:
        print(
            f"{row.action:<12} "
            f"{row.tp:>4} "
            f"{row.fp:>4} "
            f"{row.fn:>4} "
            f"{row.precision:>10.4f} "
            f"{row.recall:>10.4f} "
            f"{row.f1:>10.4f}"
        )

    print("\nITEM")
    print("=" * 80)
    print(f"Exact Matches:      {metrics.item.exact_matches}/{metrics.item.total}")
    print(f"Exact Accuracy:     {metrics.item.exact_accuracy:.4f}")
    print(f"Average Token F1:   {metrics.item.avg_token_f1:.4f}")

    if metrics.item.semantic_accuracy is not None:
        print(
            f"Semantic Matches:   "
            f"{metrics.item.semantic_matches}/{metrics.item.total}"
        )
        print(f"Semantic Accuracy:  {metrics.item.semantic_accuracy:.4f}")