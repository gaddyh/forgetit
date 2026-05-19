# ForgetIt Optimization Report - Baseline

**Run ID:** `20260519_184327`

**Dataset:** `data/save_memory_val.jsonl`

**Rows:** 10

## Row-Level Metrics

| Row | Message | Expected | Predicted | Score | Status | False Complete | False Incomplete | Missing F1 | Context F1 | Product |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | רועי משכנתא | incomplete | incomplete | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 |  | 1.000 |
| 2 | מחר בערב מסמכים לבנק | complete | incomplete | 0.163 | 0.000 | 0.000 | 1.000 |  | 0.000 | 0.325 |
| 3 | יובל רביעי | incomplete | incomplete | 0.867 | 1.000 | 0.000 | 0.000 | 0.667 |  | 0.867 |
| 4 | פגישה על האתר החדש | complete | incomplete | 0.163 | 0.000 | 0.000 | 1.000 |  | 0.000 | 0.325 |
| 5 | דרכון אוגוסט | complete | incomplete | 0.000 | 0.000 | 0.000 | 1.000 |  |  | 0.000 |
| 6 | רכב טסט | incomplete | incomplete | 0.867 | 1.000 | 0.000 | 0.000 | 0.667 |  | 0.867 |
| 7 | עוד שבועיים | complete | incomplete | 0.000 | 0.000 | 0.000 | 1.000 |  |  | 0.000 |
| 8 | הילה | incomplete | incomplete | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 |  | 1.000 |
| 9 | ראשון בצהריים לדבר על הגן | complete | incomplete | 0.000 | 0.000 | 0.000 | 1.000 |  |  | 0.000 |
| 10 | אינסטלטור מחר דחוף | complete | incomplete | 0.000 | 0.000 | 0.000 | 1.000 |  |  | 0.000 |

## Summary Metrics

| Metric | Value |
| --- | --- |
| status_match | 0.400 |
| false_complete_rate | 0.000 |
| false_incomplete_rate | 0.600 |
| missing_fields_f1 | 0.833 |
| mode_match | 1.000 |
| anchor_match | 1.000 |
| time_match | 1.000 |
| context_exact_match | 0.000 |
| context_token_f1 | 0.000 |
| link_match | 1.000 |
| memory_field_score | 0.650 |
| product_score | 0.438 |

## Artifacts

- `rows.json`
- `summary.json`
- `row_metrics.csv`
- `summary.csv`
- `report.md`


## Notes

- Baseline pre-optimization evaluation.
