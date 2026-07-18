# SRP Semantic Extraction Engine v2 Plan

This is the implementation companion to [SRP Runtime Representation v2 Specification](SRP_RUNTIME_REPRESENTATION_V2_SPEC.md) and [SRP Runtime Representation v2 Architecture](SRP_RUNTIME_REPRESENTATION_V2_ARCHITECTURE.md).

Status:

- prototype implemented
- treat the SRR v2 prototype as frozen
- do not expand this file into a larger runtime-layer roadmap until coverage attribution justifies it

Use the specification for the canonical model.

Use the architecture document for rationale.

Use this file for execution order.

---

## 1. Immediate Goal

Build a prototype Semantic Extraction Engine v2 that can populate the Runtime Representation v2 layers from source text.

The first version should focus on:

- provenance-aware node typing
- runtime object construction
- frame construction
- graph assembly
- extraction audit coverage

---

## 2. Build Order

### 2.1 Extraction Audit Expansion

- measure source information
- measure extracted information
- measure loss at the extraction boundary
- separate extraction loss from recovery loss

### 2.2 Provenance-Aware Node Typing

- add source span fields
- add extraction method fields
- distinguish extracted / inferred / copied / merged / rewritten content

### 2.3 Runtime Object Construction

- construct entities, events, states, constraints, goals, observations, inferences
- attach per-field confidence

### 2.4 Runtime Graph Assembly

- assemble typed nodes, edges, frames, provenance, and lifecycle metadata
- keep graph v1.5 frozen as the baseline representation

### 2.5 Validation Hookup

- expose layer-wise completeness metrics
- expose provenance completeness
- expose lifecycle fidelity

---

## 3. Acceptance Criteria

- extraction loss is measurable before recovery
- provenance exists on runtime objects
- the runtime IR can represent more than object presence
- the new extractor can be compared against the frozen graph v1.5 baseline

---

## 4. Deferred Work

Do not start these until the extraction engine prototype is real:

- graph recovery v2
- larger ontology expansion
- benchmark pressure changes
- strong baseline comparisons

The prototype is now real, so this document is frozen as an implementation record.
