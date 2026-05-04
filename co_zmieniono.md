# Co zmieniono, żeby projekt działał

Poniżej jest pełna lista zmian wykonanych w repozytorium, które były potrzebne, żeby `python run.py` działało poprawnie.

## 1. Naprawa kodowania plików Python (UTF-16 -> UTF-8)

Problem:
- wiele plików `.py` było zapisanych w UTF-16 LE (`FF FE`), co powodowało błędy `SyntaxError` / `unicode error` przy imporcie.

Zmiana:
- pliki `.py` w `src/` zostały przekonwertowane do UTF-8 (bez BOM).

Efekt:
- Python przestał wywalać się na starcie importów.

## 2. Naprawa modułu wykresu

Problem:
- `src/visualization/plot.py` zawierał złą treść (duplikat logiki z `run.py`), przez co brakowało funkcji `plot_epidemic_curve`.

Zmiana:
- odtworzona funkcja `plot_epidemic_curve(data: pd.DataFrame)` w `src/visualization/plot.py`:
  - waliduje wymagane kolumny (`Susceptible`, `Exposed`, `Infected`, `Recovered`, `Deceased`),
  - rysuje krzywe SEIRD przez `matplotlib`.

Efekt:
- import `from visualization.plot import plot_epidemic_curve` działa,
- wykres generuje się poprawnie.

## 3. Naprawa literówki w nazwie pliku agenta szczepień

Problem:
- plik miał nazwę `vacination_point.py` (literówka), a import oczekiwał `vaccination_point.py`.

Zmiana:
- zmiana nazwy pliku:
  - z `src/agents/vacination_point.py`
  - na `src/agents/vaccination_point.py`

Efekt:
- import `from agents.vaccination_point import VaccinationPoint` działa.

## 4. Dostosowanie kodu do Mesa 3.5.1 (zmiany API)

Problem:
- kod używał starego schedulera `RandomActivation`, który nie jest dostępny w `Mesa==3.5.1`.
- konstruktory agentów były napisane pod stare API (`super().__init__(unique_id, model)`).

Zmiany:
- `src/model/disease_model.py`:
  - usunięty import `RandomActivation`,
  - `super().__init__(rng=config.seed)` zamiast starej inicjalizacji,
  - usunięte `self.schedule = RandomActivation(self)` oraz `self.schedule.add(...)`,
  - krok modelu działa teraz przez `self.agents.shuffle_do("step")`,
  - iteracje i zliczanie agentów przeniesione z `self.schedule.agents` na `self.agents`.
- `src/agents/citizen.py`:
  - konstruktor zmieniony na `def __init__(self, model, ...)`,
  - `super().__init__(model)`.
- `src/agents/hospital.py`:
  - konstruktor zmieniony na `def __init__(self, model, ...)`,
  - `super().__init__(model)`,
  - zliczanie pacjentów po `self.model.agents`.
- `src/agents/vaccination_point.py`:
  - konstruktor zmieniony na `def __init__(self, model, ...)`,
  - `super().__init__(model)`.

Efekt:
- model uruchamia się na aktualnym Mesa 3.5.1.

## 5. Naprawa błędnego odwołania do konfiguracji

Problem:
- w modelu było `self.config.disease.initial_infected_count`, ale ten parametr jest w `PopulationConfig`.

Zmiana:
- w `src/model/disease_model.py` poprawione na:
  - `self.config.population.initial_infected_count`

Efekt:
- zniknął błąd `AttributeError: 'DiseaseConfig' object has no attribute 'initial_infected_count'`.

## 6. Status po zmianach

- Symulacja przechodzi pełny przebieg i generuje wykres.
- Nie były robione żadne commity do git.

## Zmienione pliki

- `src/run.py` (kodowanie UTF-8)
- `src/config.py` (kodowanie UTF-8)
- `src/model/__init__.py` (kodowanie UTF-8)
- `src/model/disease_model.py`
- `src/agents/__init__.py` (kodowanie UTF-8)
- `src/agents/citizen.py`
- `src/agents/hospital.py`
- `src/agents/vaccination_point.py` (rename + kod)
- `src/visualization/__init__.py` (kodowanie UTF-8)
- `src/visualization/plot.py`
