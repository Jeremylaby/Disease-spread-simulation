import argparse
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle

from agents.citizen import Citizen, State
from agents.hospital import Hospital
from agents.vaccination_point import VaccinationPoint
from config import DEFAULT_CONFIG, SimulationConfig
from model.disease_model import DiseaseModel


STATE_ORDER = [
    State.SUSCEPTIBLE,
    State.EXPOSED,
    State.INFECTED,
    State.RECOVERED,
    State.DECEASED,
]

STATE_LABELS = {
    State.SUSCEPTIBLE: "Susceptible",
    State.EXPOSED: "Exposed",
    State.INFECTED: "Infected",
    State.RECOVERED: "Recovered",
    State.DECEASED: "Deceased",
}

STATE_COLORS = {
    State.SUSCEPTIBLE: "#1f77b4",
    State.EXPOSED: "#ff7f0e",
    State.INFECTED: "#2ca02c",
    State.RECOVERED: "#d62728",
    State.DECEASED: "#9467bd",
}

JITTER_OFFSETS = [
    (0.00, 0.00),
    (0.18, 0.00),
    (-0.18, 0.00),
    (0.00, 0.18),
    (0.00, -0.18),
    (0.13, 0.13),
    (-0.13, 0.13),
    (0.13, -0.13),
    (-0.13, -0.13),
]


@dataclass(frozen=True)
class CitizenSnapshot:
    x: float
    y: float
    state: State
    is_vaccinated: bool


@dataclass(frozen=True)
class HospitalSnapshot:
    x: float
    y: float
    area_radius: int
    current_patients: int
    capacity: int


@dataclass(frozen=True)
class VaccinationPointSnapshot:
    x: float
    y: float
    total_vaccinated: int


@dataclass(frozen=True)
class ModelSnapshot:
    step: int
    citizens: tuple[CitizenSnapshot, ...]
    hospitals: tuple[HospitalSnapshot, ...]
    vaccination_points: tuple[VaccinationPointSnapshot, ...]
    quarantine_zones: tuple[tuple[float, float], ...]
    counts: dict[State, int]
    vaccinated_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Live grid visualization for the disease spread simulation."
    )
    parser.add_argument(
        "frame_delay",
        nargs="?",
        default=50,
        type=int,
        help="Delay between frames in hundredths of a second. Example: 50 = 0.5 s.",
    )
    args = parser.parse_args()

    if args.frame_delay <= 0:
        parser.error("frame_delay must be a positive integer, for example 50.")

    return args


def take_snapshot(model: DiseaseModel) -> ModelSnapshot:
    counts = {state: 0 for state in STATE_ORDER}
    citizens = []
    vaccinated_count = 0
    cell_occupancy: dict[tuple[int, int], int] = {}

    for agent in model.agents:
        if not isinstance(agent, Citizen):
            continue

        counts[agent.state] += 1

        if agent.is_vaccinated:
            vaccinated_count += 1

        if agent.pos is None:
            continue

        x, y = agent.pos
        occupancy_index = cell_occupancy.get((x, y), 0)
        cell_occupancy[(x, y)] = occupancy_index + 1
        jitter_x, jitter_y = JITTER_OFFSETS[occupancy_index % len(JITTER_OFFSETS)]

        citizens.append(
            CitizenSnapshot(
                x=x + jitter_x,
                y=y + jitter_y,
                state=agent.state,
                is_vaccinated=agent.is_vaccinated,
            )
        )

    hospitals = tuple(
        HospitalSnapshot(
            x=hospital.pos[0],
            y=hospital.pos[1],
            area_radius=hospital.area_radius,
            current_patients=hospital.current_patients,
            capacity=hospital.capacity,
        )
        for hospital in model.hospitals
        if hospital.pos is not None
    )

    vaccination_points = tuple(
        VaccinationPointSnapshot(
            x=point.pos[0],
            y=point.pos[1],
            total_vaccinated=point.total_vaccinated,
        )
        for point in model.vaccination_points
        if point.pos is not None
    )

    return ModelSnapshot(
        step=model.current_step,
        citizens=tuple(citizens),
        hospitals=hospitals,
        vaccination_points=vaccination_points,
        quarantine_zones=tuple(model.quarantine_zones),
        counts=counts,
        vaccinated_count=vaccinated_count,
    )


def advance_and_snapshot(model: DiseaseModel) -> ModelSnapshot:
    model.step()
    return take_snapshot(model)


class LiveVisualizer:
    def __init__(self, config: SimulationConfig, frame_delay_seconds: float):
        self.config = config
        self.frame_delay_seconds = frame_delay_seconds

        plt.ion()
        self.fig, (self.ax, self.side_ax) = plt.subplots(
            1,
            2,
            figsize=(13, 8),
            gridspec_kw={"width_ratios": [4.8, 1.6]},
        )
        self.fig.canvas.manager.set_window_title("Disease Spread Simulation - Live")

    def draw(self, snapshot: ModelSnapshot, status: str = "Running") -> None:
        self.ax.clear()
        self.side_ax.clear()
        self.side_ax.axis("off")

        self._draw_grid()
        self._draw_quarantine_zones(snapshot)
        self._draw_hospitals(snapshot)
        self._draw_vaccination_points(snapshot)
        self._draw_citizens(snapshot)
        self._draw_side_panel(snapshot, status)

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def _draw_grid(self) -> None:
        width = self.config.grid.width
        height = self.config.grid.height

        self.ax.set_xlim(-0.5, width - 0.5)
        self.ax.set_ylim(-0.5, height - 0.5)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_title("Disease spread live grid")

        major_x_ticks = range(0, width + 1, 5)
        major_y_ticks = range(0, height + 1, 5)
        self.ax.set_xticks(major_x_ticks)
        self.ax.set_yticks(major_y_ticks)
        self.ax.grid(color="#d0d0d0", linewidth=0.6, alpha=0.55)

    def _draw_quarantine_zones(self, snapshot: ModelSnapshot) -> None:
        radius = self.config.quarantine.zone_radius
        for x, y in snapshot.quarantine_zones:
            zone = Circle(
                (x, y),
                radius,
                facecolor="#f39c12",
                edgecolor="#d35400",
                linewidth=0.9,
                alpha=0.12,
                zorder=1,
            )
            self.ax.add_patch(zone)

    def _draw_hospitals(self, snapshot: ModelSnapshot) -> None:
        for hospital in snapshot.hospitals:
            area = Circle(
                (hospital.x, hospital.y),
                hospital.area_radius,
                facecolor="#e74c3c",
                edgecolor="#c0392b",
                linewidth=1.2,
                alpha=0.12,
                zorder=2,
            )
            self.ax.add_patch(area)
            self.ax.scatter(
                [hospital.x],
                [hospital.y],
                marker="P",
                s=230,
                c="#c0392b",
                edgecolors="#111111",
                linewidths=1.0,
                zorder=5,
            )
            self.ax.text(
                hospital.x + 0.6,
                hospital.y + 0.6,
                f"H {hospital.current_patients}/{hospital.capacity}",
                fontsize=8,
                color="#7f1d1d",
                zorder=6,
            )

    def _draw_vaccination_points(self, snapshot: ModelSnapshot) -> None:
        for point in snapshot.vaccination_points:
            self.ax.scatter(
                [point.x],
                [point.y],
                marker="X",
                s=170,
                c="#17becf",
                edgecolors="#111111",
                linewidths=1.0,
                zorder=5,
            )
            self.ax.text(
                point.x + 0.6,
                point.y + 0.6,
                f"V {point.total_vaccinated}",
                fontsize=8,
                color="#075985",
                zorder=6,
            )

    def _draw_citizens(self, snapshot: ModelSnapshot) -> None:
        by_state = {state: [] for state in STATE_ORDER}
        vaccinated_positions = []

        for citizen in snapshot.citizens:
            by_state[citizen.state].append((citizen.x, citizen.y))
            if citizen.is_vaccinated:
                vaccinated_positions.append((citizen.x, citizen.y))

        for state in STATE_ORDER:
            positions = by_state[state]
            if not positions:
                continue
            xs, ys = zip(*positions)
            self.ax.scatter(
                xs,
                ys,
                s=24,
                c=STATE_COLORS[state],
                edgecolors="none",
                alpha=0.86,
                zorder=4,
            )

        if vaccinated_positions:
            xs, ys = zip(*vaccinated_positions)
            self.ax.scatter(
                xs,
                ys,
                s=42,
                facecolors="none",
                edgecolors="#111827",
                linewidths=0.7,
                zorder=4.5,
            )

    def _draw_side_panel(self, snapshot: ModelSnapshot, status: str) -> None:
        handles = [
            Line2D(
                [0],
                [0],
                marker="o",
                linestyle="",
                markerfacecolor=STATE_COLORS[state],
                markeredgecolor="none",
                markersize=8,
                label=STATE_LABELS[state],
            )
            for state in STATE_ORDER
        ]
        handles.extend(
            [
                Line2D(
                    [0],
                    [0],
                    marker="P",
                    linestyle="",
                    markerfacecolor="#c0392b",
                    markeredgecolor="#111111",
                    markersize=10,
                    label="Hospital",
                ),
                Line2D(
                    [0],
                    [0],
                    marker="X",
                    linestyle="",
                    markerfacecolor="#17becf",
                    markeredgecolor="#111111",
                    markersize=9,
                    label="Vaccination point",
                ),
                Line2D(
                    [0],
                    [0],
                    marker="o",
                    linestyle="",
                    markerfacecolor="none",
                    markeredgecolor="#111827",
                    markersize=9,
                    label="Vaccinated outline",
                ),
            ]
        )

        self.side_ax.legend(handles=handles, loc="upper left", frameon=True)

        counts_text = "\n".join(
            [
                f"Status: {status}",
                f"Step: {snapshot.step}/{self.config.num_steps}",
                f"Frame delay: {self.frame_delay_seconds:.2f}s",
                "",
                f"S: {snapshot.counts[State.SUSCEPTIBLE]}",
                f"E: {snapshot.counts[State.EXPOSED]}",
                f"I: {snapshot.counts[State.INFECTED]}",
                f"R: {snapshot.counts[State.RECOVERED]}",
                f"D: {snapshot.counts[State.DECEASED]}",
                "",
                f"Vaccinated: {snapshot.vaccinated_count}",
                f"Quarantine zones: {len(snapshot.quarantine_zones)}",
            ]
        )
        self.side_ax.text(
            0.02,
            0.47,
            counts_text,
            transform=self.side_ax.transAxes,
            va="top",
            ha="left",
            fontsize=10,
            family="monospace",
        )


def should_stop(snapshot: ModelSnapshot, config: SimulationConfig) -> bool:
    if snapshot.step >= config.num_steps:
        return True

    return (
        snapshot.counts[State.INFECTED] == 0
        and snapshot.counts[State.EXPOSED] == 0
    )


def wait_for_next_frame(
    visualizer: LiveVisualizer,
    future: Future,
    frame_delay_seconds: float,
) -> bool:
    deadline = time.perf_counter() + frame_delay_seconds

    while plt.fignum_exists(visualizer.fig.number):
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            break
        plt.pause(min(0.05, remaining))

    while plt.fignum_exists(visualizer.fig.number) and not future.done():
        plt.pause(0.01)

    return plt.fignum_exists(visualizer.fig.number)


def keep_window_open(visualizer: LiveVisualizer) -> None:
    while plt.fignum_exists(visualizer.fig.number):
        plt.pause(0.1)


def run_live(
    frame_delay_hundredths: int,
    config: SimulationConfig = DEFAULT_CONFIG,
) -> None:
    frame_delay_seconds = frame_delay_hundredths / 100.0
    model = DiseaseModel(config)
    visualizer = LiveVisualizer(config, frame_delay_seconds)
    snapshot = take_snapshot(model)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(advance_and_snapshot, model)
        visualizer.draw(snapshot)

        while plt.fignum_exists(visualizer.fig.number):
            if not wait_for_next_frame(visualizer, future, frame_delay_seconds):
                break

            snapshot = future.result()
            finished = should_stop(snapshot, config)
            visualizer.draw(snapshot, status="Finished" if finished else "Running")

            if finished:
                keep_window_open(visualizer)
                break

            future = executor.submit(advance_and_snapshot, model)


if __name__ == "__main__":
    parsed_args = parse_args()
    run_live(parsed_args.frame_delay)
