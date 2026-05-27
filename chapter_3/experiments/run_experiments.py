"""Run repeatable Chapter 3 experiments and save machine-readable results.

Usage from the repository root:
    python chapter_3/experiments/run_experiments.py
    python chapter_3/experiments/run_experiments.py --replicates 5
    python chapter_3/experiments/run_experiments.py --scenarios baseline transmission_high
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
EXPERIMENTS_DIR = Path(__file__).resolve().parent
DEFAULT_RESULTS_DIR = ROOT_DIR / "chapter_3" / "results"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))

from agents.citizen import Citizen, State
from model.disease_model import DiseaseModel

from experiment_configs import SCENARIOS, SCENARIOS_BY_ID, Scenario


STATE_COLUMNS = {
    State.SUSCEPTIBLE: "Susceptible",
    State.EXPOSED: "Exposed",
    State.INFECTED: "Infected",
    State.RECOVERED: "Recovered",
    State.DECEASED: "Deceased",
}

PLOT_COLUMNS = [
    "Susceptible",
    "Exposed",
    "Infected",
    "Recovered",
    "Deceased",
]

PLOT_COLORS = {
    "Susceptible": "#1f77b4",
    "Exposed": "#ff7f0e",
    "Infected": "#2ca02c",
    "Recovered": "#d62728",
    "Deceased": "#9467bd",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run reproducible disease simulation experiments for Chapter 3."
    )
    parser.add_argument(
        "--replicates",
        type=int,
        default=10,
        help="Number of runs per scenario. Default: 10.",
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=1000,
        help="Seed for replicate 1; the same seed series is used for each scenario.",
    )
    parser.add_argument(
        "--scenarios",
        nargs="*",
        choices=sorted(SCENARIOS_BY_ID),
        default=None,
        help="Scenario identifiers to run. Default: all scenarios.",
    )
    parser.add_argument(
        "--batch-name",
        default=None,
        help="Optional output subdirectory name under chapter_3/results.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory for output batches. Default: chapter_3/results.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Optional run horizon override for short verification runs.",
    )
    args = parser.parse_args()

    if args.replicates <= 0:
        parser.error("--replicates must be greater than zero.")
    if args.max_steps is not None and args.max_steps <= 0:
        parser.error("--max-steps must be greater than zero.")

    return args


def flatten_config(value: Any, prefix: str = "") -> dict[str, Any]:
    flattened = {}
    if isinstance(value, dict):
        for key, child in value.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            flattened.update(flatten_config(child, new_prefix))
    elif isinstance(value, list):
        flattened[prefix] = json.dumps(value, separators=(",", ":"))
    else:
        flattened[prefix] = value
    return flattened


def create_output_dirs(results_root: Path, batch_name: str | None) -> dict[str, Path]:
    if batch_name is None:
        batch_name = datetime.now().strftime("batch_%Y%m%d_%H%M%S")

    batch_dir = results_root / batch_name
    if batch_dir.exists() and any(batch_dir.iterdir()):
        raise FileExistsError(
            f"Output batch already exists and is not empty: {batch_dir}. "
            "Choose a new --batch-name."
        )

    dirs = {
        "batch": batch_dir,
        "raw": batch_dir / "raw",
        "run_plots": batch_dir / "plots" / "runs",
        "scenario_plots": batch_dir / "plots" / "scenarios",
        "comparison_plots": batch_dir / "plots" / "comparisons",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def record_state(
    model: DiseaseModel,
    scenario: Scenario,
    replicate: int,
    seed: int,
) -> dict[str, Any]:
    citizens = [agent for agent in model.agents if isinstance(agent, Citizen)]
    counts = {
        column: sum(1 for citizen in citizens if citizen.state == state)
        for state, column in STATE_COLUMNS.items()
    }
    infected = counts["Infected"]
    population = scenario.config.population.num_citizens

    return {
        "scenario_id": scenario.scenario_id,
        "scenario_label": scenario.label,
        "family": scenario.family,
        "replicate": replicate,
        "seed": seed,
        "step": model.current_step,
        **counts,
        "Vaccinated": sum(1 for citizen in citizens if citizen.is_vaccinated),
        "QuarantineZones": len(model.quarantine_zones),
        "HospitalPatients": sum(hospital.current_patients for hospital in model.hospitals),
        "InfectedPercent": infected / population * 100,
    }


def run_single_simulation(
    scenario: Scenario,
    replicate: int,
    seed: int,
) -> pd.DataFrame:
    config = replace(scenario.config, seed=seed)
    model = DiseaseModel(config)
    rows = [record_state(model, scenario, replicate, seed)]

    while model.current_step < config.num_steps:
        model.step()
        row = record_state(model, scenario, replicate, seed)
        rows.append(row)
        if row["Infected"] == 0 and row["Exposed"] == 0:
            break

    return pd.DataFrame(rows)


def summarize_run(steps: pd.DataFrame, scenario: Scenario) -> dict[str, Any]:
    final = steps.iloc[-1]
    peak_row = steps.loc[steps["Infected"].idxmax()]
    population = scenario.config.population.num_citizens
    ever_infected = population - int(final["Susceptible"])

    return {
        "scenario_id": scenario.scenario_id,
        "scenario_label": scenario.label,
        "family": scenario.family,
        "replicate": int(final["replicate"]),
        "seed": int(final["seed"]),
        "steps_completed": int(final["step"]),
        "epidemic_ended": bool(final["Infected"] == 0 and final["Exposed"] == 0),
        "peak_infected": int(peak_row["Infected"]),
        "peak_infected_step": int(peak_row["step"]),
        "infected_person_steps": int(steps["Infected"].sum()),
        "ever_infected": ever_infected,
        "attack_rate_percent": ever_infected / population * 100,
        "final_susceptible": int(final["Susceptible"]),
        "final_recovered": int(final["Recovered"]),
        "final_deceased": int(final["Deceased"]),
        "mortality_percent_population": float(final["Deceased"]) / population * 100,
        "final_vaccinated": int(final["Vaccinated"]),
        "peak_quarantine_zones": int(steps["QuarantineZones"].max()),
        "steps_with_quarantine": int((steps["QuarantineZones"] > 0).sum()),
        "peak_hospital_patients": int(steps["HospitalPatients"].max()),
    }


def plot_run_curve(steps: pd.DataFrame, title: str, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    for column in PLOT_COLUMNS:
        ax.plot(
            steps["step"],
            steps[column],
            label=column,
            linewidth=2,
            color=PLOT_COLORS[column],
        )
    ax.set_title(title)
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Number of citizens")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def padded_steps_for_means(
    run_frames: list[pd.DataFrame],
    scenario: Scenario,
) -> pd.DataFrame:
    padded = []
    steps_index = pd.Index(range(scenario.config.num_steps + 1), name="step")
    for frame in run_frames:
        numeric = frame.set_index("step")[PLOT_COLUMNS + ["Vaccinated", "QuarantineZones"]]
        numeric = numeric.reindex(steps_index).ffill()
        numeric["scenario_id"] = scenario.scenario_id
        numeric["replicate"] = int(frame.iloc[0]["replicate"])
        padded.append(numeric.reset_index())
    return pd.concat(padded, ignore_index=True)


def build_scenario_mean_curves(
    frames_by_scenario: dict[str, list[pd.DataFrame]],
    scenarios: list[Scenario],
) -> pd.DataFrame:
    aggregates = []
    for scenario in scenarios:
        padded = padded_steps_for_means(frames_by_scenario[scenario.scenario_id], scenario)
        grouped = padded.groupby("step", as_index=False)[
            PLOT_COLUMNS + ["Vaccinated", "QuarantineZones"]
        ].agg(["mean", "std"])
        grouped.columns = [
            "step" if column[0] == "step" else f"{column[0]}_{column[1]}"
            for column in grouped.columns.to_flat_index()
        ]
        grouped.insert(0, "scenario_id", scenario.scenario_id)
        grouped.insert(1, "scenario_label", scenario.label)
        grouped.insert(2, "family", scenario.family)
        aggregates.append(grouped)
    return pd.concat(aggregates, ignore_index=True)


def plot_scenario_mean_curve(
    mean_curves: pd.DataFrame,
    scenario: Scenario,
    output_path: Path,
) -> None:
    data = mean_curves[mean_curves["scenario_id"] == scenario.scenario_id]
    fig, ax = plt.subplots(figsize=(10, 6))
    for column in PLOT_COLUMNS:
        ax.plot(
            data["step"],
            data[f"{column}_mean"],
            label=column,
            linewidth=2,
            color=PLOT_COLORS[column],
        )
    ax.set_title(f"{scenario.label}: mean epidemic curve")
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Mean number of citizens")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_family_comparisons(
    mean_curves: pd.DataFrame,
    scenarios: list[Scenario],
    output_dir: Path,
) -> None:
    baseline = SCENARIOS_BY_ID["baseline"]
    families = sorted({scenario.family for scenario in scenarios if scenario.family != "reference"})
    scenario_ids = {scenario.scenario_id for scenario in scenarios}

    for family in families:
        family_scenarios = [
            scenario
            for scenario in scenarios
            if scenario.family == family
        ]
        if baseline.scenario_id in scenario_ids:
            family_scenarios.insert(0, baseline)

        fig, ax = plt.subplots(figsize=(10, 6))
        for scenario in family_scenarios:
            data = mean_curves[mean_curves["scenario_id"] == scenario.scenario_id]
            ax.plot(
                data["step"],
                data["Infected_mean"],
                label=scenario.label,
                linewidth=2,
            )
        ax.set_title(f"{family.capitalize()} experiment: mean active infections")
        ax.set_xlabel("Simulation step")
        ax.set_ylabel("Mean infected citizens")
        ax.grid(alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_dir / f"{family}_infected_comparison.png", dpi=160)
        plt.close(fig)


def scenario_manifest(scenarios: list[Scenario]) -> pd.DataFrame:
    rows = []
    for scenario in scenarios:
        row = {
            "scenario_id": scenario.scenario_id,
            "family": scenario.family,
            "label": scenario.label,
            "changed_parameters": scenario.changed_parameters,
            "research_question": scenario.research_question,
        }
        row.update(flatten_config(asdict(scenario.config)))
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_scenarios(run_summary: pd.DataFrame) -> pd.DataFrame:
    summary = run_summary.groupby(
        ["scenario_id", "scenario_label", "family"],
        as_index=False,
    ).agg(
        runs=("replicate", "count"),
        mean_steps_completed=("steps_completed", "mean"),
        ended_runs=("epidemic_ended", "sum"),
        mean_peak_infected=("peak_infected", "mean"),
        std_peak_infected=("peak_infected", "std"),
        mean_peak_infected_step=("peak_infected_step", "mean"),
        mean_infected_person_steps=("infected_person_steps", "mean"),
        mean_ever_infected=("ever_infected", "mean"),
        mean_attack_rate_percent=("attack_rate_percent", "mean"),
        std_attack_rate_percent=("attack_rate_percent", "std"),
        mean_final_recovered=("final_recovered", "mean"),
        mean_final_deceased=("final_deceased", "mean"),
        std_final_deceased=("final_deceased", "std"),
        mean_mortality_percent_population=("mortality_percent_population", "mean"),
        mean_final_vaccinated=("final_vaccinated", "mean"),
        runs_with_quarantine=("peak_quarantine_zones", lambda values: int((values > 0).sum())),
        mean_steps_with_quarantine=("steps_with_quarantine", "mean"),
        mean_peak_hospital_patients=("peak_hospital_patients", "mean"),
    )
    return summary.sort_values(["family", "scenario_id"]).reset_index(drop=True)


def write_batch_notes(
    batch_dir: Path,
    scenarios: list[Scenario],
    replicates: int,
    base_seed: int,
) -> None:
    scenario_list = "\n".join(f"- {scenario.scenario_id}: {scenario.label}" for scenario in scenarios)
    note = f"""# Chapter 3 experiment batch

Generated: {datetime.now().isoformat(timespec="seconds")}
Replicates per scenario: {replicates}
Replicate seeds: {base_seed} to {base_seed + replicates - 1}

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

{scenario_list}
"""
    (batch_dir / "README.md").write_text(note, encoding="utf-8")


def run_experiments(args: argparse.Namespace) -> Path:
    scenarios = (
        [SCENARIOS_BY_ID[scenario_id] for scenario_id in args.scenarios]
        if args.scenarios
        else SCENARIOS
    )
    if args.max_steps is not None:
        scenarios = [
            replace(scenario, config=replace(scenario.config, num_steps=args.max_steps))
            for scenario in scenarios
        ]
    output_dirs = create_output_dirs(args.results_dir, args.batch_name)
    scenario_manifest(scenarios).to_csv(
        output_dirs["batch"] / "experiment_manifest.csv",
        index=False,
    )

    all_step_frames = []
    run_summaries = []
    frames_by_scenario = {}

    for scenario in scenarios:
        scenario_raw_dir = output_dirs["raw"] / scenario.scenario_id
        scenario_plot_dir = output_dirs["run_plots"] / scenario.scenario_id
        scenario_raw_dir.mkdir(parents=True, exist_ok=True)
        scenario_plot_dir.mkdir(parents=True, exist_ok=True)
        frames_by_scenario[scenario.scenario_id] = []

        for replicate in range(1, args.replicates + 1):
            seed = args.base_seed + replicate - 1
            print(f"Running {scenario.scenario_id}: replicate {replicate}/{args.replicates}, seed={seed}")
            steps = run_single_simulation(scenario, replicate, seed)
            filename_stem = f"run_{replicate:02d}_seed_{seed}"
            steps.to_csv(scenario_raw_dir / f"{filename_stem}_steps.csv", index=False)
            plot_run_curve(
                steps,
                f"{scenario.label} - run {replicate} (seed {seed})",
                scenario_plot_dir / f"{filename_stem}_curve.png",
            )
            all_step_frames.append(steps)
            frames_by_scenario[scenario.scenario_id].append(steps)
            run_summaries.append(summarize_run(steps, scenario))

    step_results = pd.concat(all_step_frames, ignore_index=True)
    run_summary = pd.DataFrame(run_summaries)
    scenario_summary = summarize_scenarios(run_summary)
    mean_curves = build_scenario_mean_curves(frames_by_scenario, scenarios)

    step_results.to_csv(output_dirs["batch"] / "step_results.csv", index=False)
    run_summary.to_csv(output_dirs["batch"] / "run_summary.csv", index=False)
    scenario_summary.to_csv(output_dirs["batch"] / "scenario_summary.csv", index=False)
    mean_curves.to_csv(output_dirs["batch"] / "scenario_mean_curves.csv", index=False)

    for scenario in scenarios:
        plot_scenario_mean_curve(
            mean_curves,
            scenario,
            output_dirs["scenario_plots"] / f"{scenario.scenario_id}_mean_curve.png",
        )
    plot_family_comparisons(mean_curves, scenarios, output_dirs["comparison_plots"])
    write_batch_notes(output_dirs["batch"], scenarios, args.replicates, args.base_seed)

    print(f"Results written to: {output_dirs['batch']}")
    return output_dirs["batch"]


if __name__ == "__main__":
    run_experiments(parse_args())
