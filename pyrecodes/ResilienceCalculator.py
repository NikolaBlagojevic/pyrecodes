from abc import ABC, abstractmethod
import numpy as np

"""
Module used to define resilience calculators used in the system.

More details coming soon.
"""


class ResilienceCalculator(ABC):

    @abstractmethod
    def calculate_resilience(self):
        pass

    @abstractmethod
    def update(self):
        pass


class FullRecoveryTimeResilienceCalculator(ResilienceCalculator):

    def calculate_resilience(self):
        return self.current_recovery_time

    def update(self, time_step: int) -> None:
        self.current_time_step = time_step


class ReCoDeSResilienceCalculator(ResilienceCalculator):

    def __init__(self, parameters: dict) -> None:   
        self.system_supply = {}
        self.system_demand = {}
        self.system_consumption = {}
        self.resource_names = parameters["Resources"]
        self.scope = parameters["Scope"]
        for resource_name in self.resource_names:
            self.system_supply[resource_name] = []
            self.system_demand[resource_name] = []
            self.system_consumption[resource_name] = []

    def calculate_resilience(self) -> dict:
        lack_of_resilience = dict()
        for resource_name in self.resource_names:
            lack_of_resilience[resource_name] = np.sum(
                np.asarray(self.system_demand[resource_name]) - np.asarray(self.system_consumption[resource_name]))
        return lack_of_resilience

    def update(self, resources: dict):
        for resource_name, resource_parameters in resources.items():
            if resource_name in self.resource_names:
                self.system_supply[resource_name].append(resource_parameters['DistributionModel'].get_total_supply(scope=self.scope))
                self.system_demand[resource_name].append(resource_parameters['DistributionModel'].get_total_demand(scope=self.scope))
                self.system_consumption[resource_name].append(
                    resource_parameters['DistributionModel'].get_total_consumption(scope=self.scope))


class NISTGoalsResilienceCalculator(ReCoDeSResilienceCalculator):

    def __init__(self, resilience_goals: list) -> None:
        self.set_resilience_goals(resilience_goals)

    def set_resilience_goals(self, resilience_goals: list):
        self.resilience_goals = []
        for resilience_goal in resilience_goals:
            self.resilience_goals.append(resilience_goal)
            self.resilience_goals[-1]['GoalMet'] = []

    def update(self, resources: dict):
        # compare demand and consumption and check if the goal is met
        # if its met, save the time step in a bool list and then in the end in calculate resilience method get the first time step when the goal is met and maintained
        for resilience_goal in self.resilience_goals:
            resource_parameters = resources.get(resilience_goal['Resource'])            
            total_demand = resource_parameters['DistributionModel'].get_total_demand(scope=resilience_goal['Scope'])
            total_consumption = resource_parameters['DistributionModel'].get_total_consumption(scope=resilience_goal['Scope'])
            resilience_goal['GoalMet'].append(resilience_goal['DesiredFunctionalityLevel'] < total_consumption/total_demand)

    def calculate_resilience(self):
        # find the time step at which the goal is met and MAINTAINED - the last time step at which the goal was not met
        for resilience_goal in self.resilience_goals:
            resilience_goal['MetAtTimeStep'] = np.where(np.asarray(resilience_goal['GoalMet']) == False)[0][-1] + 1
            # remove GoalMet key not important anymore
            del resilience_goal['GoalMet']
        return self.resilience_goals

    
        
