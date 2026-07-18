# Real Validation Scientific Report

This is the final scientific summary for the 7/18 LoCoMo real-validation slice.
It is intentionally short and conclusion-oriented.

## Research Question

Does SRP prevent unsupported semantic transitions in a real dataset slice?

## Dataset

- LoCoMo real slice
- physical source: `data/locomo/locomo10.json`
- selected sample: `conv-26`
- selected events: `temporal_refinement`, `unsupported_mutation`, `contradiction_update`

## Compared Systems

- `SRP`
- `Direct mutation baseline`

## Results

| Event | SRP | Direct Mutation Baseline |
| --- | --- | --- |
| `temporal_refinement` | accept | accept |
| `unsupported_mutation` | reject | accept |
| `contradiction_update` | accept | accept |

Aggregate comparison:

| Metric | SRP | Direct Mutation Baseline |
| --- | ---: | ---: |
| accepted transitions | `2` | `3` |
| rejected transitions | `1` | `0` |
| invalid accept rate | `0.0` | `1.0` |
| unsupported mutation accepted | `False` | `True` |
| recommendation/execution separated | `True` | `False` |
| replay consistency | `1.0` | `1.0` |

## Interpretation

The direct-mutation baseline accepts an unsupported mutation because it has no validation boundary.
SRP rejects that same mutation while preserving the governance boundary.

This is the key mechanism result:

> SRP blocks unsupported semantic transitions; a direct update path does not.

## Limitations

- The slice is small and manually audited.
- This is not a leaderboard comparison.
- The result does not imply universal memory superiority.
- LongMemEval remains protocol-ready, but its real-data slice is still pending and is not part of the current release gate.

## Conclusion

The LoCoMo slice provides comparative empirical evidence for the SRP governance claim.
It supports the statement that semantic runtime governance can reject unsupported transitions, not merely score them.
