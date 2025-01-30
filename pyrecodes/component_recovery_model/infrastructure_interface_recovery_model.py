from pyrecodes.component_recovery_model.abstract_recovery_model import AbstractRecoveryModel
from pyrecodes.component_recovery_model.concrete_recovery_activity import ConcreteRecoveryActivity
from pyrecodes.relation import relation

class InfrastructureInterfaceRecoveryModel(AbstractRecoveryModel):
    """
    Component recovery model for infrastructure interfaces to simulate their pre-defined post-disaster supply/demand dynamics.
    """    

    RECOVERY_ACTIVITY_NAME = 'Recovery'
    
    def __init__(self, recovery_model_parameters: dict) -> None: 
        """
        Constructor for InfrastructureInterfaceRecoveryModel. Model has a single recovery activity, whose name is defined in the RECOVERY_ACTIVITY_NAME attribute.

        Args:
            recovery_model_parameters (dict): Parameters for the recovery model.
        """       
        self.recovery_activities = {self.RECOVERY_ACTIVITY_NAME: ConcreteRecoveryActivity(self.RECOVERY_ACTIVITY_NAME, initial_level=1.0)}
        self.set_damage_functionality()
        self.set_parameters(recovery_model_parameters['Parameters'])        
    
    def set_parameters(self, parameters: dict, default_duration=0) -> None:
        """
        Set model parameters. These include setting the post-disaster functionality levels and the time steps at which they change as multiple steps to achieve the predefined supply/demand dynamics as set in the system configuration file.

        Args:
            parameters (dict): Parameters for the recovery model.
            default_duration (list, optional): Default duration for recovery activities (default is zero).

        Notes:
            - This method sets step durations and demands for the recovery activity.
            - RestoredIn is the time it takes for the infrastructure interface to be restored to full functionality. It is sampled before passed to this method. That's why it's a deterministic value here.
            - The implementation should be improved in the future.

        TODO:
            - Improve the method. See if StepLimits are redundant as RestoredIn is already defined.
        """
        self.damage_to_functionality_relation.set_steps(parameters.get('StepLimits', []), parameters.get('StepValues', []))       
        self.recovery_activities[self.RECOVERY_ACTIVITY_NAME].set_duration({"Deterministic": {"Value": parameters.get('RestoredIn', default_duration)}})
        self.recovery_activities[self.RECOVERY_ACTIVITY_NAME].set_demand('')  

    def set_initial_damage_level(self, damage_level: float) -> None:
        """
        Set the initial damage level for infrastructure interfaces. The damage level is always 1 to triger the pre-defined supply/demand dynamics.

        Args:
            damage_level (float): The initial damage level. For this model, it must be 1.

        Notes:
            - This method sets both the damage level and the initial state of the recovery activity.
        """
        self.damage_level = 1.0
        self.recovery_activities[self.RECOVERY_ACTIVITY_NAME].level = 0.0

    def set_damage_functionality(self) -> None:
        """
        Set damage functionality relation. For this model it's always a multiple step relation.
        """
        target_damage_functionality = getattr(relation, 'MultipleStep')
        self.damage_to_functionality_relation = target_damage_functionality()

    def set_activities_demand_to_met(self) -> None:
        pass

    def recover(self, time_step: int) -> None:
        """
        | Perform recovery for a time step. Recovery here means simulating the pre-defined post-disaster supply/demand dynamics.
        | Recovery happens at each time step. Recovery time steps are not considered for Infrastructure Interfaces as the supply/dynamic is predefined.
        Args:
            time_step (int): The time step for which recovery is performed.
        """
        
        self.recovery_activities[self.RECOVERY_ACTIVITY_NAME].recover(time_step)
    
    def get_damage_level(self) -> float:
        """
        Get the damage level of the infrastructure interface.

        Returns:
            float: The damage level.
        """
        return 1 - self.recovery_activities[self.RECOVERY_ACTIVITY_NAME].level

    def get_functionality_level(self) -> float:
        """
        Get the functionality level of the infrastructure interface.

        Note: input to the damage functionality relation is 1 - damage level due to the way in which the Multistep Relation is defined.

        Returns:
            float: The functionality level.
        """
        return self.damage_to_functionality_relation.get_output(1 - self.get_damage_level())
    
    def get_demand(self) -> dict:
        """
        Get the demand for the infrastructure interface.

        Returns:
            dict: An empty dictionary, as it assumed that there is no recovery demand for infrastructure interfaces.
        """
        return {}