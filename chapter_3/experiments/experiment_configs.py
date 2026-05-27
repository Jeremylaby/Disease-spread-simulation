"""Experimental scenarios for Chapter 3.

Each scenario changes one intervention family relative to the baseline.
The runner uses identical replicate seeds across scenarios, making the
comparisons less sensitive to random initial population placement.
"""

from dataclasses import dataclass, replace

from config import DEFAULT_CONFIG, SimulationConfig


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    family: str
    label: str
    changed_parameters: str
    research_question: str
    config: SimulationConfig


BASE_CONFIG = replace(DEFAULT_CONFIG, num_steps=1_000)

DENSE_VACCINATION_POINTS = [
    (5, 5),
    (5, 15),
    (5, 25),
    (5, 35),
    (5, 45),
    (15, 10),
    (15, 30),
    (25, 5),
    (25, 25),
    (25, 45),
    (35, 10),
    (35, 30),
    (45, 5),
    (45, 15),
    (45, 25),
    (45, 35),
    (45, 45),
]


SCENARIOS = [
    Scenario(
        scenario_id="baseline",
        family="reference",
        label="Baseline",
        changed_parameters="None (default configuration)",
        research_question="What epidemic course is produced by the default model?",
        config=BASE_CONFIG,
    ),
    Scenario(
        scenario_id="transmission_low",
        family="transmission",
        label="Lower transmission",
        changed_parameters="disease.beta=0.15",
        research_question="How does lower transmission probability change the epidemic?",
        config=replace(
            BASE_CONFIG,
            disease=replace(BASE_CONFIG.disease, beta=0.15),
        ),
    ),
    Scenario(
        scenario_id="transmission_high",
        family="transmission",
        label="Higher transmission",
        changed_parameters="disease.beta=0.50",
        research_question="How does higher transmission probability change the epidemic?",
        config=replace(
            BASE_CONFIG,
            disease=replace(BASE_CONFIG.disease, beta=0.50),
        ),
    ),
    Scenario(
        scenario_id="vaccination_none",
        family="vaccination",
        label="No vaccination points",
        changed_parameters="vaccination_point.positions=[]; effectiveness=0.0",
        research_question="How much does access to vaccination limit infections?",
        config=replace(
            BASE_CONFIG,
            vaccination_point=replace(
                BASE_CONFIG.vaccination_point,
                positions=[],
                effectiveness=0.0,
            ),
        ),
    ),
    Scenario(
        scenario_id="vaccination_dense",
        family="vaccination",
        label="Expanded vaccination programme",
        changed_parameters="vaccination_point.positions=17 distributed points; effectiveness=0.90",
        research_question="Can wide access to a highly effective vaccine suppress spread?",
        config=replace(
            BASE_CONFIG,
            vaccination_point=replace(
                BASE_CONFIG.vaccination_point,
                positions=DENSE_VACCINATION_POINTS,
                effectiveness=0.90,
            ),
        ),
    ),
    Scenario(
        scenario_id="hospital_none",
        family="hospital",
        label="No hospital support",
        changed_parameters="hospital.positions=[]; recovery_bonus=0.0",
        research_question="How does hospital support affect outcomes of infected agents?",
        config=replace(
            BASE_CONFIG,
            hospital=replace(
                BASE_CONFIG.hospital,
                positions=[],
                recovery_bonus=0.0,
            ),
        ),
    ),
    Scenario(
        scenario_id="hospital_expanded",
        family="hospital",
        label="Expanded hospital coverage",
        changed_parameters="hospital.positions=[(12,12),(25,25),(38,38)]; area_radius=4; capacity=100; recovery_bonus=0.10",
        research_question="Does increased treatment coverage improve recovery and mortality outcomes?",
        config=replace(
            BASE_CONFIG,
            hospital=replace(
                BASE_CONFIG.hospital,
                positions=[(12, 12), (25, 25), (38, 38)],
                area_radius=4,
                capacity=100,
                recovery_bonus=0.10,
            ),
        ),
    ),
    Scenario(
        scenario_id="avoidance_none",
        family="behavior",
        label="No avoidance behavior",
        changed_parameters="behavior.avoidance_fraction=0.0",
        research_question="Does voluntary avoidance of infected neighbors slow spread?",
        config=replace(
            BASE_CONFIG,
            behavior=replace(BASE_CONFIG.behavior, avoidance_fraction=0.0),
        ),
    ),
    Scenario(
        scenario_id="avoidance_high",
        family="behavior",
        label="High avoidance behavior",
        changed_parameters="behavior.avoidance_fraction=0.80",
        research_question="What happens when most citizens avoid infected neighbors?",
        config=replace(
            BASE_CONFIG,
            behavior=replace(BASE_CONFIG.behavior, avoidance_fraction=0.80),
        ),
    ),
    Scenario(
        scenario_id="quarantine_disabled",
        family="quarantine",
        label="Quarantine disabled",
        changed_parameters="quarantine.threshold=501",
        research_question="Does an early movement restriction influence epidemic spread?",
        config=replace(
            BASE_CONFIG,
            quarantine=replace(BASE_CONFIG.quarantine, threshold=501),
        ),
    ),
    Scenario(
        scenario_id="quarantine_early",
        family="quarantine",
        label="Early quarantine activation",
        changed_parameters="quarantine.threshold=20; zone_radius=5",
        research_question="Does an early movement restriction influence epidemic spread?",
        config=replace(
            BASE_CONFIG,
            quarantine=replace(BASE_CONFIG.quarantine, threshold=20, zone_radius=5),
        ),
    ),
]


SCENARIOS_BY_ID = {scenario.scenario_id: scenario for scenario in SCENARIOS}
