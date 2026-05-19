# ForgetIt

ForgetIt is a dataset-first AI engineering experiment focused on one question:

> When is a human memory fragment safe to forget?

The project explores cognitive memory completion.

Instead of building agents, RAG pipelines, orchestration frameworks, or chatbot infrastructure first, ForgetIt starts from manual behavioral definition:

```text
human examples
    -> dataset
        -> metrics
            -> evaluation
                -> optimization
```

The project intentionally begins with the smallest possible cognitive layer.

Not:

* assistants
* agents
* tools
* memory stores
* vector databases
* retrieval systems

Instead:

```text
short messy memory fragments
    -> usable future memory objects
```

---

# Core Problem

Humans naturally compress information.

Examples:

```text
"שי סמבה"
"יוסי 4200"
"מיקו שישי"
"ביטוח רכב שבוע הבא"
```

Humans understand these fragments because they already contain hidden context.

But a useful AI memory system must answer:

```text
Will future-you understand this later?
```

That is the real task.

Not extraction.

Not classification.

Cognitive completeness.

---

# Product Behavior

ForgetIt currently learns one behavior:

```text
message (+ optional existing memory)
    -> MemoryExtraction
```

The system must determine:

* Is the memory complete?
* Is it actionable or reference memory?
* What fields are missing?
* Can the new message complete an older partial memory?

---

# Examples

## Incomplete Memory

Input:

```text
שי סמבה
```

Expected understanding:

```text
Incomplete.
Missing:
- time
- context
```

Because future-you will not understand:

* when?
* why?
* what about Shay Samba?

---

## Completing Existing Memory

Existing memory:

```text
שי סמבה
```

New message:

```text
מחר בבוקר יועץ נדלן
```

Expected result:

```text
Complete actionable memory:

anchor: שי סמבה
time: מחר בבוקר
context: יועץ נדלן
```

---

## Complete Memory

Input:

```text
ביטוח רכב שבוע הבא
```

Expected:

```text
Complete.
```

Because future-you already understands the meaning.

No additional clarification is required.

---

## Reference Memory

Input:

```text
מאמר טוב על dspy https://example.com/dspy
```

Expected:

```text
Reference memory.
```

No future time is required.

Only enough context to retrieve the information later.

---

# Core Insight

ForgetIt discovered something important very early:

```text
Extraction is easy.
Cognitive completeness is hard.
```

Most NLP systems stop at:

* entities
* dates
* labels
* intents
* classification

ForgetIt explores something deeper:

```text
Can the system determine whether future-you
will understand the memory later?
```

That is a much harder cognitive task.

---

# Dataset-First Development

ForgetIt is intentionally built backwards compared to most AI projects.

Typical AI workflow:

```text
prompt
    -> agent
        -> hope
```

ForgetIt workflow:

```text
dataset
    -> metrics
        -> evaluation
            -> optimization
```

The dataset comes first.

The behavioral space is manually defined before optimization begins.

Only after the task becomes measurable does DSPy enter the loop.

---

# Dataset

The dataset consists of JSONL rows.

One row per memory interaction.

Current splits:

```text
train
val
test
```

Current dataset categories:

* actionable complete
* actionable incomplete
* actionable memory completion
* reference complete
* reference incomplete
* link-based memory
* ambiguous/tricky cases

Example row:

```json
{
  "message": "שי סמבה",
  "expected": {
    "status": "incomplete",
    "missing_fields": ["time", "context"]
  }
}
```

Completion example:

```json
{
  "message": "מחר בבוקר יועץ נדלן",
  "existing_memory": {
    "anchor": "שי סמבה"
  },
  "expected": {
    "status": "complete",
    "memory": {
      "mode": "actionable",
      "anchor": "שי סמבה",
      "time": "מחר בבוקר",
      "context": "יועץ נדלן"
    }
  }
}
```

---

# Memory Model

Current Pydantic schema:

```python
class MemoryItem(BaseModel):
    mode: Literal["actionable", "reference"]
    anchor: str
    time: str | None
    context: str | None
    link: str | None
```

And:

```python
class MemoryExtraction(BaseModel):
    status: Literal["complete", "incomplete"]
    memory: MemoryItem | None
    missing_fields: list[str]
```

This structure intentionally stays minimal.

The goal is not complex architecture.

The goal is measurable cognition.

---

# Metrics

ForgetIt uses product-oriented metrics instead of generic NLP scoring.

Current metrics:

## Status Metrics

```text
status_match
false_complete_rate
false_incomplete_rate
```

These measure whether the model correctly determines:

```text
safe to forget
vs
not safe to forget
```

---

## Missing Field Metrics

```text
missing_fields_f1
```

Measures whether the model correctly identifies:

* missing time
* missing context

---

## Memory Field Metrics

```text
mode_match
anchor_match
time_match
context_token_f1
link_match
```

These measure the quality of extracted memory structure.

---

## Product Score

ForgetIt uses a weighted product-oriented score.

The score prioritizes:

* avoiding dangerous false-complete memories
* reducing overly cautious false-incomplete behavior
* improving future-self usability

This is intentionally different from simple extraction accuracy.

---

# DSPy Optimization

ForgetIt uses DSPy only after:

* dataset creation
* metric definition
* evaluation design

Current optimizer:

```text
DSPy MIPROv2
```

Optimization objective:

```text
Improve cognitive completeness behavior.
```

Not:

```text
maximize extraction overlap
```

---

# Current Results

Baseline validation score:

```text
0.406
```

After DSPy optimization:

```text
0.796
```

The optimization significantly improved:

* memory completion behavior
* merging follow-up messages
* determining usable completeness

Example:

Before optimization:

```text
"מחר בערב מסמכים לבנק"
-> incomplete
```

After optimization:

```text
-> complete actionable memory
```

This demonstrates behavioral optimization over a cognitive dataset.

Full experiment details: [reports/optimize_report.md](reports/optimize_report.md)

---

# Why This Project Is Different

ForgetIt is not:

* another chatbot
* another RAG demo
* another LangChain wrapper
* another agent orchestration project

The interesting part is:

```text
behavioral optimization over cognitive completeness
```

The system is not merely extracting information.

It is learning:

```text
What information humans actually need
in order to safely forget something.
```

---

# Project Structure

```text
forgetit/
│
├── app/
│   ├── memory/
│   │   ├── models.py
│   │   ├── program.py
│   │   ├── metrics.py
│   │   └── optimize.py
│   │
│   ├── eval.py
│   └── optimize.py
│
├── data/
│   ├── save_memory_train.jsonl
│   ├── save_memory_val.jsonl
│   └── save_memory_test.jsonl
│
├── artifacts/
│   └── compiled_memory_program.json
│
├── reports/
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# Design Philosophy

ForgetIt intentionally stays small.

The goal is not architectural complexity.

The goal is disciplined AI engineering:

1. Define behavior manually
2. Build a dataset
3. Define metrics
4. Build a baseline
5. Evaluate failures
6. Improve metrics
7. Optimize behavior
8. Re-evaluate

The project treats datasets as behavioral spaces.

Not merely training data.

---

# Current Scope

ForgetIt v0 intentionally does NOT yet include:

* vector search
* memory retrieval
* WhatsApp integration
* calendar integration
* autonomous agents
* tool calling
* long-term personalization
* production infrastructure

Those systems may come later.

But only after the cognitive layer becomes measurable and reliable.

---

# Roadmap

## v0.1

* stronger datasets
* more ambiguity cases
* improved context evaluation
* better split balancing

## v0.2

* memory storage
* retrieval evaluation
* reference memory search

## v0.3

* user-specific shorthand learning
* recurring anchor adaptation
* personalized memory compression

## v0.4

* WhatsApp interface
* real-world memory ingestion
* measurable production feedback loops

---

# Status

Early.

But already meaningful.

ForgetIt is becoming a measurable cognitive systems lab focused on one question:

**When is memory safe to forget?**
