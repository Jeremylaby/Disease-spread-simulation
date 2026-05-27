# Generated experiment results

This directory is populated by:

```powershell
python chapter_3\experiments\run_experiments.py
```

Each execution creates a new batch subdirectory rather than overwriting older
results. A batch contains detailed per-step CSV data, run and scenario
summaries, and PNG plots for individual runs and comparisons.

Do not treat short runs executed with `--max-steps` as final experimental
evidence; that option is intended only for technical verification.
