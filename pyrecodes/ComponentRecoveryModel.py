import math
from abc import ABC, abstractmethod
from pyrecodes import ProbabilityDistribution
from pyrecodes import Relation
from pyrecodes import Resource

"""
Module used to define recovery models for components.
"""

class RecoveryActivity(ABC):
    """
    Abstract class representing a recovery activity.

    Attributes:
        level (float): The current progress level of the activity at a time step (between 0 and 1).
        duration (float): The duration of the activity.
        rate (float): The rate of progress per time unit.
        preceding_activities (list[str]): List of names of preceding activities that have to be completed until this activity can start.
        preceding_activities_finished (bool): True if all preceding activities are finished.
        demand_met (float): The percent of demand met.
        name (str): The name of the recovery activity.
        time_steps (list[int]): List of time steps when progress was recorded.
    """
    level: float
    duration: float
    rate: float
    preceding_activities: list([str])
    preceding_activities_finished: bool
    demand_met: float
    name: str
    time_steps: list([int])

    @abstractmethod
    def __init__(self, name: str) -> None:
        pass

    @abstractmethod
    def set_name(self, name: str) -> None:
        pass

    @abstractmethod
    def set_level(self, level: float) -> None:
        pass

    @abstractmethod
    def set_duration(self, distribution: dict) -> None:
        pass

    @abstractmethod
    def sample_duration(self, distribution: dict) -> float:
        pass

    @abstractmethod
    def set_preceding_activities(self, preceding_activities: list([str])) -> None:
        pass    

    @abstractmethod
    def set_preceding_activities_finished(self, finished: bool) -> None:
        pass

    @abstractmethod
    def set_demand(self, resources: list) -> None:
        pass

    @abstractmethod
    def set_demand_met(self) -> None:
        pass

    @abstractmethod
    def get_demand(self) -> dict:
        pass

    @abstractmethod
    def recover(self, time_step: int) -> None:
        pass

    @abstractmethod
    def record_progress(self, time_step: int) -> None:
        pass

    @abstractmethod
    def activity_finished(self) -> bool:
        pass


class ConcreteRecoveryActivity(RecoveryActivity):
    """
    Concrete implementation of a recovery activity.
    """

    def __init__(self, name: str, initial_level=0.0) -> None:
        """
        Constructor for ConcreteRecoveryActivity.

        Args:
            name (str): The name of the activity.
            initial_level (float, optional): The initial progress level (default is 0.0).
        """
        self.set_name(name)
        self.set_level(initial_level)
        self.time_steps = []
        self.demand_met = {}
        self.demand = {}
        self.preceding_activities_finished = False

    def set_name(self, name: str) -> None:
        """
        Set the name of the activity.

        Args:
            name (str): The name of the activity.
        """
        self.name = name

    def set_level(self, level: float) -> None:
        """
        Set the progress level of the activity.

        Args:
            level (float): The progress level of the activity (between 0 and 1).
        """
        if 0 <= level <= 1:
            self.level = level
        else:
            raise ValueError(f'Level must be between 0 and 1. Recovery activity: {self.name}.')

    def set_duration(self, distribution: dict) -> None:
        """
        Set the duration of the activity based on a distribution. Duration must be a positive number. If duration is zero, the rate is infinite - activity is immediately finished.

        Args:
            distribution (dict): A dictionary describing the duration distribution.
        """
        duration = self.sample_duration(distribution)
        self.duration = duration
        if duration > 0:            
            self.rate = 1 / duration
        elif duration == 0: 
            self.rate = math.inf
        else:
            raise ValueError(f'Duration must be a positive number. Recovery activity: {self.name}.')

    def sample_duration(self, distribution: dict) -> float:
        """
        Sample the duration from a distribution.

        Args:
            distribution (dict): A dictionary describing the duration distribution.

        Returns:
            float: The sampled duration.
        """
        distribution_name, distribution_parameters = list(distribution.items())[0]
        target_distribution = getattr(ProbabilityDistribution, distribution_name)
        distribution = target_distribution(distribution_parameters)
        return distribution.sample()

    def set_preceding_activities(self, preceding_activities: list([str])) -> None:
        """
        Set preceding activities that need to be completed for this activity to start.

        Args:
            preceding_activities (list[str]): List of names of preceding activities.
        """
        self.preceding_activities = preceding_activities

    def set_preceding_activities_finished(self, finished: bool) -> None:
        """
        Set the status of preceding activities.

        Args:
            finished (bool): True if all preceding activities are finished.
        """
        self.preceding_activities_finished = finished

    def set_demand(self, resources: list) -> None:
        """
        Set the resource demand for the activity.

        Args:
            resources (list): List of dictionaries describing resource demands.
        """
        for resource in resources:
            resource_name = resource['Resource']
            resource_parameters = {'Amount': resource['Amount']}          
            self.demand[resource_name] = Resource.ConcreteResource(resource_name, resource_parameters)
            self.demand_met[resource_name] = 1.0

    def set_demand_met(self, resource_name: str, demand_met: float) -> None:
        """
        Set the level of demand met (between 0 and 1) for a resource resource_name.

        Args:
            resource_name (str): The name of the resource.
            demand_met (float): The level of demand met (between 0 and 1).
        """
        if 0 <= demand_met <= 1:
            self.demand_met[resource_name] = demand_met
        else:
            raise ValueError(f'Demand Met must be between 0 and 1. Recovery activity: {self.name}. Resource name: {resource_name}')

    def get_demand(self) -> dict:
        """
        Get the current resource demand of the activity.

        Returns:
            dict: A dictionary of resource demands.
        """
        return self.demand

    def recover(self, time_step: int) -> None:
        """
        Perform recovery for a given time step. Activity recovers (i.e., progresses) if it's not already finished. The rate of progress depends on the percent of met resource demand. 

        Args:
            time_step (int): The time step for which recovery is performed.
        """
        if not self.activity_finished():
            current_level_increase = self.rate * self.effect_of_unmet_demand_on_activity()            
            self.level = min(self.level + current_level_increase, 1.0)
            if current_level_increase > 0:
                self.record_progress(time_step)

    def record_progress(self, time_step: int) -> None:
        """
        Record progress at a specific time step. If the rate at a time step was higher than zero, than the time step is recorded.

        Args:
            time_step (int): The time step when progress is recorded.
        """
        self.time_steps.append(time_step)
    
    def effect_of_unmet_demand_on_activity(self) -> float:
        """
        Determine how demand met for each resource in the recovery demand affects the recovery activity.

        Returns:
            float: The effect of unmet demand on the activity.
        """
        return min(self.demand_met.values(), default=1.0)

    def activity_finished(self) -> bool:
        """
        Check if the activity is finished and return a boolean value.

        Returns:
            bool: True if the activity is finished, False otherwise.
        """
        return math.isclose(self.level, 1.0)

class RecoveryModel(ABC):
    """
    Abstract class representing a recovery model.
    """

    recovery_activities: dict

    @abstractmethod
    def set_parameters(self, parameters: dict) -> None:
        pass

    @abstractmethod
    def set_initial_damage_level(self, damage_level: float) -> None:
        pass

    @abstractmethod
    def set_damage_functionality(self, damage_functionality_relation: dict) -> None:
        pass

    @abstractmethod
    def set_activities_demand_to_met(self) -> None:
        pass

    @abstractmethod
    def recover(self, time_step: int) -> None:
        pass

    @abstractmethod
    def get_functionality_level(self) -> float:
        pass

    @abstractmethod
    def get_demand(self) -> dict:
        pass

    @abstractmethod
    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        pass

class ComponentLevelRecoveryActivitiesModel(RecoveryModel):
    """
    Component recovery model that considers multiple recovery activities defined on a component level.
    
    This model accounts for several impeding factors and a single repair activity.

    Attributes:
        damage_level (float): The damage level of the component (between 0 and 1).
        damage_to_functionality_relation (Relation.Relation): The relation to get the functionality level based on the current damage level.
        recovery_activities (dict): A dictionary of recovery activities parameters.
        REPAIR_ACTIVITY_NAME (str): The name of the repair activity - one that actually reduces the damage level.
    """

    damage_level: float
    damage_to_functionality_relation: Relation.Relation
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

    def set_damage_functionality(self, damage_functionality_relation: dict) -> None:
        """
        Set damage functionality relation. This relation is used to get the component's functionality level based on its current damage level.

        Args:
            damage_functionality_relation (dict): Damage functionality relation parameters.
        """
        target_damage_functionality = getattr(Relation, damage_functionality_relation['Type'])
        self.damage_to_functionality_relation = target_damage_functionality()

    def recover(self, time_step: int) -> None:
        """
        Perform recovery for a time step. Increase the level of all activities that are not finished, for which all preceding activities are finished and the resource demand is met.

        Args:
            time_step (int): The time step for which recovery is performed.
        """
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

    def get_functionality_level(self) -> float:
        """
        Get the functionality level of the component absed on the current damage level and the damage-functionality relation.

        Returns:
            float: The functionality level (between 0 and 1).
        """
        return self.damage_to_functionality_relation.get_output(self.get_damage_level())

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

class NoRecoveryActivityModel(ComponentLevelRecoveryActivitiesModel):
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

    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        pass

class InfrastructureInterfaceRecoveryModel(RecoveryModel):
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
    
    def set_parameters(self, parameters: dict, default_duration=[{"Deterministic": {"Value": 0}}]) -> None:
        """
        Set model parameters. These include setting the post-disaster functionality levels and the time steps at which they change as multiple steps to achieve the predefined supply/demand dynamics as set in the system configuration file.

        Args:
            parameters (dict): Parameters for the recovery model.
            default_duration (list, optional): Default duration for recovery activities (default is zero).

        Notes:
            - This method sets step durations and demands for the recovery activity.
            - The implementation might be improved in the future.

        TODO:
            - Improve the method. See if StepLimits are redundant as RestoredIn is already defined.
            - The for loop setting the duration is a temporary solution. It should be replaced by a more general solution, just take the max.
        """
        self.damage_to_functionality_relation.set_steps(parameters.get('StepLimits', []), parameters.get('StepValues', []))
        step_durations = parameters.get('RestoredIn', default_duration)
        for step_duration in step_durations:
            self.recovery_activities[self.RECOVERY_ACTIVITY_NAME].set_duration(step_duration)
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
        target_damage_functionality = getattr(Relation, 'MultipleStep')
        self.damage_to_functionality_relation = target_damage_functionality()

    def set_activities_demand_to_met(self) -> None:
        pass

    def recover(self, time_step: int) -> None:
        """
        Perform recovery for a time step. Recovery here means simulating the pre-defined post-disaster supply/demand dynamics.

        Args:
            time_step (int): The time step for which recovery is performed.
        """
        self.recovery_activities[self.RECOVERY_ACTIVITY_NAME].recover(time_step)

    def get_functionality_level(self) -> float:
        """
        Get the functionality level of the infrastructure interface.

        Returns:
            float: The functionality level.
        """
        return self.damage_to_functionality_relation.get_output(1 - self.get_damage_level())
    
    def get_damage_level(self) -> float:
        """
        Get the damage level of the infrastructure interface.

        Returns:
            float: The damage level.
        """
        return 1 - self.recovery_activities[self.RECOVERY_ACTIVITY_NAME].level
    
    def get_demand(self) -> dict:
        """
        Get the demand for the infrastructure interface.

        Returns:
            dict: An empty dictionary, as it assumed that there is no recovery demand for infrastructure interfaces.
        """
        return {}
    
    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        pass
