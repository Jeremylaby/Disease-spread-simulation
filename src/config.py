from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class GridConfig:
    width: int = 50
    height: int = 50


@dataclass
class PopulationConfig:
    num_citizens: int = 500
    # Age brackets (min, max) and their probabilities
    age_brackets: List[Tuple[int, int]] = field(default_factory=lambda: [
        (0, 17),
        (18, 44),
        (45, 64),
        (65, 100),
    ])
    age_bracket_weights: List[float] = field(default_factory=lambda: [0.18, 0.37, 0.26, 0.19])
    initial_infected_count: int = 5


@dataclass
class DiseaseConfig:
    beta: float = 0.3
    gamma: float = 0.05
    incubation_period: int = 5

    mortality_base: float = 0.01
    # Added to mortality per year of age above 60
    age_mortality_modifier: float = 0.001

    # 0 = permanent immunity after recovery
    immunity_duration: int = 0


@dataclass
class HospitalConfig:
    capacity: int = 50
    recovery_bonus: float = 0.05
    # Radius of cells around hospital center that count as "inside"
    area_radius: int = 3
    # (x, y) center positions on the grid
    positions: List[Tuple[int, int]] = field(default_factory=lambda: [(25, 25)])


@dataclass
class VaccinationPointConfig:
    effectiveness: float = 0.7
    positions: List[Tuple[int, int]] = field(default_factory=lambda: [(10, 10), (40, 40)])


@dataclass
class BehaviorConfig:
    # Fraction of population that actively avoids visibly infected neighbors
    avoidance_fraction: float = 0.3

    # Agents above this age get reduced movement
    age_mobility_threshold: int = 60
    elderly_move_probability: float = 0.4

    # Infected agents within this radius will move toward nearest hospital
    hospital_seek_radius: int = 15


@dataclass
class QuarantineConfig:
    # Infection count that triggers quarantine zone activation
    threshold: int = 100
    # Radius of restricted zone in grid cells
    zone_radius: int = 5


@dataclass
class SimulationConfig:
    grid: GridConfig = field(default_factory=GridConfig)
    population: PopulationConfig = field(default_factory=PopulationConfig)
    disease: DiseaseConfig = field(default_factory=DiseaseConfig)
    hospital: HospitalConfig = field(default_factory=HospitalConfig)
    vaccination_point: VaccinationPointConfig = field(default_factory=VaccinationPointConfig)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    quarantine: QuarantineConfig = field(default_factory=QuarantineConfig)

    num_steps: int = 1_000
    seed: int = 42


DEFAULT_CONFIG = SimulationConfig()