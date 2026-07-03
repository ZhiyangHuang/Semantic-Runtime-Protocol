# One-Semester Execution Checklist

## Goal

This document rewrites the current SRP paper and experiment plan into a version that is realistic for:

- one undergraduate student
- one remaining semester before graduation
- limited funding
- academic positioning as the primary goal
- job value as the secondary goal

This is also the first SRP paper, the first top-conference-oriented paper in my undergraduate research path, and it must be finished within one semester of focused refinement.

The purpose is not to maximize ambition. The purpose is to maximize the probability of finishing a credible research project that can lead to:

- professor support
- a recommendation letter
- a short paper or workshop-style paper
- a public research repo
- a stronger academic and job narrative

## Core Rule

Do not optimize for the biggest paper.

Optimize for the strongest completed package:

1. a narrow research claim
2. a reproducible experiment
3. a readable draft
4. a professor who is willing to back the work

Prefer one evaluation framework that answers many reviewer-facing questions over many loosely related experiments that each answer only one question.

## Final Scope

### Paper Scope

The first paper should make only one main claim:

> Explicit semantic-state management can improve finite-horizon stability under repeated compression-recovery cycles, relative to simple summarization and other lightweight context baselines.

This is enough.

The following are out of scope for the semester:

- a universal semantic theory
- a full agent architecture
- a general operating system for LLMs
- a multi-domain large-scale benchmark
- a top-tier full-paper contribution in one step

### Experiment Scope

Keep the experiment at the smallest scale that still looks like real research.

Recommended main setup:

- `1` main model
- `2` core task families
- `3` main methods in the body
- `3` cycle settings
- `1-2` ablations

Recommended body methods:

- `summarization`
- `strongest baseline`
- `srp`

Recommended appendix methods:

- `raw_prompt`
- `rag`

Recommended main tasks:

- multi-turn instruction consistency
- iterative compression-recovery cycles

Optional extra task only if time remains:

- long-context summarization/regeneration

Recommended cycle settings:

- `3`
- `5`
- `7`

Recommended ablations:

- SRP without recovery
- SRP without validation

Recommended dataset rule:

- no more than `2` benchmark families in the semester version
- one long-context family such as `LongBench`
- one memory or conversation family such as `LoCoMo` or `LongMemEval`

Recommended prompt rule:

- keep one compression prompt family
- keep one recovery prompt family
- keep one judge prompt family
- do not rewrite the full prompt protocol for every experiment

## Deliverables

By the end of the semester, the target package should contain:

### Academic Deliverables

- one polished `research pitch`
- one professor-facing one-page summary
- one complete short paper draft
- one table-ready experiment section
- one recommendation-letter-worthy research repo

### Technical Deliverables

- reproducible `srp_experiment/`
- batch experiment config
- summary tables
- paper-ready LaTeX tables
- one shared-query evaluation flow so all methods answer the same question schedule

### Evidence And Data Management

- current formal evidence namespace under `srp_experiment/results/batch_runs/first_paper_formal_local`
- legacy or suspect exploratory outputs archived under `legacy_results/`
- future refactor reruns kept in a separate namespace so they do not overwrite the current formal evidence

### Career Deliverables

- one public or private repo with clean README
- one concise project summary for resume use
- one research narrative that connects to AI systems / evaluation / long-horizon LLMs

## What To Cut

The following items are out of scope for the semester unless everything else is already finished:

- full theoretical guarantee section beyond a clean finite-horizon sketch
- large-scale multi-model sweep
- many datasets
- enterprise runtime architecture
- governance or protocol standardization
- RL-based extensions
- too many benchmarks
- too many figures

If an idea is interesting but not necessary for submission, defer it to:

- future work
- appendix
- repo issues
- next paper

## Weekly Plan

## Week 1

### Objective

Lock the scope.

### Tasks

- rewrite the paper title and claim into the narrow version
- freeze the main task families
- freeze the main methods
- freeze the cycle settings
- define the exact figures and tables needed

### End-of-Week Output

- one-page paper scope note
- one-page professor pitch
- final experiment checklist

## Week 2

### Objective

Make the experiment runnable end to end.

### Tasks

- make sure `srp_experiment/` runs with one default configuration
- verify output for `results.json`, `summary.json`, and plots
- generate one first drift plot
- generate one first paper-style table

### End-of-Week Output

- one working baseline run
- one working SRP run
- one drift plot
- one summary table

## Week 3

### Objective

Turn the project into something a professor can evaluate quickly.

### Tasks

- clean the repo README
- prepare one professor-facing update
- prepare one 5-minute explanation version
- contact the first professor

### End-of-Week Output

- professor outreach email
- one-page research pitch
- cleaned repo structure

## Week 4

### Objective

Get the main experiment results stable.

### Tasks

- run the main 3 method comparison
- finalize the main `3/5/7` cycle experiment
- export `quality`, `efficiency`, and `camera_ready` tables
- identify the strongest baseline clearly

### End-of-Week Output

- main result table
- quality table
- efficiency table
- camera-ready comparison table

## Week 5

### Objective

Write the shortest complete paper draft.

### Tasks

- finalize introduction
- finalize method section
- finalize experiment section
- insert figures and tables
- write limitations honestly

### End-of-Week Output

- complete short draft v1

## Week 6

### Objective

Refine for credibility.

### Tasks

- remove exaggerated claims
- tighten related work
- simplify formalization where needed
- make figure captions publication-ready
- make tables cleaner

### End-of-Week Output

- short draft v2
- professor-reviewable version

## Week 7 and Beyond

### Objective

Choose the best use of remaining time.

Priority order:

1. improve clarity of the current paper
2. improve reproducibility
3. add one ablation
4. add one extra task
5. add one extra model

Do not reverse this order.

## Paper Structure

The recommended paper structure for your semester version is:

1. Introduction
2. Related Work
3. SRP Framework
4. Minimal Formalization
5. Experimental Setup
6. Results
7. Limitations
8. Conclusion

Keep future work short.

Keep formalization practical.

Keep results section stronger than theory section.

## Open Questions To Preserve

These are preserved for future work and should not be forced closed before the semester paper is ready:

- Is SRP fundamentally a runtime, a protocol, or a semantic communication layer?
- What is the minimal semantic-state object?
- Which drift proxy is the most defensible first-paper metric?
- Where exactly is the novelty boundary relative to retrieval memory and prompt compression?
- What failure cases should be shown explicitly rather than hidden?
- What would count as evidence that `S_t` is a sufficient state rather than only a compressed cache?
- Which runtime lifecycle operations belong in the first paper, and which should stay as future work?
- Should the theory borrow explicitly from predictive state representation, or remain a simpler runtime framing in the first semester paper?
- Should vocabulary mapping eventually become a first-class semantic contract rather than only an auxiliary field?
- Should the runtime also include a reverse-expansion step so compressed concepts can be made understandable to the user again?
- Should semantic updates eventually be modeled as transaction-style commit / rollback behavior?

These questions are part of the project, not a sign that the project is unfinished.

## Minimum Publishable Unit

If the semester becomes too compressed, the absolute minimum publishable unit is:

- one model
- one core task
- `summarization` vs `srp`
- one drift figure
- one token-efficiency table
- one short paper draft

This is still much better than an unfinished project expansion.

## Professor Strategy

The professor should not be asked to validate a broad theory.

The professor should be asked to support a narrow, disciplined, already-running research project.

What you want from a professor:

- periodic feedback
- project legitimacy
- possible independent study or supervision
- future recommendation support

What you should show:

- scope control
- clean execution
- reproducibility
- honesty about limitations

## Academic Positioning

Your academic identity for this project should be:

> undergraduate researcher working on long-horizon LLM stability, semantic-state abstraction, and reproducible evaluation

This is much stronger than presenting yourself as:

- someone with a huge untested new paradigm
- someone trying to replace all existing memory systems

## Job Positioning

The project should also be legible for hiring.

Useful job-facing tags:

- LLM systems
- evaluation
- prompt and compression pipelines
- experiment reproducibility
- AI infrastructure
- model benchmarking

## Risk Control

If you feel overloaded, cut in this order:

1. cut extra models
2. cut extra tasks
3. cut extra ablations
4. cut extra theory
5. do not cut the main experiment

Never cut the core runnable pipeline just to keep a bigger story alive.

## Success Criteria

This semester is successful if, by the end, you have:

- one credible short paper draft
- one clean experiment repo
- one professor who takes the project seriously
- one set of paper-ready figures and tables
- one strong academic narrative you can reuse

That outcome is realistic, valuable, and much more important than chasing a version of the project that is too large to finish.
