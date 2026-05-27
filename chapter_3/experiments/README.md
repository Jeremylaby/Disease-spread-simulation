# Chapter 3 experiments

This directory contains reproducible configurations and a runner for the
experimental research chapter. It does not use the live visualization.

## Design

The baseline is compared with interventions in five families:

- transmission probability: lower and higher `beta`;
- vaccination: no vaccination points and expanded vaccination access;
- hospital support: no hospital and expanded hospital coverage;
- avoidance behavior: no avoidance and high avoidance;
- quarantine: disabled and early activation.

Each scenario is executed repeatedly with the same series of seeds. Matching
seeds make comparisons more meaningful because each scenario starts from an
equivalent randomized population realization.

## Run

From the repository root:

```powershell
python chapter_3\experiments\run_experiments.py
```

The default execution performs 10 replicates for every scenario. For a quick
test:

```powershell
python chapter_3\experiments\run_experiments.py --replicates 1 --max-steps 10 --scenarios baseline
```

Outputs are written into a new time-stamped directory inside
`chapter_3/results/`, so previous experimental data are not overwritten.
For verification runs, `--results-dir` can redirect outputs to a separate
directory without contaminating the final result set.

## Output files

- `experiment_manifest.csv`: scenario definitions and complete parameters.
- `step_results.csv`: all detailed step-by-step observations.
- `raw/<scenario>/run_*_steps.csv`: one detailed CSV per individual run.
- `run_summary.csv`: outcomes calculated for each run.
- `scenario_summary.csv`: outcomes averaged over repeated runs.
- `scenario_mean_curves.csv`: mean time series for scenario comparisons.
- `plots/runs/`: individual epidemic curve PNG files.
- `plots/scenarios/`: mean epidemic curve PNG files.
- `plots/comparisons/`: comparative mean-infection PNG files for each family.
