# ForgetIt Optimization Report

## Experiment

Initial DSPy optimization experiment for cognitive memory completeness.

Date:

```text
2026-05-19
```

Optimizer:

```text
DSPy MIPROv2
```

Model:

```text
gpt-4o-mini
```

Validation set size:

```text
10 rows
```

Optimization goal:

```text
Improve cognitive memory completeness behavior.
```

The optimization metric was intentionally product-oriented.

The system was rewarded for:

* correctly identifying complete memories
* correctly identifying incomplete memories
* merging follow-up memory messages
* avoiding dangerous false-complete memories

The system was penalized for:

* marking incomplete memory as complete
* excessive false-incomplete behavior
* weak context completion

---

# Baseline Validation Results

Initial baseline validation average:

```text
0.406
```

Per-row baseline scores:

| Row | Message                   | Score |
| --- | ------------------------- | ----- |
| 1   | רועי משכנתא               | 1.000 |
| 2   | מחר בערב מסמכים לבנק      | 0.163 |
| 3   | יובל רביעי                | 0.867 |
| 4   | פגישה על האתר החדש        | 0.163 |
| 5   | דרכון אוגוסט              | 0.000 |
| 6   | רכב טסט                   | 0.867 |
| 7   | עוד שבועיים               | 0.000 |
| 8   | הילה                      | 1.000 |
| 9   | ראשון בצהריים לדבר על הגן | 0.000 |
| 10  | אינסטלטור מחר דחוף        | 0.000 |

Observed baseline behavior:

```text
The model was extremely conservative.
```

Main failure mode:

```text
false incomplete
```

The model frequently refused to mark memories as complete even when enough information existed.

Example:

```text
"מחר בערב מסמכים לבנק"
```

Expected:

```text
complete actionable memory
```

Baseline prediction:

```text
incomplete
missing context
```

The system correctly extracted:

* anchor
* time
* memory mode

But still refused to finalize the memory.

This revealed that the core challenge was not extraction quality.

The challenge was:

```text
determining cognitive completeness
```

---

# Optimization Process

DSPy MIPROv2 optimization settings:

```text
num_trials: 10
fewshot candidates: 6
instruction candidates: 3
```

The optimizer explored combinations of:

* instructions
* bootstrapped few-shot examples

The optimization metric was based on:

* product_score
* false_complete penalties
* false_incomplete penalties
* weighted memory field scoring

---

# Optimization Trials

| Trial    | Score |
| -------- | ----- |
| Baseline | 40.58 |
| Trial 2  | 58.93 |
| Trial 3  | 44.46 |
| Trial 4  | 72.22 |
| Trial 5  | 52.96 |
| Trial 6  | 79.61 |
| Trial 7  | 44.46 |
| Trial 8  | 56.33 |
| Trial 9  | 43.04 |
| Trial 10 | 56.33 |
| Trial 11 | 79.61 |

Best optimization score:

```text
79.61
```

Best configuration:

```text
Instruction 0
Few-Shot Set 5
```

---

# Compiled Validation Results

Compiled validation average:

```text
0.796
```

Per-row compiled scores:

| Row | Message                   | Score |
| --- | ------------------------- | ----- |
| 1   | רועי משכנתא               | 1.000 |
| 2   | מחר בערב מסמכים לבנק      | 0.803 |
| 3   | יובל רביעי                | 0.867 |
| 4   | פגישה על האתר החדש        | 0.775 |
| 5   | דרכון אוגוסט              | 0.000 |
| 6   | רכב טסט                   | 0.867 |
| 7   | עוד שבועיים               | 0.825 |
| 8   | הילה                      | 1.000 |
| 9   | ראשון בצהריים לדבר על הגן | 1.000 |
| 10  | אינסטלטור מחר דחוף        | 0.825 |

---

# Improvement Analysis

The optimization produced a major behavioral improvement:

```text
0.406 -> 0.796
```

Largest improvements occurred on:

* follow-up completion rows
* memory merge behavior
* determining actionable completeness

Examples:

## Example 1

Message:

```text
מחר בערב מסמכים לבנק
```

Baseline:

```text
0.163
```

Compiled:

```text
0.803
```

The optimized system became significantly more willing to complete existing memories.

---

## Example 2

Message:

```text
ראשון בצהריים לדבר על הגן
```

Baseline:

```text
0.000
```

Compiled:

```text
1.000
```

This demonstrated successful memory completion merging.

---

## Example 3

Message:

```text
אינסטלטור מחר דחוף
```

Baseline:

```text
0.000
```

Compiled:

```text
0.825
```

The optimizer learned that:

```text
"דחוף"
```

already implies meaningful future context.

---

# Remaining Failure Cases

The following case still failed completely:

```text
דרכון אוגוסט
```

Compiled score:

```text
0.000
```

This revealed an important ambiguity.

Possible interpretations:

* renew passport
* check expiration
* pickup passport
* prepare for travel

This suggests:

```text
dataset ambiguity still exists
```

This is useful.

The evaluation system successfully exposed unstable cognitive labels.

---

# Key Insight

The most important result was not the numerical score.

The most important discovery was:

```text
The optimization target shapes the cognitive behavior.
```

Changing the optimization metric changed:

* memory completion behavior
* willingness to finalize memories
* handling of future-self usability

The system was not merely optimizing extraction.

It was optimizing:

```text
cognitive completeness
```

---

# Conclusion

ForgetIt successfully demonstrated:

* dataset-first AI engineering
* product-oriented evaluation
* measurable cognitive behavior
* DSPy behavioral optimization
* memory completeness reasoning

The project evolved from a simple extraction task into:

```text
behavioral optimization over future-self memory usability
```

This establishes a strong foundation for future work in:

* memory retrieval
* shorthand personalization
* cognitive compression
* long-term memory systems
* reflective assistants
