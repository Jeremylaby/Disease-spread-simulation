from mesa import Agent


class VaccinationPoint(Agent):
    def __init__(self, model, effectiveness: float):
        super().__init__(model)
        self.effectiveness = effectiveness
        self.total_vaccinated = 0

    def step(self):
        from agents.citizen import Citizen, State

        occupants = [
            a for a in self.model.grid.get_cell_list_contents([self.pos])
            if isinstance(a, Citizen)
        ]

        for citizen in occupants:
            if citizen.state == State.SUSCEPTIBLE and not citizen.is_vaccinated:
                citizen.is_vaccinated = True
                self.total_vaccinated += 1

    def __repr__(self):
        return (
            f"VaccinationPoint_{self.unique_id}"
            f"(total_vaccinated={self.total_vaccinated})"
        )
