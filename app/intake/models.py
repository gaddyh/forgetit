from typing import Literal

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """
    A future-retrievable memory unit.

    The goal is not perfect semantic understanding.

    The goal is:
    can future-you understand and act on this later?
    """

    mode: Literal["actionable", "reference"]

    anchor: str = Field(
        description=(
            "The main handle of the memory. "
            "Usually a person, subject, object, or short phrase."
        )
    )

    time: str | None = Field(
        default=None,
        description=(
            "Natural language future time reference. "
            "Examples: 'tomorrow', 'next week', 'Friday morning'."
        )
    )

    context: str | None = Field(
        default=None,
        description=(
            "Short future context explaining why this memory matters "
            "or what future-you should understand."
        )
    )

    link: str | None = Field(
        default=None,
        description="Optional URL or external reference."
    )


class MemoryExtraction(BaseModel):
    """
    Output of the extraction step.

    The system either:
    - determines the memory is complete
    - or identifies missing fields
    """

    status: Literal["complete", "incomplete"]

    memory: MemoryItem | None = None

    missing_fields: list[Literal["time", "context"]] = Field(
        default_factory=list
    )