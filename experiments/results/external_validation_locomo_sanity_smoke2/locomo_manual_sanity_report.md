# SRP LoCoMo Manual Sanity Harness

This report freezes the LoCoMo adapter-calibration evidence package for SRP.
It is a calibration artifact, not a paper result, not a benchmark claim, and not a runtime policy.

## 1. Frozen Scope

- Benchmark: `locomo`
- Baselines: `full_context, vector_rag, srp`
- Seed: `11`
- Case limit: `2`
- Data root: `data/locomo`

## 2. Adapter Validation Summary

- Cases checked: `2`
- Cases passed: `2`
- Cases failed: `0`
- `focus_relations_resolve` pass count: `2`
- `focus_units_resolve` pass count: `2`
- `sample_id_consistent` pass count: `2`
- `session_datetime_present_on_dialog_turns` pass count: `2`
- `source_relations_present` pass count: `2`
- `source_units_present` pass count: `2`
- `target_relations_resolve` pass count: `2`
- `target_relations_subset_source` pass count: `2`
- `target_units_present` pass count: `2`
- `target_units_subset_source` pass count: `2`
- `timestamps_non_decreasing` pass count: `2`

## 3. Summary

- Record count: `6`
- semantic_coverage: `0.527778`
- semantic_drift: `0.502445`
- fact_accuracy: `0.555555`
- relation_accuracy: `0.5`
- recovery_accuracy: `0.589947`
- closure_accuracy: `0.5`
- neighborhood_completeness: `0.666667`
- hallucinated_relation_rate: `0.623333`
- evidence_cost: `349.776667`
- answer_accuracy: `0.714286`
- official_metric_score: `0.714286`

## 4. Selected Cases

### conv-26:qa:0

- Question: When did Caroline go to the LGBTQ support group?
- Gold answer: `7 May 2023`
- Official category: `2`
- Question labels: `temporal`
- Selection bucket: `temporal`
- Evidence ids: `conv-26:D1:3`
- Adapter passed: `True`

#### Adapter checks

| Check | Pass |
| --- | --- |
| `source_units_present` | `True` |
| `source_relations_present` | `True` |
| `target_units_present` | `True` |
| `target_relations_resolve` | `True` |
| `focus_units_resolve` | `True` |
| `focus_relations_resolve` | `True` |
| `target_units_subset_source` | `True` |
| `target_relations_subset_source` | `True` |
| `sample_id_consistent` | `True` |
| `session_datetime_present_on_dialog_turns` | `True` |
| `timestamps_non_decreasing` | `True` |

#### Source state preview

- Units: `647`
- Relations: `400`
- Unit `conv-26:D1:1` [dialog_turn] t=100 :: Hey Mel! Good to see you! How have you been?
- Unit `conv-26:session_1_observation:Caroline:0` [observation] t=100 :: Caroline attended an LGBTQ support group recently and found the transgender stories inspiring.
- Unit `conv-26:session_1_observation:Melanie:0` [observation] t=100 :: Melanie is currently managing kids and work and finds it overwhelming.
- Unit `conv-26:D1:2` [dialog_turn] t=101 :: Hey Caroline! Good to see you! I'm swamped with the kids & work. What's up with you? Anything new?
- Relation `conv-26:next:D1:1:D1:2` :: conv-26:D1:1 -> conv-26:D1:2 (next_turn)
- Relation `conv-26:next:D1:2:D1:3` :: conv-26:D1:2 -> conv-26:D1:3 (next_turn)
- Relation `conv-26:next:D1:3:D1:4` :: conv-26:D1:3 -> conv-26:D1:4 (next_turn)
- Relation `conv-26:next:D1:4:D1:5` :: conv-26:D1:4 -> conv-26:D1:5 (next_turn)

#### Gold target state preview

- Units: `3`
- Relations: `2`
- Target unit `conv-26:D1:2` [dialog_turn] t=101 :: Hey Caroline! Good to see you! I'm swamped with the kids & work. What's up with you? Anything new?
- Target unit `conv-26:D1:3` [dialog_turn] t=102 :: I went to a LGBTQ support group yesterday and it was so powerful.
- Target unit `conv-26:D1:4` [dialog_turn] t=103 :: Wow, that's cool, Caroline! What happened that was so awesome? Did you hear any inspiring stories?
- Target relation `conv-26:next:D1:2:D1:3` :: conv-26:D1:2 -> conv-26:D1:3 (next_turn)
- Target relation `conv-26:next:D1:3:D1:4` :: conv-26:D1:3 -> conv-26:D1:4 (next_turn)

#### Baseline responses

| Baseline | Predicted | Answer Acc. | Coverage | Drift | Relation Acc. | Recovery Acc. | Closure Acc. | Cost | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `full_context` | 7 May 2023 | 1.0 | 1.0 | 0.199 | 1.0 | 1.0 | 1.0 | 1047.0 | evidence_failure, cost_failure |
| `vector_rag` | 7 May 2023 | 1.0 | 0.166667 | 0.666667 | 0.0 | 0.444444 | 0.0 | 0.54 | representation_failure, relation_failure |
| `srp` | 7 May 2023 | 1.0 | 1.0 | 0.15 | 1.0 | 1.0 | 1.0 | 2.2 | evidence_failure |

#### Recovered state previews

- `full_context`
  - Units: `647`
  - Relations: `400`
  - Predicted answer: `7 May 2023`
  - Unit `conv-26:D1:1` [dialog_turn] t=100 :: Hey Mel! Good to see you! How have you been?
  - Unit `conv-26:session_1_observation:Caroline:0` [observation] t=100 :: Caroline attended an LGBTQ support group recently and found the transgender stories inspiring.
  - Unit `conv-26:session_1_observation:Melanie:0` [observation] t=100 :: Melanie is currently managing kids and work and finds it overwhelming.
  - Unit `conv-26:D1:2` [dialog_turn] t=101 :: Hey Caroline! Good to see you! I'm swamped with the kids & work. What's up with you? Anything new?
  - Relation `conv-26:next:D1:1:D1:2` :: conv-26:D1:1 -> conv-26:D1:2 (next_turn)
  - Relation `conv-26:next:D1:2:D1:3` :: conv-26:D1:2 -> conv-26:D1:3 (next_turn)
  - Relation `conv-26:next:D1:3:D1:4` :: conv-26:D1:3 -> conv-26:D1:4 (next_turn)
  - Relation `conv-26:next:D1:4:D1:5` :: conv-26:D1:4 -> conv-26:D1:5 (next_turn)
- `vector_rag`
  - Units: `3`
  - Relations: `0`
  - Predicted answer: `7 May 2023`
  - Unit `conv-26:session_1_observation:Caroline:1` [observation] t=101 :: The support group has made Caroline feel accepted and given her courage to embrace herself.
  - Unit `conv-26:D1:3` [dialog_turn] t=102 :: I went to a LGBTQ support group yesterday and it was so powerful.
  - Unit `conv-26:D1:7` [dialog_turn] t=106 :: The support group has made me feel accepted and given me courage to embrace myself.
- `srp`
  - Units: `10`
  - Relations: `8`
  - Predicted answer: `7 May 2023`
  - Unit `conv-26:D1:1` [dialog_turn] t=100 :: Hey Mel! Good to see you! How have you been?
  - Unit `conv-26:D1:2` [dialog_turn] t=101 :: Hey Caroline! Good to see you! I'm swamped with the kids & work. What's up with you? Anything new?
  - Unit `conv-26:session_1_observation:Caroline:1` [observation] t=101 :: The support group has made Caroline feel accepted and given her courage to embrace herself.
  - Unit `conv-26:D1:3` [dialog_turn] t=102 :: I went to a LGBTQ support group yesterday and it was so powerful.
  - Relation `conv-26:next:D1:6:D1:7` :: conv-26:D1:6 -> conv-26:D1:7 (next_turn)
  - Relation `conv-26:next:D1:7:D1:8` :: conv-26:D1:7 -> conv-26:D1:8 (next_turn)
  - Relation `conv-26:next:D1:2:D1:3` :: conv-26:D1:2 -> conv-26:D1:3 (next_turn)
  - Relation `conv-26:next:D1:3:D1:4` :: conv-26:D1:3 -> conv-26:D1:4 (next_turn)

### conv-26:qa:1

- Question: When did Melanie paint a sunrise?
- Gold answer: `2022`
- Official category: `2`
- Question labels: `temporal`
- Selection bucket: `temporal`
- Evidence ids: `conv-26:D1:12`
- Adapter passed: `True`

#### Adapter checks

| Check | Pass |
| --- | --- |
| `source_units_present` | `True` |
| `source_relations_present` | `True` |
| `target_units_present` | `True` |
| `target_relations_resolve` | `True` |
| `focus_units_resolve` | `True` |
| `focus_relations_resolve` | `True` |
| `target_units_subset_source` | `True` |
| `target_relations_subset_source` | `True` |
| `sample_id_consistent` | `True` |
| `session_datetime_present_on_dialog_turns` | `True` |
| `timestamps_non_decreasing` | `True` |

#### Source state preview

- Units: `647`
- Relations: `400`
- Unit `conv-26:D1:1` [dialog_turn] t=100 :: Hey Mel! Good to see you! How have you been?
- Unit `conv-26:session_1_observation:Caroline:0` [observation] t=100 :: Caroline attended an LGBTQ support group recently and found the transgender stories inspiring.
- Unit `conv-26:session_1_observation:Melanie:0` [observation] t=100 :: Melanie is currently managing kids and work and finds it overwhelming.
- Unit `conv-26:D1:2` [dialog_turn] t=101 :: Hey Caroline! Good to see you! I'm swamped with the kids & work. What's up with you? Anything new?
- Relation `conv-26:next:D1:1:D1:2` :: conv-26:D1:1 -> conv-26:D1:2 (next_turn)
- Relation `conv-26:next:D1:2:D1:3` :: conv-26:D1:2 -> conv-26:D1:3 (next_turn)
- Relation `conv-26:next:D1:3:D1:4` :: conv-26:D1:3 -> conv-26:D1:4 (next_turn)
- Relation `conv-26:next:D1:4:D1:5` :: conv-26:D1:4 -> conv-26:D1:5 (next_turn)

#### Gold target state preview

- Units: `3`
- Relations: `2`
- Target unit `conv-26:D1:11` [dialog_turn] t=110 :: I'm keen on counseling or working in mental health - I'd love to support those with similar issues.
- Target unit `conv-26:D1:12` [dialog_turn] t=111 :: You'd be a great counselor! Your empathy and understanding will really help the people you work with. By the way, take a look at this.
- Target unit `conv-26:D1:13` [dialog_turn] t=112 :: Thanks, Melanie! That's really sweet. Is this your own painting?
- Target relation `conv-26:next:D1:11:D1:12` :: conv-26:D1:11 -> conv-26:D1:12 (next_turn)
- Target relation `conv-26:next:D1:12:D1:13` :: conv-26:D1:12 -> conv-26:D1:13 (next_turn)

#### Baseline responses

| Baseline | Predicted | Answer Acc. | Coverage | Drift | Relation Acc. | Recovery Acc. | Closure Acc. | Cost | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `full_context` | 7 May 2023 | 0.428571 | 1.0 | 0.199 | 1.0 | 0.809524 | 1.0 | 1047.0 | evidence_failure, cost_failure |
| `vector_rag` | 7 May 2023 | 0.428571 | 0.0 | 0.8 | 0.0 | 0.142857 | 0.0 | 0.54 | representation_failure, relation_failure |
| `srp` | 7 May 2023 | 0.428571 | 0.0 | 1.0 | 0.0 | 0.142857 | 0.0 | 1.38 | representation_failure, relation_failure, evidence_failure |

#### Recovered state previews

- `full_context`
  - Units: `647`
  - Relations: `400`
  - Predicted answer: `7 May 2023`
  - Unit `conv-26:D1:1` [dialog_turn] t=100 :: Hey Mel! Good to see you! How have you been?
  - Unit `conv-26:session_1_observation:Caroline:0` [observation] t=100 :: Caroline attended an LGBTQ support group recently and found the transgender stories inspiring.
  - Unit `conv-26:session_1_observation:Melanie:0` [observation] t=100 :: Melanie is currently managing kids and work and finds it overwhelming.
  - Unit `conv-26:D1:2` [dialog_turn] t=101 :: Hey Caroline! Good to see you! I'm swamped with the kids & work. What's up with you? Anything new?
  - Relation `conv-26:next:D1:1:D1:2` :: conv-26:D1:1 -> conv-26:D1:2 (next_turn)
  - Relation `conv-26:next:D1:2:D1:3` :: conv-26:D1:2 -> conv-26:D1:3 (next_turn)
  - Relation `conv-26:next:D1:3:D1:4` :: conv-26:D1:3 -> conv-26:D1:4 (next_turn)
  - Relation `conv-26:next:D1:4:D1:5` :: conv-26:D1:4 -> conv-26:D1:5 (next_turn)
- `vector_rag`
  - Units: `3`
  - Relations: `0`
  - Predicted answer: `7 May 2023`
  - Unit `conv-26:session_1_observation:Melanie:1` [observation] t=101 :: Melanie painted a lake sunrise last year which holds special meaning to her.
  - Unit `conv-26:D1:3` [dialog_turn] t=102 :: I went to a LGBTQ support group yesterday and it was so powerful.
  - Unit `conv-26:session_1_observation:Melanie:2` [observation] t=102 :: Painting is a fun way for Melanie to express her feelings and get creative, helping her relax after a long day.
- `srp`
  - Units: `7`
  - Relations: `4`
  - Predicted answer: `7 May 2023`
  - Unit `conv-26:D1:1` [dialog_turn] t=100 :: Hey Mel! Good to see you! How have you been?
  - Unit `conv-26:D1:2` [dialog_turn] t=101 :: Hey Caroline! Good to see you! I'm swamped with the kids & work. What's up with you? Anything new?
  - Unit `conv-26:session_1_observation:Melanie:1` [observation] t=101 :: Melanie painted a lake sunrise last year which holds special meaning to her.
  - Unit `conv-26:D1:3` [dialog_turn] t=102 :: I went to a LGBTQ support group yesterday and it was so powerful.
  - Relation `conv-26:next:D1:2:D1:3` :: conv-26:D1:2 -> conv-26:D1:3 (next_turn)
  - Relation `conv-26:next:D1:3:D1:4` :: conv-26:D1:3 -> conv-26:D1:4 (next_turn)
  - Relation `conv-26:next:D1:1:D1:2` :: conv-26:D1:1 -> conv-26:D1:2 (next_turn)
  - Relation `conv-26:next:D1:4:D1:5` :: conv-26:D1:4 -> conv-26:D1:5 (next_turn)

## 5. Failure Summary

- cost_failure: `2`
- evidence_failure: `4`
- relation_failure: `3`
- representation_failure: `3`

### Failure Examples

- cost_failure: locomo:full_context:conv-26:qa:0, locomo:full_context:conv-26:qa:1
- evidence_failure: locomo:full_context:conv-26:qa:0, locomo:srp:conv-26:qa:0, locomo:full_context:conv-26:qa:1
- relation_failure: locomo:vector_rag:conv-26:qa:0, locomo:vector_rag:conv-26:qa:1, locomo:srp:conv-26:qa:1
- representation_failure: locomo:vector_rag:conv-26:qa:0, locomo:vector_rag:conv-26:qa:1, locomo:srp:conv-26:qa:1
