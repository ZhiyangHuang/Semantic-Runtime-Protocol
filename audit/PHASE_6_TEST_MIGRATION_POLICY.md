# Phase 6.3 Test Migration Policy

## Purpose

Phase 6.3 removes test dependencies on the legacy namespace without breaking the frozen v1 compatibility surface.

The goal is not to make every `srp_experiment` reference disappear immediately.
The goal is to move tests that already have live equivalents while keeping explicit legacy-compatibility tests until deletion is safe.

## Test Classes

### 1. Live behavior tests

These tests assert behavior that already exists in live namespaces such as `experiments/`, `experiments/srp_runtime_legacy/`, or `srp_runtime/`.

Action:

- migrate the import path to the live namespace
- keep the behavioral assertions unchanged

### 2. Legacy compatibility tests

These tests intentionally verify that the frozen compatibility surface still works.

Action:

- keep them in a clearly labeled legacy-compatibility area until the legacy tree is deleted
- do not migrate them simply to reduce reference counts

### 3. Historical regression tests

These tests reproduce prior bugs, archived boundary conditions, or frozen release behaviors.

Action:

- keep them only if they still support the v1 evidence chain
- otherwise retire them with an audit note

## Migration Rule

Only tests that target live behavior are eligible for Phase 6.3 migration.

Compatibility and historical tests remain blocking references until the deletion decision is made.

## Acceptance Criteria

Phase 6.3 is complete only when:

- live-behavior tests no longer import `srp_experiment`
- any remaining `srp_experiment` references are explicitly tagged legacy-compatibility or archival
- release verification continues to pass
- the dependency report shows `test_imports = 0` or an explicitly approved legacy remainder

## Current Position

The first H1 batch has already moved the obvious live-behavior analysis tests to live namespaces.
The remaining work is to separate the legacy compatibility suite from the live regression suite and then migrate the rest in small batches.
