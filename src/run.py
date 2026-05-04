import pandas as pd

from model.disease_model import DiseaseModel
from config import DEFAULT_CONFIG, SimulationConfig
from visualization.plot import plot_epidemic_curve


def run(config: SimulationConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    model = DiseaseModel(config)

    for step in range(config.num_steps):
        model.step()

        infected = model.datacollector.model_vars["Infected"][-1]
        print(f"Step {step + 1:>4}/{config.num_steps} | Infected: {infected}")

        # Stop early if epidemic is over
        exposed = model.datacollector.model_vars["Exposed"][-1]
        if infected == 0 and exposed == 0:
            print(f"Epidemic ended at step {step + 1}.")
            break

    data = model.datacollector.get_model_vars_dataframe()
    return data


if __name__ == "__main__":
    data = run()
    plot_epidemic_curve(data)