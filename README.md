# ForgetIt

ForgetIt is a dataset-first AI engineering experiment.

The project explores a simple but deep question:

> Can an AI system learn how to turn short, messy human memory fragments into clean memory operations?

Instead of starting with agents, vector databases, retrieval pipelines, or orchestration frameworks, ForgetIt starts from manual cognition:

```text
human examples
    -> dataset
        -> metrics
            -> evaluation
                -> DSPy optimization
```

The core idea is that before building an AI system, a human should first define the behavior space manually.

Only after that does it make sense to introduce prompts, models, metrics, and optimization.

## What ForgetIt Does

ForgetIt currently learns one small behavior:

```text
message
    -> action + memory item
```

The action is one of:

- save
- retrieve

The item is the clean memory object.

Example:

```json
{
  "input": {
    "message": "לא לשכוח לקנות מגבון לניקוי התופים"
  },
  "output": {
    "action": "save",
    "item": "לקנות מגבון לניקוי התופים"
  }
}
```

And:

```json
{
  "input": {
    "message": "מה הייתי צריך לקנות לתופים?"
  },
  "output": {
    "action": "retrieve",
    "item": "לקנות מגבון לניקוי התופים"
  }
}
```

The first message saves a memory.

The second message asks to retrieve that same memory.

## Why This Project Exists

Most AI assistant projects begin with implementation:

- chatbot UI
- LangChain chains
- agents
- tools
- memory
- RAG
- vector search

ForgetIt starts one level earlier.

It asks:

> What behavior do I actually want the system to learn?

The answer is encoded in the dataset.

The dataset is not just training data.

It is the product definition.

## The Core Shift

ForgetIt is built around this workflow:

```text
manual dataset
    -> behavioral space
        -> metrics
            -> evaluation
                -> optimization
```

Not this:

```text
prompt
    -> agent
        -> hope
```

The manual dataset comes first.

Metrics come second.

DSPy comes later.

That is the important shift.

## Dataset

The dataset lives in:

`data/forgetit_v0.jsonl`

Each row has:

```json
{
  "id": "save_001",
  "input": {
    "split": "train",
    "message": "..."
  },
  "output": {
    "action": "save",
    "item": "..."
  }
}
```

Current splits:

- train
- val
- test

The dataset contains two mirrored behavior families:

- Save examples
- Retrieve examples

Example save row:

```json
{
  "id": "save_012",
  "input": {
    "split": "train",
    "message": "הארנונה יצאה 2500"
  },
  "output": {
    "action": "save",
    "item": "ארנונה 2500"
  }
}
```

Example retrieve row:

```json
{
  "id": "retrieve_012",
  "input": {
    "split": "train",
    "message": "כמה יצאה הארנונה?"
  },
  "output": {
    "action": "retrieve",
    "item": "ארנונה 2500"
  }
}
```

This creates a small but meaningful memory behavior space.

The model must learn both:

- Should this message save something?
- What memory object does this message refer to?

## Current Model

The current DSPy program is a simple memory router.

```text
message
    -> action
    -> item
```

The output schema is intentionally small:

```text
action: "save" | "retrieve"
item: str
```

The point is not to build a full assistant yet.

The point is to make one cognitive layer measurable.

## Metrics

ForgetIt evaluates two different things.

### 1. Action Quality

Did the model choose the correct action?

`save` vs `retrieve`

Metrics:

- action accuracy
- per-action precision
- per-action recall
- per-action F1
- macro precision
- macro recall
- macro F1

This measures whether the system understands the user's operation.

### 2. Item Quality

Did the model produce the right memory item?

Metrics:

- exact item accuracy
- average token F1
- semantic item accuracy

Exact match is strict.

Token F1 is softer.

Semantic accuracy uses a judge to decide whether the predicted item refers to the same memory object as the expected item.

This distinction matters because memory items may be phrased differently while still referring to the same thing.

Example:

```
expected:  מתנה לשי
predicted: המתנה לשי
```

Exact match may fail.

Semantic match may pass.

But if important information is missing, semantic match should fail.

Example:

```
expected:  יוסי 300000 בקרנות
predicted: יוסי בקרנות
```

This should not pass, because the amount is essential.

## Evaluation

Run evaluation:

```bash
python app/eval.py --split val
```

Evaluate another split:

```bash
python app/eval.py --split test
```

Evaluate all rows:

```bash
python app/eval.py --split all
```

Default dataset:

`data/forgetit_v0.jsonl`

The evaluation prints:

- each message
- expected output
- predicted output
- action metrics
- item metrics

It also saves a markdown report under:

`reports/`

## Optimization

ForgetIt uses DSPy only after the dataset and metrics exist.

Run optimization:

```bash
python app/optimize.py
```

Default behavior:

```text
train split -> optimize
val split   -> evaluate before/after
```

The optimizer currently uses DSPy BootstrapFewShot.

The compiled program is saved to:

`artifacts/memory_router_bootstrap.json`

This makes the project an optimization loop, not just a prompt experiment.

## Project Structure

```
forgetit/
│
├── app/
│   ├── program.py       # DSPy memory router: message -> action + item
│   ├── eval.py          # evaluation runner
│   ├── optimize.py      # DSPy optimization loop
│   ├── metrics.py       # action + item metrics
│   ├── item_judge.py    # semantic item judge
│   ├── opt_metric.py    # scalar metric for DSPy optimization
│   └── report.py        # markdown report generation
│
├── data/
│   └── forgetit_v0.jsonl
│
├── artifacts/
│   └── memory_router_bootstrap.json
│
├── reports/
│   └── generated evaluation reports
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Design Philosophy

ForgetIt is intentionally small.

The goal is not to impress with architecture.

The goal is to show a disciplined AI engineering loop:

1. Manually define behavior
2. Create dataset
3. Define measurable outputs
4. Build baseline
5. Evaluate
6. Analyze failure modes
7. Optimize with DSPy
8. Re-evaluate

This is the opposite of building a large agent first and only later asking whether it works.

## Current Scope

ForgetIt v0 does not yet implement:

- real memory storage
- vector search
- calendar integration
- WhatsApp integration
- multi-step planning
- long-term personalization
- agentic tool use

That is intentional.

The current scope is narrower:

> Can the system understand whether a message is saving memory or retrieving memory,
> and can it produce the correct canonical memory item?

Only after this layer is measurable should the system grow.

## Why This Matters

A memory assistant is not primarily a chat problem.

It is a behavioral modeling problem.

Users write compressed fragments like:

- "מיקו מתנה שישי"
- "תשלום 4200 עד סוף חודש"
- "יוסי קרנות"

A useful system must learn how to turn those fragments into durable, retrievable memory objects.

ForgetIt starts by making that behavior explicit.

## Roadmap

Possible next steps:

### v0.1 — Stronger Evaluation

- add more edge cases
- improve split balance
- add confusion analysis
- compare baseline vs optimized reports

### v0.2 — Memory Store

- save canonical memory items
- retrieve matching items
- evaluate retrieval quality

### v0.3 — Context-Aware Retrieval

- retrieve from a set of saved memories
- distinguish similar memory objects
- measure retrieval precision and recall

### v0.4 — Personal Shorthand Learning

- learn user-specific phrasing
- handle recurring people, places, and topics
- adapt canonicalization over time

### v0.5 — WhatsApp Interface

- send notes to the system
- ask natural questions later
- keep the entire loop measurable

## Status

Early but meaningful.

ForgetIt is not a production assistant yet.

It is a clean AI engineering lab for building one measurable cognitive layer at a time.