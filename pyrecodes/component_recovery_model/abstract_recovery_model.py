from pyrecodes.component_recovery_model.recovery_model import RecoveryModel
from pyrecodes.relation import relation

class AbstractRecoveryModel(RecoveryModel):
    """
    Abstract class using the component recovery model interface.
    """

    parameters = {}

    def __init__(self, recovery_model_parameters: dict) -> None:
        """
        To be implemented in subclasses.
        """
        self.recovery_activities = {}

    def set_parameters(self, parameters: dict) -> None:
        """
        To be implemented in subclasses.
        """
        pass

    def set_initial_damage_level(self, damage_level: float) -> None:
        """
        To be implemented in subclasses.
        """
        pass

    def get_damage_level(self) -> None:
        """
        To be implemented in subclasses.
        """
        pass

    def set_damage_functionality(self, damage_functionality_relation: dict) -> None:
        """
        Set damage functionality relation. This relation is used to get the component's functionality level based on its current damage level.
        If no type is specified, constant relation is used.

        Args:
            damage_functionality_relation (dict): Damage functionality relation parameters.
        """
        damage_functionality_relation_type = damage_functionality_relation.get('Type', 'Constant')
        target_damage_functionality = getattr(relation, damage_functionality_relation_type)
        self.damage_to_functionality_relation = target_damage_functionality()

    def recover(self, time_step: int) -> None:
        """
        To be implemeneted in subclasses.
        """
        pass

    def get_functionality_level(self) -> float:
        """
        Get the functionality level of the component.

        Returns:
            float: The functionality level.
        """
        return self.damage_to_functionality_relation.get_output(self.get_damage_level())

    def get_demand(self) -> dict:
        """
        To be implemented in subclasses.
        """
        pass

    def set_recovery_time_steps(self, time_steps: list) -> None:
        self.recovery_time_steps = time_steps
    
    def get_time_step_length(self, time_step: int) -> int:
        """
        | Get the time steps in the recovery time stepping interval.
        | Explain what exactly is done here once you settle on one of the options.
        """
        # Option 1:
        # return max(time_step - self.recovery_time_steps[max(self.recovery_time_steps.index(time_step)-1, 0)], 1)
        # Option 2:
        # if self.recovery_time_steps.index(time_step) == 0:
        #     return 0, 0
        # else:
        #     start_time_step = self.recovery_time_steps[self.recovery_time_steps.index(time_step)-1] + 1
        #     end_time_step = time_step + 1
        # Option 3:
        if self.recovery_time_steps.index(time_step) == 0:
            return time_step, time_step+1
        else:
            start_time_step = self.recovery_time_steps[self.recovery_time_steps.index(time_step)-1] + 1
            end_time_step = time_step + 1

        return start_time_step, end_time_step
    
    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        """
        To be implemented in subclasses.
        """
        pass

    def set_activities_demand_to_met(self) -> None:
        pass