import json
import os
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

from app.metrics import score_row, summarize
from app.program import ExtractMemoryProgram


DATA_PATH = Path("data/save_memory_val.jsonl")


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


def to_plain_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    raise TypeError(f"Cannot convert prediction to dict: {type(value)}")


def run_eval(path: Path = DATA_PATH) -> None:
    configure_dspy()

    program = ExtractMemoryProgram()
    rows = load_jsonl(path)

    results = []

    for i, row in enumerate(rows, start=1):
        message = row["message"]
        existing_memory = row.get("existing_memory")
        expected = row["expected"]

        prediction = program(
            message=message,
            existing_memory=existing_memory,
        )

        predicted = to_plain_dict(prediction)
        metrics = score_row(expected, predicted)
        results.append(metrics)

        print("=" * 80)
        print(f"ROW {i}")
        print(f"MESSAGE: {message}")

        if existing_memory:
            print(f"EXISTING: {json.dumps(existing_memory, ensure_ascii=False)}")

        print("\nEXPECTED:")
        print(json.dumps(expected, ensure_ascii=False, indent=2))

        print("\nPREDICTED:")
        print(json.dumps(predicted, ensure_ascii=False, indent=2))

        print("\nMETRICS:")
        print(metrics)

    print("=" * 80)
    print("SUMMARY")
    print(json.dumps(summarize(results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_eval()