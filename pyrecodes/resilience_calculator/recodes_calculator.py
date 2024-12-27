import numpy as np
from pyrecodes.resilience_calculator.resilience_calculator import ResilienceCalculator

class ReCoDeSCalculator(ResilienceCalculator):
    """
    Resilience calculator class that assesses the resilience of a system based on the ReCoDeS framework.    
    """

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
    
    def __str__(self):
        lack_of_resilience = self.calculate_resilience()
        output = 'Re-CoDeS Resilience Calculator \n'
        output += 'Scope: ' + self.scope + '\n'
        output += '----------------------------- \n'
        output += 'Total unmet demand: \n'
        for resource_name, value in lack_of_resilience.items():
            output += ' ' + resource_name + ': ' + str(value) + '\n'
        return output

    def calculate_resilience(self) -> dict:
        self.lack_of_resilience = dict()
        for resource_name in self.resource_names:
            self.lack_of_resilience[resource_name] = np.sum(
                np.asarray(self.system_demand[resource_name]) - np.asarray(self.system_consumption[resource_name]))
        return self.lack_of_resilience

    def update(self, system):
        resources = system.resources
        for resource_name, resource_parameters in resources.items():
            if resource_name in self.resource_names:
                self.system_supply[resource_name].append(resource_parameters['DistributionModel'].get_total_supply(scope=self.scope))
                self.system_demand[resource_name].append(resource_parameters['DistributionModel'].get_total_demand(scope=self.scope))
                self.system_consumption[resource_name].append(
                    resource_parameters['DistributionModel'].get_total_consumption(scope=self.scope))