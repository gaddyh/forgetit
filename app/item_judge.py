from __future__ import annotations

from typing import Literal

import dspy
from pydantic import BaseModel, Field


class ItemSemanticJudgment(BaseModel):
    is_match: bool = Field(
        description=(
            "True if the predicted item refers to the same memory object "
            "as the expected item."
        )
    )
    reason: str = Field(
        description="Short reason for the judgment."
    )


class JudgeItemSemanticMatch(dspy.Signature):
    """
    Judge whether two Hebrew memory item strings refer to the same memory object.

    The strings do not need to be identical.

    Mark as match when:
    - one is a cleaner phrasing of the other
    - one contains harmless filler words
    - both point to the same saved fact, task, address, amount, person, link, or note

    Mark as not match when:
    - important information is missing
    - the predicted item is only a vague category
    - the amount, time, person, object, location, or link is missing when essential
    - the predicted item refers to the user's question instead of the remembered object

    Examples:
    expected: "מייבש כביסה לבן"
    predicted: "מייבש כביסה עדיף לבן"
    is_match: true

    expected: "הדס 20 בנימינה"
    predicted: "הכתובת בבנימינה"
    is_match: false

    expected: "יוסי 300000 בקרנות"
    predicted: "יוסי בקרנות"
    is_match: false

    expected: "מתנה לשי"
    predicted: "המתנה לשי"
    is_match: true
    """

    expected_item: str = dspy.InputField()
    predicted_item: str = dspy.InputField()

    is_match: bool = dspy.OutputField()
    reason: str = dspy.OutputField()


class ItemSemanticJudge(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.judge = dspy.Predict(JudgeItemSemanticMatch)

    def forward(self, expected_item: str, predicted_item: str) -> ItemSemanticJudgment:
        prediction = self.judge(
            expected_item=expected_item,
            predicted_item=predicted_item,
        )

        return ItemSemanticJudgment(
            is_match=bool(prediction.is_match),
            reason=str(prediction.reason).strip(),
        )