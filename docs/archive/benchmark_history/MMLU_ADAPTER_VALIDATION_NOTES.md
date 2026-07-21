# MMLU Adapter Validation Notes

## Issue

The initial MMLU smoke run exposed a parsing bug in the adapter:

- integer answer labels such as `0` were treated as falsy
- this caused the adapter to mis-handle valid zero-indexed answers

## Fix

- replaced truthiness-based answer selection with explicit `None` checks
- preserved zero-valued labels during normalization

## Impact

- improved prediction parsing correctness
- preserved the integrity of smoke artifact generation
- ensured baseline and SRP results were computed from correctly normalized answers

## Verification

- MMLU smoke was rerun after the fix
- the rerun produced a complete artifact bundle
- adapter and shared benchmark tests passed after the fix

