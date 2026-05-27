# Chapter 3 experiment batch

Generated: 2026-05-27T11:52:52
Replicates per scenario: 10
Replicate seeds: 1000 to 1009

## Data interpretation

- `step_results.csv` contains one row for every recorded simulation state.
- Step `0` is the initialized population before any transition.
- Step `n` is recorded after the model has completed transition step `n`.
- `raw/<scenario>/run_*_steps.csv` contains the same data for an individual run.
- `run_summary.csv` contains derived outcome measures for every run.
- `scenario_summary.csv` aggregates outcomes over replicates.
- `scenario_mean_curves.csv` contains padded mean curves: after an epidemic ends,
  its final state is carried forward to the configured maximum time horizon.

All tested scenarios use permanent post-recovery immunity, so
`ever_infected = population - final_susceptible` is valid.

## Scenarios

- baseline: Baseline
- transmission_low: Lower transmission
- transmission_high: Higher transmission
- vaccination_none: No vaccination points
- vaccination_dense: Expanded vaccination programme
- hospital_none: No hospital support
- hospital_expanded: Expanded hospital coverage
- avoidance_none: No avoidance behavior
- avoidance_high: High avoidance behavior
- quarantine_disabled: Quarantine disabled
- quarantine_early: Early quarantine activation
