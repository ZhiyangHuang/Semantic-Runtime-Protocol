# Generated Configs

This directory stores launcher-generated session configs.

They are useful because they preserve the exact parameters used for a launched run, including:

- selected method
- selected task group
- selected profile
- selected output root
- timestamped session namespace

## Important Rule

These configs are execution records, not canonical experiment plans.

Use them to:

- reproduce one specific launched run
- audit which parameters were used
- map a result directory back to its generated config

Do not use them as the main source of truth for semester-level experiment planning.

For canonical planning, use:

- `../longbench_v2_multimodel_100_1000_smoke.json`
- `../longbench_v2_multimodel_100_1000.json`
- `../first_paper_formal_local.json`
