from __future__ import annotations

from typing import Any

import dspy
from dspy.evaluate import SemanticF1


semantic_f1 = SemanticF1(decompositional=True)


def forgetit_metric(example: Any, pred: Any, trace: Any | None = None) -> float:
    """
    Single scalar optimization score for ForgetIt v0.

    Expected example fields:
        action: expected action
        item: expected memory item

    Prediction fields:
        action: predicted action
        item: predicted memory item

    Rule:
        Wrong action => 0.0
        Correct action => semantic F1 over item
    """

    expected_action = normalize_action(example.action)
    predicted_action = normalize_action(pred.action)

    if expected_action != predicted_action:
        return 0.0

    item_example = dspy.Example(
        response=normalize_text(example.item)
    ).with_inputs()

    item_prediction = dspy.Prediction(
        response=normalize_text(pred.item)
    )

    return float(semantic_f1(item_example, item_prediction))


def normalize_action(value: Any) -> str:
    return str(value).strip().lower()


def normalize_text(value: Any) -> str:
    return " ".join(str(value).strip().split())