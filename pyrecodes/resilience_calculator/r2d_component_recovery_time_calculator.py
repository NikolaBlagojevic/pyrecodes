from pyrecodes.resilience_calculator.component_recovery_time_calculator import ComponentRecoveryTimeCalculator

class R2DComponentRecoveryTimeCalculator(ComponentRecoveryTimeCalculator):

    def calculate_resilience(self):
        self.component_recovery_times = []
        for component in self.system.components:
            self.component_recovery_times.append({component.name + ' | AIM ID: ' + str(getattr(component, 'aim_id', 'None')): self.get_component_recovery_time(component)})