from pyrecodes.component_recovery_model.component_level_recovery_activities_model import AbstractRecoveryModel

class NoRecoveryActivityModel(AbstractRecoveryModel):
    """
    Recovery model for components that did not experience damage.
    """
    
    def set_initial_damage_level(self, damage_level: float) -> None:
        """
        Set the initial damage level for undamaged components.

        Args:
            damage_level (float): The initial damage level. For this model, it must be 0.

        Raises:
            ValueError: If the damage level is not 0.
        """
        if damage_level != 0:
            raise ValueError('Initial damage level for NoRecoveryActivity model must be 0.')

    def set_damage_functionality(self, damage_functionality_relation: dict) -> None:
        """
        Set damage functionality relation (not applicable for undamaged components).

        Args:
            damage_functionality_relation (dict): Damage functionality relation parameters.
        """
        pass

    def get_functionality_level(self) -> float:
        """
        Get the functionality level of the undamaged component.

        Returns:
            float: The functionality level (always 1.0 for undamaged components).
        """
        return 1.0

    def get_damage_level(self) -> float:
        """
        Get the damage level of the undamaged component.

        Returns:
            float: The damage level (always 0 for undamaged components).
        """
        return 0

    def get_demand(self) -> dict:
        """
        Get the demand for recovery activities for the undamaged component.

        Returns:
            dict: An empty dictionary, as there is no demand for undamaged components.
        """
        return {}    