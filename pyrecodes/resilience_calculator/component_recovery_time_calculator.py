from pyrecodes.resilience_calculator.resilience_calculator import ResilienceCalculator
from pyrecodes.component.component import Component
from pyrecodes.constants import DAMAGE_LEVEL_TOLERANCE
import math

class ComponentRecoveryTimeCalculator(ResilienceCalculator):
    # It's cleaner to calculate component recovery here than in the Component class.

    def __init__(self, parameters: dict) -> None:
        self.parameters = parameters

    def __str__(self):
        # define what the print() method should return
        output = 'Component Recovery Time Calculator \n'
        output += '-------------------------------- \n'
        for component_recovery_time in self.component_recovery_times:
            output += list(component_recovery_time.keys())[0] + ': ' + str(list(component_recovery_time.values())[0]) + '\n'
        return output

    def calculate_resilience(self):
        self.component_recovery_times = []
        for component_id, component in enumerate(self.system.components):
            self.component_recovery_times.append({component.name + ' | ID: ' + str(component_id): self.get_component_recovery_time(component)})
    
    def get_component_recovery_time(self, component: Component):
        # Component recovery is asumed to finish once the component is repaired and damage is removed.
        # Component may be functional during recovery, depending on the damage to functionality relation.
        if math.isclose(component.get_damage_level(), 0, abs_tol=DAMAGE_LEVEL_TOLERANCE):
            if 'Repair' in component.recovery_model.recovery_activities and len(component.recovery_model.recovery_activities['Repair'].time_steps) > 0:
                return component.recovery_model.recovery_activities['Repair'].time_steps[-1] - self.system.DISASTER_TIME_STEP
            else:
                return 0                
        else:
            return math.inf      

    def update(self, system) -> None:
        self.system = system