from __future__ import annotations

from typing import Literal

import dspy
from pydantic import BaseModel, Field


Action = Literal["save", "retrieve"]


class MemoryRouterResult(BaseModel):
    action: Action = Field(
        description="Either 'save' or 'retrieve'."
    )
    item: str = Field(
        description=(
            "The memory item. For save, write the clean item to remember. "
            "For retrieve, write the item the user is trying to find."
        )
    )


class RouteMemoryMessage(dspy.Signature):
    """
    Classify a short WhatsApp-style message as either saving memory or retrieving memory.

    Return only:
    - action: save or retrieve
    - item: the memory object

    Do not extract entities.
    Do not return people, subjects, locations, times, amounts, or links.
    Do not explain.
    """

    message: str = dspy.InputField(
        description="A short WhatsApp-style message from the user."
    )

    action: Action = dspy.OutputField(
        description="Either 'save' or 'retrieve'."
    )

    item: str = dspy.OutputField(
        description="The clean memory item being saved or searched for."
    )


class MemoryRouter(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.route = dspy.Predict(RouteMemoryMessage)

    def forward(self, message: str) -> MemoryRouterResult:
        prediction = self.route(message=message)

        return MemoryRouterResult(
            action=normalize_action(prediction.action),
            item=normalize_item(prediction.item),
        )


def normalize_action(value: str) -> Action:
    value = str(value).strip().lower()

    if value == "save":
        return "save"

    if value == "retrieve":
        return "retrieve"

    raise ValueError(f"Invalid action returned by model: {value!r}")


def normalize_item(value: str) -> str:
    return " ".join(str(value).strip().split())