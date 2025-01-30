
# pyrecodes Release Notes

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
