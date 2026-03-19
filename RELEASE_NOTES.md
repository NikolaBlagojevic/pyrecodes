
# pyrecodes Release Notes

## [v0.3.0] - 2026

### **New Features**

- **Household-Level Recovery Modeling**:
  A new `household` module introduces agent-based household models (`Household` abstract class, `R2DBuildingWithHouseholds` component). Households can make relocation decisions, track displacement, and participate in the regional recovery simulation. The `BuiltEnvironmentWithHouseholds` system class integrates household dynamics into the main simulation loop via an observer pattern.

- **LLM-Driven Household Agents**:
  `HouseholdGPTBase` and `HouseholdGPT` enable GPT- or Llama-backed household agents that make relocation decisions based on damage state, available resources, and social factors. Agents can be informed by academic literature summaries or rule sets prior to simulation. Both synchronous and asynchronous (async) prompting modes are supported.

- **Survey-Based Household Agents**:
  `HouseholdSurveyGPT` allows household relocation decisions to be driven by survey data (US Census Household Pulse Survey), with GPT used to map survey responses to structured decisions.

- **New Recovery Target Checker**:
  A new `RecoveryTargetChecker` abstraction (`NoDamageRecoveryTargetChecker`) makes the condition for ending the simulation explicit and configurable.

- **Observer Pattern in `BuiltEnvironment`**:
  The core simulation loop now supports `register_hook(event, callback)` / `_notify(event)` hooks, allowing subclasses and extensions to inject behavior at each time step without subclassing the main loop.

- **Abstract Marker Classes for Infrastructure Components**:
  `Bridge`, `Roadway`, and `Tunnel` abstract marker classes added to `component.py`. `R2DBridge`, `R2DRoadway`, and `R2DTunnel` now inherit from these, enabling `isinstance`-based type checks throughout the framework.

- **`met_demand_tracker` in Components**:
  Components now track whether their resource demand was met at each time step, enabling finer-grained post-simulation analysis.

- **`main.run()` Accepts Folder Path**:
  The entry-point `run()` function now accepts a folder path in addition to a direct file path, simplifying batch simulation workflows.

- **New Examples (6 and 7)**:
  Example 6 demonstrates LLM-driven household relocation decisions in a small Alameda community, including comparison of GPT responses against baseline, literature-informed, and rule-based strategies. Example 7 covers a multi-system community recovery scenario.

---

### **Improvements**

- Added plotting methods for household spatial data to `ConcretePlotter`.
- Extended `ConcreteGeoVisualizer` with new helper methods for R2D-based visualizations.
- `RandomPriority` rewritten with a single-pass O(n) algorithm (previously O(n²)).
- Observer hooks eliminate the need to override `start_resilience_assessment()` in subclasses.
- Consistent use of `json_deepcopy()` utility across distribution models.

---

### **Bug Fixes**

- Fixed variable shadowing in the recovery activity loop (`current_step` vs. `time_step`).
- Fixed unclosed file handle in `utilities.py` — all JSON reads now use `read_json_file()`.
- Fixed implicit `None` return in `get_step_id()` — now raises `ValueError` on missing step.
- Removed dead commented-out code and unused `reset_suppliers` method from `UtilityDistributionModel`.
- Fixed duplicate `Component` import in `ConcreteGeoVisualizer`.

---

### **Breaking Changes**

- **Locality geometry format**: Locality coordinates must now be specified as `{"Centroid": {"X": ..., "Y": ...}}` instead of flat `{"X": ..., "Y": ...}` dicts in system configuration JSON files.
- **`BuiltEnvironmentWithHouseholds`**: Subclass no longer overrides `start_resilience_assessment()`; household step logic is registered as an observer hook in `create_system()`.
- **`main.run`**: Requires folder and filename as inputs, instead of requiring filename only.

---

## [v0.2.0] - Jan 2025

### **New Features**
- **Integration with NHERI R2D Tool**:  
  Pyrecodes now supports exposure and damage data provided by the NHERI R2D Tool in JSON format, enabling simulations of regional recovery for buildings, water distribution systems, and transportation networks.
  
- **Water Flow Simulation**:  
  Integration with the **REWET water flow simulator** allows simulation of water flow in damaged water distribution networks at each time step of the recovery simulation. The connection is facilitated via a novel API that exchanges JSON files between REWET and pyrecodes during the recovery simulation.

- **Traffic Flow Simulation**:  
  Traffic flow in damaged road networks can now be simulated using the **residual demand traffic flow simulator** at each time step of the recovery simulation, integrated via a JSON-based API similar to REWET.

- **Sparse Resource Distribution Time Stepping**:  
  Users can optimize computational resource usage by specifying time steps at which resource distribution models are executed during the recovery simulation.

- **Sparse Recovery Model Time Stepping**:  
  Recovery models for individual components can be run at user-specified time steps, reducing the computational demand.

- **Flexible Subsystem Definitions**:  
  Subsystems (e.g., power, housing, water distribution) within the same pyrecodes system (e.g., a city)  can now be defined using:
  - Pyrecodes JSON files,  
  - NHERI R2D Tool files, or  
  - Pyrecodes supply/demand infrastructure interfaces.

- **New Example (Example 5)**:  
  Demonstrates the use of third-party resource flow simulators (e.g., REWET) via APIs in pyrecodes.

---

### **Bug Fixes**
- Eliminated the requirement for `potential_path_sets` in transportation service distribution models when unused.  
- Resolved dependency conflicts with external libraries.  
- Fixed inconsistencies in type hints.

---

### **Improvements**
- Added detailed comments for most classes, improving code readability.  
- Increased test coverage to **86%**.

---

### **Breaking Changes**
- **File and Folder Structure**:  
  The overall structure has been updated for clarity. System creation and import statements compatible with v0.1.0 need to be revised to align with v0.2.0.
  
- **JSON Input File Structure**:  
  The formats for system configuration, component libraries, and main input files have been modified. Users must update JSON files created for v0.1.0. Updated example files are available for reference.
