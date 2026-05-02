# Disease Spread Simulation

Agent-based epidemic simulation using Mesa (Python).

## Model overview

SEIRD model on a spatial grid with heterogeneous agents and environment objects.

## Agents

### Citizen

- States: susceptible, exposed (incubation), infected, recovered, deceased
- Attributes: age, position, vaccination status
- Infection probability depends on number of infected neighbors: P = 1 - (1-p)^k
- Mortality rate scales with age
- Recovery chance per step: base gamma, increased when in hospital
- Vaccinated agents have reduced infection probability by a configurable factor
- Healthy agents avoid visibly infected neighbors (configurable % of population)
- Younger agents move more, older agents move less
- Recovered agents lose immunity after X steps (configurable, 0 = permanent)

### Hospital

- Fixed position on grid
- Increases recovery rate of infected agents within its area
- Limited capacity - no bonus when full

### Vaccination Point

- Fixed position on grid
- Susceptible agents entering its area become vaccinated
- Reduces infection probability by a configurable parameter

## Global mechanics

- Quarantine zone: when infection count exceeds threshold, regions of the map become restricted
- Epidemic curve emerges from local interactions, not computed from equations

## Parameters

- Population size, grid dimensions
- beta (transmission rate per contact), gamma (base recovery rate)
- Incubation period (steps), mortality rate (base + age modifier)
- Hospital capacity, hospital recovery bonus
- Vaccination effectiveness (infection probability reduction)
- Avoidance behavior (% of population that avoids infected)
- Immunity duration (0 = permanent)
- Quarantine threshold

## Usefull links:

- https://ccl.northwestern.edu/netlogo/ egzaple of agents models
- https://mesa.readthedocs.io/latest/
- https://simpy.readthedocs.org/en/latest/
- https://github.com/pygame/pygame
- https://cs.gmu.edu/~eclab/projects/mason/
- https://github.com/DEAP/deap
- https://neat-python.readthedocs.io/en/latest/
- https://jenetics.io
- https://github.com/scikit-learn/scikit-learn
- https://www.tensorflow.org/
- https://keras.io/
- https://pytorch.org/
- https://www.r-project.org/
