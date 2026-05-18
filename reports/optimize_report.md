# ForgetIt Optimization Report

## Run Summary

This run compares the raw `MemoryRouter` baseline against a DSPy `BootstrapFewShot` optimized version on the validation split.

The validation set contains 20 examples:

- 10 `save` examples
- 10 `retrieve` examples

The optimizer used 40 training rows and saved the compiled program to:

```text
artifacts/memory_router_bootstrap.json
```

## Headline Result

The optimization clearly improved the router.

| Metric | Baseline | Optimized | Change |
|---|---:|---:|---:|
| Action Accuracy | 0.7000 | 0.9000 | +0.2000 |
| Macro Precision | 0.8125 | 0.9167 | +0.1042 |
| Macro Recall | 0.7000 | 0.9000 | +0.2000 |
| Macro F1 | 0.6703 | 0.8990 | +0.2287 |
| Save Recall | 0.4000 | 0.8000 | +0.4000 |
| Retrieve Precision | 0.6250 | 0.8333 | +0.2083 |
| Item Exact Accuracy | 0.1000 | 0.0500 | -0.0500 |
| Avg Token F1 | 0.5015 | 0.5090 | +0.0075 |
| Semantic Accuracy | 0.3500 | 0.4000 | +0.0500 |

## Interpretation

The optimization worked where it matters most right now: action routing.

The baseline had a strong bias toward `retrieve`. It predicted every retrieve example correctly, but incorrectly classified 6 of 10 save examples as retrieve.

Baseline per-action behavior:

| Action | Precision | Recall | F1 |
|---|---:|---:|---:|
| retrieve | 0.6250 | 1.0000 | 0.7692 |
| save | 1.0000 | 0.4000 | 0.5714 |

After optimization, that bias was reduced significantly.

Optimized per-action behavior:

| Action | Precision | Recall | F1 |
|---|---:|---:|---:|
| retrieve | 0.8333 | 1.0000 | 0.9091 |
| save | 1.0000 | 0.8000 | 0.8889 |

This is a real improvement. The model learned that many short human self-notes are saves, even when they contain action-like language.

## What Improved

The biggest win is save recall.

Baseline:

```text
save recall = 0.4000
```

Optimized:

```text
save recall = 0.8000
```

That matters because ForgetIt is first a memory capture system. If the user sends something to remember and the router misclassifies it as retrieval, the product fails at the first step.

The optimized model fixed several examples that the baseline got wrong:

| ID | Message | Baseline | Optimized |
|---|---|---|---|
| save_022 | לבדוק אברול של קונטי | retrieve | save |
| save_023 | הכתובת היא הדס 20 בנימינה | retrieve | save |
| save_024 | לדבר עם העוד על החוזה ביום ראשון | retrieve | save |
| save_026 | עירית צריכה מיילים על הקרנות | retrieve | save |
| save_027 | לראות אחר כך את הסרטון הזה https://youtube.com/watch?v=123 | retrieve | save |

This confirms the dataset is useful: it exposed a product-specific ambiguity, and bootstrapping improved it.

## What Did Not Improve Enough

The item field is still weak.

Optimized item metrics:

```text
Exact Accuracy:     0.0500
Average Token F1:   0.5090
Semantic Accuracy:  0.4000
```

The item result improved semantically only slightly:

```text
semantic accuracy: 0.3500 -> 0.4000
```

This means the optimizer mainly improved the action decision, not the item normalization.

There are still several item problems:

### 1. Missing important details

Example:

```text
expected:  לראות סרטון יוטיוב https://youtube.com/watch?v=123
predicted: לראות אחר כך את הסרטון הזה
```

The optimized model correctly chose `save`, but dropped the URL. That is a serious item failure.

### 2. Returning the question instead of the memory object

Example:

```text
message:   כמה המשכנתא?
expected:  משכנתא 8500000
predicted: כמה המשכנתא?
```

The action is correct, but the item is not the remembered object.

### 3. Partial retrieval target

Example:

```text
expected: האוטו בגומא מחר בבוקר
predicted: האוטו בגומא
```

This is close, but missing the time.

### 4. Save/retrieve still confused in some cases

The optimized model still misclassified two save examples:

```text
save_029: האוטו בגומא מחר בבוקר -> retrieve
save_030: ליוסי יש 300000 בקרנות -> retrieve
```

This shows the router is better, but not stable yet.

## Important Observation

The optimization objective was binary:

```text
score = 1 only if action is correct and item semantically matches
```

But the actual result suggests the bootstrapped demos helped the action decision more than the item construction.

That is not a problem. It means the current program may be doing two jobs inside one signature:

1. classify action
2. produce item

The action task is learning faster than the item task.

## Judgment

This is a good first optimization result.

Not because the final score is high, but because the loop is now real:

```text
dataset -> baseline -> metrics -> optimization -> before/after comparison
```

The system moved from:

```text
unstable router with retrieve bias
```

to:

```text
much better router, still weak item extraction/normalization
```

That is exactly what should happen in a serious eval-driven workflow.

## Recommended Next Step

Do not jump to a larger optimizer yet.

First, split the metrics conceptually:

```text
router quality = action metrics
item quality = item semantic metric
```

Then decide whether to keep one DSPy signature or split into two modules.

### Option A: Keep one module

```text
message -> action + item
```

Pros:

- simple
- one optimizer
- easy to explain

Cons:

- item quality may stay noisy
- retrieval examples often require knowing what stored memory should match

### Option B: Split into two modules

```text
MemoryActionRouter:
message -> action

MemoryItemWriter:
message + action -> item
```

Pros:

- easier to optimize separately
- cleaner metrics
- action and item failures are isolated
- better portfolio story

Cons:

- slightly more code
- two datasets or two evaluation heads

## Recommendation

Stay with one module for one more run, but strengthen the item instruction.

The next benchmark target should be:

```text
Action Accuracy >= 0.90
Save Recall >= 0.90
Item Semantic Accuracy >= 0.60
```

Current optimized result:

```text
Action Accuracy = 0.9000
Save Recall = 0.8000
Item Semantic Accuracy = 0.4000
```

So the next bottleneck is clearly:

```text
item quality
```

## Next Technical Move

Add item-specific rules to the signature:

```text
For save:
- keep URLs exactly
- keep amounts exactly
- keep dates/times if present
- remove only filler words when safe

For retrieve:
- do not return the question
- return the remembered object being searched for
- preserve essential constraints: person, amount, time, location, link
```

Then rerun the same optimization.

Only after that, consider `MIPROv2`.

## Conclusion

Step 1 succeeded: dataset.

Step 2 succeeded: metrics.

Step 3 succeeded partially: optimization improved action routing strongly.

The project is now at the first real engineering fork:

```text
Do we optimize the single action+item program further,
or split routing and item writing into separate measured modules?
```

My call: one more single-module optimization after improving item instructions. If item semantic accuracy remains low, split the module.
