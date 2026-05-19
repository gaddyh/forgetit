import json
import dspy

from app.models import MemoryExtraction


class ExtractMemorySignature(dspy.Signature):
    """
    Extract a safe-to-forget memory item from a short human message.

    Rules:
    - Complete actionable memory needs time and context.
    - Complete reference memory needs enough context to be searchable later.
    - If existing_memory is provided, merge the new message into it.
    - Do not invent missing fields.
    """

    message: str = dspy.InputField(desc="The latest user message.")

    existing_memory_json: str | None = dspy.InputField(
        desc="Optional partial memory JSON from a previous turn, or null."
    )

    extraction: MemoryExtraction = dspy.OutputField(
        desc="MemoryExtraction object."
    )


class ExtractMemoryProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract = dspy.Predict(ExtractMemorySignature)

    def forward(
        self,
        message: str,
        existing_memory: dict | None = None,
    ) -> MemoryExtraction:
        existing_memory_json = (
            json.dumps(existing_memory, ensure_ascii=False)
            if existing_memory is not None
            else None
        )

        prediction = self.extract(
            message=message,
            existing_memory_json=existing_memory_json,
        )

        return prediction.extraction