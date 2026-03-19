# CLAUDE.md — pyrecodes

## Project Overview

**pyrecodes** is a Python framework for regional recovery simulation and resilience assessment of the built environment, based on the iRe-CoDeS (integrated Recovery Computational Design System) framework. It simulates how communities and infrastructure systems recover after disasters by modeling component damage, resource distribution, and recovery activities over time.

**Version:** 0.3.0 (in development) | **Python:** ≥3.9

## Architecture

The codebase follows a **plugin/strategy pattern** with abstract base classes and concrete implementations. Nearly everything is instantiated dynamically from JSON configuration via `utilities.get_class(module_name, class_name, folder_name)`, which uses `importlib` to load `pyrecodes.<folder>.<module>`.

**Core simulation loop** (in `BuiltEnvironment.start_resilience_assessment()`):
1. Initialize component damage
2. For each time step:
   - Distribute resources across components
   - Update component recovery activities
   - Calculate resilience metrics
3. Save/visualize results

**Key abstractions:**
- `System` → `BuiltEnvironment` (and `BuiltEnvironmentWithHouseholds`)
- `Component` → `StandardiReCoDeSComponent`, `R2DComponent`, `R2DBuildingWithHouseholds`
- `RecoveryModel` → `ComponentLevelRecoveryActivitiesModel`
- `ResourceDistributionModel` → `UtilityDistributionModel`, `HousingDistributionModel`, `REWETDistributionModel`, `ResidualDemandTrafficDistributionModel`, `AccessToCommoditiesDistributionModel`, `BridgeServiceDistributionModel`
- `DamageInput` → `ListDamageInput`, `R2DDamageInput`

**Entry point:** `main.py` — `run()`, `create_system()`, `form_component_library()`, `load_system()`

## Directory Structure

```
pyrecodes/                   # Main package
├── component/               # Component definitions
├── component_configurator/  # Configures components from JSON
├── component_library_creator/
├── component_recovery_model/
├── damage_input/
├── distribution_priority/
├── geovisualizer/
├── household/               # Household-level models (new in v0.2)
├── plotter/
├── probability_distribution/
├── relation/                # Damage-functionality mathematical relations
├── resilience_calculator/
├── resource/
├── resource_distribution_model/
├── subsystem_creator/
├── system/
├── system_creator/
├── main.py
├── utilities.py
├── constants.py
tests/                       # pytest test suite (~530 tests, 86% coverage)
├── test_inputs/             # Complete JSON configs for test systems
"Example 1-6"/               # Example notebooks and input files
```

## Key Files

- `pyrecodes/main.py` — Entry point
- `pyrecodes/utilities.py` — `get_class()` dynamic loader, JSON readers, geometry helpers
- `pyrecodes/constants.py` — Global constants (time step = 3600s, damage states, colors)
- `tests/test_inputs/` — Reference JSON configurations for understanding system structure

## Running Tests

```bash
pytest tests/                                        # all tests
pytest tests/test_system/test_built_environment.py  # specific file
pytest -v                                            # verbose
```

## Code Conventions

- **Naming:** `snake_case` functions/variables, `PascalCase` classes, `UPPER_CASE` constants
- **Type hints:** Used extensively
- **Docstrings:** Google-style
- **Config:** All external configuration via JSON; avoid hardcoding values

### Style Rules (strictly enforced)

- **Short methods:** Every method should do one thing. If a method is getting long, extract helpers.
- **Short classes:** Classes should have a single, clear responsibility. Split large classes.
- **No duplication:** Before writing a method or class, check if similar logic already exists. Reuse or generalize — never copy-paste.
- **Readable code:** Prefer clarity over cleverness. Variable and method names should make the intent obvious without needing a comment.

### Testing Rules

- Write **pytest** unit tests for every new method and class.
- Cover **all edge cases**: empty inputs, boundary values, invalid types, unexpected states.
- Tests live in `tests/` mirroring the package structure (e.g. `pyrecodes/foo/bar.py` → `tests/test_foo/test_bar.py`).
- Each test function tests one behavior. Use descriptive names: `test_<method>_<scenario>`.

## Key Concepts for Working with This Codebase

1. **JSON-driven configuration** — Most issues stem from JSON config; understand the structure first. Fields `FileName` and `ClassName` map to the module/class loaded via `get_class()`.

2. **Resource supply/demand** — Components have supply resources they provide and demand resources they need. Relations (Linear, Constant, Binary, MultipleStep) map damage/functionality to supply/demand values.

3. **Damage → Functionality → Recovery chain** — Damage sets initial functionality via a relation; recovery activities restore damage over time; resource supply/demand creates feedback loops.

4. **Third-party integrators** — REWET (water network) and residual demand traffic simulator communicate via JSON file APIs during time steps.

5. **Sparse time stepping** — Resource distribution and recovery models can run on non-uniform time steps for performance.

6. **Household models** — New in v0.2; `R2DBuildingWithHouseholds` and `AccessToCommoditiesDistributionModel` support household-level recovery tracking.

## Dependencies

Core: `pandas`, `numpy`, `geopandas`, `shapely`, `matplotlib`, `scipy`, `networkx`, `openpyxl`

Optional (third-party simulators): `rewet`, `wntrfr`, `pandana`

Install: `pip install -e .` or `pip install -e ".[third_party_models]"`
