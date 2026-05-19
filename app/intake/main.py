import json
import os
import uuid
from datetime import datetime

import dspy
from dotenv import load_dotenv

from app.intake.models import MemoryExtraction
from app.intake.program import ExtractMemoryProgram


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


def print_memory(memory: dict) -> None:
    print("\nMEMORY")
    print("-" * 80)
    print(json.dumps(memory, ensure_ascii=False, indent=2))


def print_missing(fields: list[str]) -> None:
    print("\nMISSING FIELDS")
    print("-" * 80)

    for field in fields:
        print(f"- {field}")


def build_followup_question(missing_fields: list[str]) -> str:
    questions = []

    if "time" in missing_fields:
        questions.append("When?")

    if "context" in missing_fields:
        questions.append("Short context?")

    return " ".join(questions)

def apply_policy(result: dict) -> dict:
    memory = result.get("memory")

    if memory is None:
        return result

    missing = set(result.get("missing_fields", []))

    if memory.get("time"):
        missing.discard("time")

    if memory.get("context"):
        missing.discard("context")

    result["missing_fields"] = list(missing)

    if not result["missing_fields"]:
        result["status"] = "complete"

    return result

def preserve_existing_anchor(result: dict, existing_memory: dict | None) -> dict:
    if not existing_memory:
        return result

    memory = result.get("memory")
    if not memory:
        return result

    existing_anchor = existing_memory.get("anchor")
    if existing_anchor:
        memory["anchor"] = existing_anchor

    return result

def main() -> None:
    configure_dspy()

    program = ExtractMemoryProgram()

    session_id = str(uuid.uuid4())

    print("=" * 80)
    print("FORGETIT INTAKE")
    print(f"SESSION: {session_id}")
    print("=" * 80)

    current_memory = None

    while True:
        print("\n")
        user_input = input("> ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("\nBye.")
            break

        prediction: MemoryExtraction = program(
            message=user_input,
            existing_memory=current_memory,
        )

        result = prediction.model_dump()

        result = apply_policy(result)
        result = preserve_existing_anchor(result, current_memory)

        print("\nRESULT")
        print("-" * 80)
        print(json.dumps(result, ensure_ascii=False, indent=2))

        status = result["status"]

        if status == "complete":
            memory = result["memory"]

            saved_memory = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
                "memory": memory,
            }

            print_memory(saved_memory)

            print("\nSaved.")

            current_memory = None

        else:
            missing_fields = result.get("missing_fields", [])
            partial_memory = result.get("memory")

            if partial_memory is not None:
                current_memory = partial_memory
            else:
                current_memory = {
                    "mode": "actionable",
                    "anchor": user_input,
                    "time": None,
                    "context": None,
                    "link": None,
                }

            print_missing(missing_fields)

            followup = build_followup_question(missing_fields)

            if followup:
                print("\nBOT:")
                print(followup)


if __name__ == "__main__":
    main()