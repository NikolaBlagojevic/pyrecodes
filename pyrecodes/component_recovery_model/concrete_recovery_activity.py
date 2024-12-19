from pyrecodes.component_recovery_model.recovery_activity import RecoveryActivity
import math
from pyrecodes.resource.concrete_resource import ConcreteResource
from pyrecodes.probability_distribution import probability_distribution

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
        target_distribution = getattr(probability_distribution, distribution_name)
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
            self.demand[resource_name] = ConcreteResource(resource_name, resource_parameters)
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
