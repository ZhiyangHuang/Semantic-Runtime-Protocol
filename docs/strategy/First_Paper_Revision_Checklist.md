# First Paper Revision Checklist

## Purpose

This file translates the current paper review into a practical revision checklist for the first paper package in `first_paper/`.

It is not part of the submit-ready draft itself.
It is a strategy-side correction plan for turning the current draft into a more defensible short paper.

## Executive Summary

The current first paper is no longer a loose blueprint. It already has:

- a clear topic
- a stable paper frame
- a minimal formal layer
- a runnable experiment scaffold
- a LaTeX compilation path that works

However, the main difficulty is no longer "having an idea." The main difficulty is that the paper currently looks stronger than the evidence behind it.

At the moment:

- the topic is timely and relevant
- the research question is reasonably clear
- the paper structure is mostly complete
- the experiment scaffold is reproducible

But:

- the evidence is still too thin
- the current results do not yet support the strongest version of the claim
- parts of the draft still read like a project plan rather than a finished research paper
- the benchmark and task evidence are still closer to scaffold than final proof

The overall difficulty is therefore not "content too short," but "evidence too weak relative to the stated claim."

## Overall Judgment

### What Is Already Strong

- The paper is focused enough for a first submission.
- The central question is understandable:
  - can explicit semantic-state management improve finite-horizon stability under repeated compression-recovery cycles?
- The formalization is appropriately narrow for a semester paper.
- The repo already has a working experiment scaffold, shared query flow, batch summary pipeline, and paper-table export path.

### What Is Still Weak

- The current experimental evidence is not yet strong enough to support the strongest wording in the abstract and introduction.
- The results section still behaves partly like an expected-results section.
- Some project-management material still appears inside the paper draft.
- The benchmark layer is still too small for a convincing main submission.

## Current Risk Level

The current first paper is viable as a short-paper candidate, but only if the claim is tightened and the evidence is upgraded.

If nothing changes, the most likely reviewer concerns are:

- the claim is bigger than the evidence
- the benchmark is too small
- the results are still pilot-level
- the contribution is interesting, but not yet sufficiently validated

## Main Findings

## 1. Title and Research Question

### Current State

The title is technically strong and thematically aligned with long-horizon LLM stability. The research question is also fairly clear.

### Main Risk

The wording is still slightly heavier than the current evidence base. The problem is not conceptual confusion; the problem is claim pressure.

### Revision Direction

- Keep the topic and title family stable.
- Make sure the abstract and introduction ask a falsifiable first-paper question rather than sounding like a broad system claim.
- Preserve the narrow research question near the top of the introduction.

## 2. Literature Review

### Current State

The draft covers relevant directions:

- prompt compression
- memory-augmented LLM systems
- retrieval-based systems
- semantic communication
- reproducibility and evaluation

### Main Risk

The related-work section still reads more like positioning notes than a strong academic comparison layer.

### Revision Direction

- Add more explicit contrast between SRP and existing memory or retrieval methods.
- State more clearly why prior methods do not directly manage semantic state as a runtime object.
- Add one clearer sentence per subsection:
  - what prior work solves
  - what it does not solve
  - why SRP studies a different layer

## 3. Formalization

### Current State

The formal layer is already appropriate for a semester paper:

- `S_t = (M_t, V_t, P_t)`
- compression / recovery / validation / update
- observation operator
- drift definition
- bounded finite-horizon claim

### Main Risk

The formalization is not the biggest weakness anymore. The larger issue is that the experiment layer has not yet matched the formal ambition.

### Revision Direction

- Keep the formal layer modest.
- Do not expand toward a larger theorem program right now.
- Use the formalization only to support measurable empirical claims.

## 4. Experimental Design

### Current State

The experiment scaffold is technically solid:

- shared query flow exists
- task files define canonical `queries`
- metrics are logged
- batch summary and paper tables are already wired

New evidence from the local pilot:

- the local `Qwen/Qwen3-4B-AWQ + vLLM` backend now runs end to end
- `results.json`, `summary.json`, and `run_metadata.json` are generated on a real model run
- shared-query evaluation remains consistent across methods at the same `task_id + cycle`
- prompt and state redesign already changed the measured SRP profile in meaningful ways

### Main Risk

The current evidence base is still too small:

- only a few toy tasks
- current outputs are still scaffold-level
- benchmark imports are not yet the main paper evidence
- the current `query_success` metric is still too coarse to support strong comparative claims
- short-memory `3`-cycle toy tasks naturally favor `raw_prompt` and `rag`

### Revision Direction

- Treat current toy tasks as pipeline validation only.
- Move toward one long-context benchmark family and one memory benchmark family.
- Keep the one-framework-many-questions design.
- Freeze the prompt family, cycle settings, and query schedule before running final comparisons.
- Treat the tuned local pilot as real progress in implementation, not yet as final paper evidence.

## 5. Results and Argumentation

### Current State

The results structure is correct:

- drift
- task success
- token cost
- strongest-baseline comparison

### Main Risk

The current experimental outputs do not yet support the strongest wording of the main claim. In the current scaffold results, SRP is not yet outperforming the strongest baseline.

New evidence from the local pilot:

- the untuned local `3`-cycle pilot placed `srp` behind `summarization` and `rag`
- the first two tuning rounds improved `srp` materially:
  - drift dropped
  - task success improved
  - token cost dropped sharply
- the later `tuned4` local `5`-cycle pilot made SRP more credible again after the over-abstracted `tuned3` regression
- under `tuned4 + 5 cycles`, SRP became much stronger in task success and token cost than in the earliest local pilot, even though `rag` still remained the strongest drift baseline
- the `tuned4 + 7 cycles` extension kept SRP far above plain summarization on `task_success`, which strengthens the case that SRP becomes more meaningful in the longer-cycle regime than in the original `3`-cycle toy setting
- however, the tuned `srp` path still does not beat `rag` on short-memory `3`-cycle toy tasks

This means the project now has a real failure-boundary signal rather than only a missing experiment.

### Revision Direction

- Downgrade the paper claim until real results support stronger language.
- Recast the current results as pilot results if needed.
- Convert result subsections from "should show" language to "current results show" language once real runs are available.
- Add numeric summary tables and not only descriptive interpretation.
- Use the local pilot to justify a more honest limitations and failure-boundary section.

Short audit summary for current pilot interpretation:

- shared backend and scoring layers have already changed across local tuning rounds, so baseline movement is expected
- SRP-specific changes mainly live in the compression, recovery, state, and validation path
- current tables are useful as tuning and failure-boundary evidence, but not every cross-round comparison should be treated as a clean isolated SRP comparison

## 6. Conclusion and Limitations

### Current State

The draft is already reasonably cautious, and it preserves limitations and open questions.

### Main Risk

The conclusion is still safer than the evidence, but some earlier sections remain slightly more ambitious than the actual result base.

### Revision Direction

- Keep limitations explicit.
- Preserve the failure boundary.
- Keep future work separate from first-paper claims.
- Make sure the conclusion reflects what was actually demonstrated, not only what was planned.

## 7. Writing and Submission Readiness

### Current State

The paper is readable and structurally coherent, but not yet fully paper-like in all sections.

### Main Risk

Some sections still sound like internal planning documents:

- submission strategy
- immediate next steps
- recommendation-letter or faculty-support framing

These are useful for project management, but they should not remain in the paper draft.

### Revision Direction

- Remove project-management sections from the paper draft.
- Keep those materials in `docs/` or `00_Current_Stage_Report.md`.
- Make the paper itself look more like a self-contained research submission.

## Priority Checklist

## P0: Must Fix Before Submission

- unify the main comparison across Markdown and LaTeX
- reduce the core claim until it matches the current evidence
- remove planning-oriented sections from the paper body
- clarify that current toy tasks are not final paper evidence
- run at least one real-backend minimal comparison
- document the local pilot improvements and failure boundaries so the paper claim stays aligned with the evidence

## P1: Strongly Recommended

- strengthen related-work contrasts
- convert the current results section from expected-results language to actual-results language
- add stronger numeric tables and clear result interpretation
- clarify benchmark import status and evidence hierarchy
- replace task-level query scoring with per-query expected answers or query-level keyword sets
- test whether SRP improves at `5` or `7` cycles rather than treating `3` cycles as the main proof regime

## P2: Nice to Have

- add one more ablation if the main comparison is already stable
- add one more benchmark family only if the first benchmark is already working cleanly
- improve figure polish and captions

## Concrete Modification Directions

1. Rewrite the abstract and introduction so the paper says:
   - "tests whether SRP improves finite-horizon stability"
   instead of:
   - "shows that SRP improves stability"
   until stronger results are available.

2. Make the main comparison definition consistent across:
   - `first_paper/draft/01_Full_Draft.md`
   - `first_paper/latex/main.tex`
   - `docs/paper_sections/04_Experiment_Section.md`

3. Replace plan-style paper sections with proper paper sections:
   - remove `Submission Strategy`
   - remove `Immediate Next Steps`
   - keep those materials in strategy docs instead

4. Recast the current experimental story:
   - toy tasks = scaffold validation
   - benchmark imports = future main evidence
   - real backend runs = required before strong claims
   - tuned local pilots = implementation evidence and failure-boundary evidence

5. Add stronger reviewer-facing comparisons in related work:
   - prompt compression vs semantic state
   - retrieval memory vs runtime-governed state
   - memory storage vs semantic transformation control

6. Upgrade the results layer:
   - provide numeric tables
   - state whether the current results are pilot or final
   - add one clear interpretation paragraph per metric block
   - explain why low-cycle toy tasks can understate SRP's intended advantage
   - explain how protocol leakage and reasoning-trace pollution affected early local runs

## Suggested Timeline

### Week 1

- unify paper wording and comparison scope
- remove planning sections from the paper body
- downgrade claim wording to match current evidence

### Week 2

- run the smallest real-backend experiment
- verify the shared-query flow and benchmark import path
- generate updated drift, task success, and token cost tables

### Week 3

- rewrite the results section around actual outputs
- strengthen related work
- finalize limitations and failure boundary

### Week 4

- prepare advisor-facing review version
- compile final paper PDF
- do one last language and formatting pass

## Risks and Mitigations

### Risk 1

Real-backend results still do not support SRP over the strongest baseline.

Mitigation:

- weaken the claim to characterization rather than superiority
- emphasize failure boundary and tradeoff analysis

### Risk 2

Benchmark integration takes too long.

Mitigation:

- keep toy tasks for scaffold validation
- run one benchmark family cleanly rather than two benchmark families poorly

### Risk 3

The paper still reads like a proposal instead of a result paper.

Mitigation:

- delete planning sections from the main draft
- rewrite all "should" language in the results section

## Final Guidance

The main path forward is not to add more theory.

The main path forward is:

- tighten the claim
- align the paper with the actual evidence
- upgrade the benchmark layer
- keep only paper-like material in the paper

That is the highest-probability route to turning the current first paper into a credible short submission.
