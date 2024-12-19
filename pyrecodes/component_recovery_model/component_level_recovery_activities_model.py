from pyrecodes.component_recovery_model.abstract_recovery_model import AbstractRecoveryModel
from pyrecodes.component_recovery_model.concrete_recovery_activity import ConcreteRecoveryActivity
from pyrecodes.component_recovery_model.recovery_activity import RecoveryActivity
from pyrecodes.relation import relation

class ComponentLevelRecoveryActivitiesModel(AbstractRecoveryModel):
    """
    Component recovery model that considers multiple recovery activities defined on a component level.
    
    This model accounts for several impeding factors and a single repair activity.

    Attributes:
        damage_level (float): The damage level of the component (between 0 and 1).
        damage_to_functionality_relation (relation.Relation): The relation to get the functionality level based on the current damage level.
        recovery_activities (dict): A dictionary of recovery activities parameters.
        REPAIR_ACTIVITY_NAME (str): The name of the repair activity - one that actually reduces the damage level.
    """

    damage_level: float
    damage_to_functionality_relation: relation.Relation
    recovery_activities: dict

    def __init__(self, recovery_model_parameters: dict, REPAIR_ACTIVITY_NAME = 'Repair') -> None:
        """
        Constructor for ComponentLevelRecoveryActivitiesModel.

        Args:
            recovery_model_parameters (dict): Parameters for the recovery model.
            REPAIR_ACTIVITY_NAME (str, optional): The name of the repair activity (default is 'Repair').
        """
        self.recovery_activities = {}
        self.REPAIR_ACTIVITY_NAME = REPAIR_ACTIVITY_NAME
        self.set_parameters(recovery_model_parameters['Parameters'])
        self.set_damage_functionality(recovery_model_parameters['DamageFunctionalityRelation'])        

    def set_parameters(self, parameters: dict) -> None:
        """
        Set parameters for all recovery activities. Parameters are preceding activities, duration, and demand of activities.

        Args:
            parameters (dict): Parameters for the recovery model.
        """
        self.parameters = parameters # store the parameters to resample the duration between components in the SubsystemCreator class
        for recovery_activity, recovery_activity_parameters in parameters.items():
            self.recovery_activities[recovery_activity] = ConcreteRecoveryActivity(recovery_activity, initial_level=1.0)
            self.recovery_activities[recovery_activity].set_preceding_activities(
                recovery_activity_parameters.get('PrecedingActivities', []))
            self.recovery_activities[recovery_activity].set_duration(recovery_activity_parameters.get('Duration', ''))
            self.recovery_activities[recovery_activity].set_demand(recovery_activity_parameters.get('Demand', ''))

    def set_initial_damage_level(self, damage_level: float) -> None:
        """
        Set the initial damage level. The damage level must be between 0 and 1.

        Sets the progress level of all activities to 0 and the progress level of the repair activity to 1 - damage_level.

        Args:
            damage_level (float): The initial damage level (between 0 and 1).
        """
        if 0 <= damage_level <= 1:
            for recovery_activity_object in self.recovery_activities.values():
                recovery_activity_object.set_level(0.0)
            self.set_initial_repair_activity_state(damage_level)
        else:
            raise ValueError('Damage level must be between 0 and 1.')

    def set_initial_repair_activity_state(self, damage_level: float) -> None:
        """
        Set the initial state of the repair activity. Initial level is 1 - damage_level and the rate is damage_level / duration to ensure that the component is repaired in the specified duration.

        Args:
            damage_level (float): The initial damage level (between 0 and 1).
        """
        self.recovery_activities[self.REPAIR_ACTIVITY_NAME].set_level(1 - damage_level)
        self.recovery_activities[self.REPAIR_ACTIVITY_NAME].rate = damage_level / self.recovery_activities[
            self.REPAIR_ACTIVITY_NAME].duration

    def recover(self, time_step: int) -> None:
        """
        Perform recovery for a time step. Increase the level of all activities that are not finished, for which all preceding activities are finished and the resource demand is met.

        Args:
            time_step (int): The time step for which recovery is performed.
        
        TODO: Not sure if there should be a for loop with start and end time steps or just get the length and multiply by the rate. Compare computational time.
        """
        if time_step in self.recovery_time_steps:
            start_time_step, end_time_step = self.get_time_step_length(time_step)
            for time_step in range(start_time_step, end_time_step):
                self.check_preceding_activities()
                for recovery_activity_object in self.recovery_activities.values():
                    if recovery_activity_object.preceding_activities_finished and self.get_damage_level() > 0:
                        recovery_activity_object.recover(time_step)

    def check_preceding_activities(self) -> None:
        """
        Check if preceding activities are finished for all recovery activities and set the preceding_activities_finished attribute accordingly.
        """
        for recovery_activity_object in self.recovery_activities.values():
            if self.preceding_activities_finished(recovery_activity_object):
                recovery_activity_object.set_preceding_activities_finished(True)
            else:
                recovery_activity_object.set_preceding_activities_finished(False)

    def preceding_activities_finished(self, recovery_activity_object: RecoveryActivity) -> bool:
        """
        Check if preceding activities for a single recovery activity are finished.

        Args:
            recovery_activity_object (RecoveryActivity): The recovery activity to check.

        Returns:
            bool: True if all preceding activities are finished, False otherwise.
        """
        for preceding_activity in recovery_activity_object.preceding_activities:
            if not (self.recovery_activities[preceding_activity].activity_finished()):
                return False
        return True

    def get_damage_level(self) -> float:
        """
        Get the current damage level of the component. It's 1 - the progress level of the repair activity.

        Returns:
            float: The damage level (between 0 and 1).
        """
        return 1 - self.recovery_activities[self.REPAIR_ACTIVITY_NAME].level

    def get_demand(self) -> dict:
        """
        Get the resource demand needed to meet the demand of all recovery activities currently in progress.

        Returns:
            dict: A dictionary of resource demands for active recovery activities.
        """
        resource_dict = {}
        for recovery_activity in self.recovery_activities.values():
            if self.preceding_activities_finished(recovery_activity) and self.get_damage_level() > 0 and not (
                    recovery_activity.activity_finished()):
                recovery_activity_demand = recovery_activity.get_demand()
                if len(recovery_activity_demand) > 0:
                    resource_dict = {**resource_dict, **recovery_activity_demand}
        return resource_dict

    def set_activities_demand_to_met(self) -> None:
        """
        Set the demand for recovery activities to met. This is done before resource are distributed at each time step, as resource distribution can only reduce the percent of met demand of a component - this is an iRe-CoDeS assumption.
        """
        for recovery_activity in self.recovery_activities.values():
            for resource_name in recovery_activity.demand.keys():
                recovery_activity.set_demand_met(resource_name, 1.0)

    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        """
        Set the percent of met demand for a recovery activity that requires the resource resource_name. This method is called during resource distribution.

        Args:
            resource_name (str): The name of the resource.
            percent_of_met_demand (float): The percent of met demand (between 0 and 1).:
        
        TODO:
            Add recovery activity name as input parameter. This will allow the same resource to be demanded by multiple recovery activities. Not possible at the moment.
        """
        recovery_activity_to_update = self.find_recovery_activity_that_demands_the_resource(resource_name)
        recovery_activity_to_update.set_demand_met(resource_name, percent_of_met_demand)

    def find_recovery_activity_that_demands_the_resource(self, resource_name: str) -> RecoveryActivity:
        """
        Find the recovery activity that demands the resource resource_name.

        Args:
            resource_name (str): The name of the resource.

        Returns:
            RecoveryActivity: The recovery activity that demands the resource.
        
        Raises:
            ValueError: If no recovery activity demands the resource.
        """
        for recovery_activity in self.recovery_activities.values():
            if resource_name in recovery_activity.demand:
                return recovery_activity
        raise ValueError('No recovery activity demands the resource: ' + resource_name)
