import matplotlib.pyplot as plt
import pandas as pd


def plot_epidemic_curve(data: pd.DataFrame) -> None:
    required_columns = ["Susceptible", "Exposed", "Infected", "Recovered", "Deceased"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        raise ValueError(f"Missing columns for epidemic plot: {missing}")

    plt.figure(figsize=(10, 6))
    for column in required_columns:
        plt.plot(data.index, data[column], label=column, linewidth=2)

    plt.title("Epidemic Curve (SEIRD)")
    plt.xlabel("Step")
    plt.ylabel("Number of agents")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
