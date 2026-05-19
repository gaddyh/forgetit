# ForgetIt — Mindset Shift

ForgetIt started as a simple extraction project.

It became a realization about AI engineering.

---

# Initial Assumption

The naive approach was:

```text
prompt
    ->
LLM
    ->
hope
```

Meaning:

- write a clever prompt
- manually tweak behavior
- patch edge cases in code
- hope the system improves

This quickly collapsed.

---

# The Shift

The core realization became:

```text
dataset
    ->
metrics
        ->
evaluation
            ->
optimization
                ->
behavior shift
```

The dataset defines the cognitive space.

The metrics define what "good" means.

Only then does optimization become meaningful.

---

# The Product

ForgetIt is based on a simple idea:

> Everything you send should become safe to forget.

**Example:**

**User:**
```
"שי שמבה"
```

**Bot:**
```
"When? Short context?"
```

**User:**
```
"חמישי יועץ נדלן"
```

**Result:**

```json
{
  "anchor": "שי שמבה",
  "time": "חמישי",
  "context": "יועץ נדלן"
}
```

The system learns conversational memory completion.

---

# First Dataset

The first dataset focused on:

- incomplete actionable memories
- follow-up completion
- explicit time
- explicit context
- reference links

**Examples:**

```
"דני ביטוח"
+
"חמישי לחדש ביטוח"
```

```
"https://react.dev useEffect"
```

---

# First Major Discovery

The system initially failed badly on follow-up cognition.

**Example:**

```
"מיקו מתי מגיע"
+
"מחר נזילה"
```

The model treated the second message as a NEW memory.

This revealed a deeper truth:

> The unit of cognition is not a message.
> It is a state transition.

Meaning:

```text
previous_memory
    +
new_message
        ->
updated_memory
```

This changed the entire dataset design.

---

# The Collapse

The next dataset mixed multiple cognition spaces together:

- explicit completion
- semantic shorthand
- fuzzy anchors
- compressed memories

**Examples:**

```
"מיקו נזילה מחר"
"ביטוח רכב"
"דרכון אוגוסט"
```

Optimization became unstable.

Rows that were previously perfect collapsed.

The ontology itself became inconsistent.

This revealed another major realization:

> `"memory extraction"`
> is not one task
>
> It is multiple cognition spaces.

---

# The Decomposition

The project was decomposed into separate spaces:

**Space 1 — Explicit Actionable Completion**

Stable.

Requires:

- explicit time
- explicit context

**Space 2 — Semantic Shorthand**

Hard.

Questions like:

- When is shorthand sufficient?

**Space 3 — Reference Memory**

Links, articles, searchable knowledge.

**Space 4 — Anchor Semantics**

Understanding:

- what is anchor?
- what is context?

---

# The Stable Dataset

After rolling back to a coherent cognition space:

```text
explicit actionable completion
+
clean reference memories
```

optimization suddenly converged.

---

# Real Numbers

**Baseline validation score:**

```
59.4%
```

**Compiled DSPy score:**

```
88.4%
```

Without changing architecture.

Only:

- dataset quality
- ontology clarity
- metrics
- optimization

---

# Important Metrics

Final compiled metrics:

```
status_match:          0.923
false_complete_rate:  0.000
missing_fields_f1:    0.944
mode_match:           1.000
time_match:           1.000
product_score:        0.898
```

**Key product insight:**

```
false_complete_rate = 0
```

Meaning:

The system almost never says:

> "safe to forget"

when information is actually missing.

---

# Most Important Insight

The biggest realization was:

> **good dataset is gold**

Not because "data is important".

Because:

> the dataset defines the cognitive boundaries

The project stopped being:

- prompt engineering

and became:

- measurable cognition design

---

# Final Mental Model

```text
dataset
    ->
behavior space
        ->
metrics
            ->
optimization
                ->
behavioral convergence
```

This is the core mindset behind ForgetIt.
