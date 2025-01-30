from pyrecodes.resilience_calculator.resilience_calculator import ResilienceCalculator

class FullRecoveryTimeCalculator(ResilienceCalculator):
    """
    Resilience calculator class that calculates the recovery time for the system defined as the time at which all components are damage-free.
    """

    def __init__(self) -> None:
        self.current_recovery_time = None

    def __str__(self):
        if self.current_recovery_time is None:
            return 'Full Recovery Time Resilience Calculator \n' + 'Recovery time: ' + 'Not yet recovered.' + '\n'
        else:
            return 'Full Recovery Time Resilience Calculator \n' + 'Recovery time: ' + str(self.current_recovery_time) + '\n'

    def calculate_resilience(self):
        return self.current_recovery_time

    def update(self, system) -> None:
        for component in system.components:
            if component.get_damage_level() > 0:
                self.current_recovery_time = None
                break
        else:
            # This condition prevents the recovery time to be smaller than the disaster time step and to be equal to the first time step at which all components are damage-free.
            if system.time_step > system.DISASTER_TIME_STEP and self.current_recovery_time == None:
                self.current_recovery_time = system.time_step