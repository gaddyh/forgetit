# ForgetIt

ForgetIt is an experiment in dataset-first AI engineering.

The project started from a simple realization:

Before building agents, memory systems, or orchestration,
first define the behavior space manually.

Instead of starting with:

prompts
chains
agents
RAG
orchestration frameworks

the project starts with:

manual cognition

Meaning:

A human first performs the task manually and builds a dataset of expected behavior.

Only then:

metrics are defined
evaluation becomes possible
extraction quality becomes measurable
DSPy is introduced later as an optimization layer

---

## The Core Shift

The important shift in this project is:

```
dataset
    ->
metrics
        ->
evaluation
            ->
DSPy
```

NOT:

```
DSPy
    ->
prompting
        ->
hope
```

The dataset defines the behavioral space.

The metrics define what "good" means.

Only then does optimization make sense.

---

## Problem

Humans naturally create compressed memory fragments:

"מיילים יוסי קרנות"
"תשלום 4200 עד סוף חודש"
"מיקו מתנה שישי"

These fragments contain implicit structure.

ForgetIt explores whether a system can extract structured perception from these compressed notes.

---

## Current Task

Current task:

```
message
    ->
structured entities
```

Current schema:

people
subjects
locations
times
amounts
links

Example:

```json
{
  "message": "גבעתיים רואה חשבון 2500",
  "output": {
    "people": [],
    "subjects": ["רואה חשבון"],
    "locations": ["גבעתיים"],
    "times": [],
    "amounts": ["2500"],
    "links": []
  }
}
```

---

## Dataset-First Development

The dataset was created manually before any optimization.

This forced:

ontology decisions
ambiguity analysis
decomposition decisions
behavioral consistency

The dataset is intentionally small and curated.

Goal:

understand the space before scaling

Current dataset includes:

people
shorthand fragments
locations
links
quantities
temporal phrases
compressed reminders
ambiguous notes

---

## Evaluation

Once the dataset existed, metrics became natural.

The project evaluates extraction quality using:

### Exact Metrics

Per field:

Precision
Recall
F1

Global:

Micro F1
Macro F1

These metrics expose:

missing entities
hallucinations
decomposition failures
schema errors
weak extraction coverage

### Semantic Metrics

DSPy SemanticF1 is added as a secondary layer.

Purpose:

tolerate semantic similarity
compare approximate meaning
handle fuzzy language

But exact evaluation remains primary.

Reason:

structural correctness matters before semantic flexibility

---

## Why DSPy Was Added Later

DSPy is not the starting point.

DSPy becomes useful only after:

the dataset exists
metrics exist
behavior is measurable

At that point DSPy becomes:

an optimization system

rather than:

a prompting framework

This changes the role of LLM engineering completely.

---

## Current Findings

Current evaluation already reveals meaningful failure modes:

### Subject under-extraction

The system is highly conservative:

high precision
lower recall

Especially for:

subjects

which currently acts as the most ambiguous field.

### Entity decomposition issues

Example:

"מייל חוזה"

Should become:

["מייל", "חוזה"]

not:

["מייל חוזה"]

### Quantity normalization pressure

Example:

"12 ממר"
-> "12"

Semantic information is lost.

### Temporal normalization ambiguity

Example:

"עד סוף חודש"
vs
"סוף חודש"

---

## Current Architecture

```
manual dataset
    ->
ontology
        ->
metrics
            ->
evaluation
                ->
DSPy extraction
```

Not:

```
agent
    ->
tools
        ->
memory
            ->
magic
```

---

## Project Structure

```
forgetit/
│
├── data/
│   └── perception_v0.jsonl
│
├── app/
│   └── perception/
│       ├── extractor.py
│       ├── metrics.py
│       ├── eval_exact.py
│       └── eval.py
│
├── reports/
│   └── baseline_eval.md
│
├── README.md
└── requirements.txt
```

---

## Current Focus

Current work focuses ONLY on:

### Perceive

Meaning:

```
raw text
    ->
structured perception
```

Not:

planning
acting
memory orchestration
agents
retrieval systems

Those may come later.

But only after perception becomes measurable and improvable.
