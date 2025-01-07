## [v0.2.0] - 2024-12-24

### New Features
- pyrecodes can use exposure and damage information provided by the NHERI R2D Tool as JSON files to simulate regional recovery of buildings, water distribution and transportation systems.
- Water flow in damaged water distribution networks can be simulated using the REWET flow simulator connected to pyrecodes through a novel API based on exchanging JSON files between pyrecodes and REWET during the recovery simulation.
- Traffic flow in damaged road networks can be simulated using residual demand traffic flow simulator connected to pyrecodes through a novel API based on exchanging JSON files between pyrecodes and traffic flow simulator during the recovery simulation.
- Sparse resource distribution time stepping is implemented in case resource distribution models are too computationally demanding. User can specify at which time steps each resource distribution model should be run to conserve computational resources.
- Sparse recovery model time stepping is implemented in case recovery models are too computationally demanding. User can specify time steps at which recovery models of each component should be run to conserve computational resources.
- pyrecodes system can have subsystems defined in different ways: using pyrecodes JSON files, R2D files and pyrecodes supply/demand infrastructure interfaces. 
- Example 5 is introduced to illustrate the use of third-party resource flow simulators through APIs in pyrecodes.

### Bug Fixes
- potential_path_sets are not required if not used by the transportation service distribution model.
- Dependency issues with external libraries are resolved.
- Type hints fixed.

### Improvements
- Comments provided for most classes.
- Code coverage is 86%.

### Breaking Changes
- File and Folder structure is modified compared to 0.1.0 to increase clarity. System creation and import module statements for code compatible with pyrecodes 0.1.0 needs to be updated.
- Structure of input JSON files is modified (system configuration, component library and main). This requires updating input JSON files compatible with pyrecodes 0.1.0. Please consult updated example input files.