# Experiment Progress Report

## Current Status

The project has passed the "can SRP be turned into a paper?" threshold.
The current risk is no longer missing core experiments; it is evidence sprawl, duplicate entrypoints, and mixed namespaces.

## What Is Working

- submission-shape draft exists
- qualified experiment gate exists
- LongBench v2 frozen public layer exists
- launcher exists for grouped runs
- repeat aggregation exists
- long-horizon reporting exists
- submission audit exists

## What Is Still Messy

- too many scripts are visible as if they were equal entrypoints
- results include both formal evidence and smoke/debug residues
- some duplicate output namespaces exist, especially accidental nested paths
- diagnostic tools and primary tools are not clearly separated

## Current Highest-Priority Risks

1. experiment outputs become harder to audit because namespaces are mixed
2. baseline semantics become harder to explain if implementation and wording drift apart
3. semester time gets wasted on tool sprawl instead of core report completion

## Current Mitigation Direction

- freeze the canonical experiment path
- demote duplicate tooling before deleting anything
- preserve strong diagnostics, but move them out of the main user-facing path conceptually
- keep paper-facing evidence in a clearly named, stable namespace

## Current Working Conclusion

The project should now behave like a paper production system, not like an exploratory prototype playground.
