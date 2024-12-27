from pyrecodes.resilience_calculator.recodes_calculator import ReCoDeSCalculator
import numpy as np

class NISTGoalsCalculator(ReCoDeSCalculator):
    """
    | Resilience calculator class that assesses the resilience of a system based on NIST resilience goals.
    | The NIST resilience goals are defined as achieving the desired functionality level of a system within a certain time after a disruption.
    | Functionality level is defined as the ratio of the total consumption (i.e., met demand) to the total demand of a resource provided by the system.
    """

    def __init__(self, resilience_goals: list) -> None:
        self.set_resilience_goals(resilience_goals)
    
    def __str__(self):
        # define what the print() method should return
        output = 'NIST Resilience Goals Calculator: \n'
        output += '-------------------------------- \n'
        for resilience_goal in self.resilience_goals:
            for key, value in resilience_goal.items():
                output += ' ' + key + ': ' + str(value) + '\n'
            output += '\n'
        return output

    def set_resilience_goals(self, resilience_goals: list):
        self.resilience_goals = []
        for resilience_goal in resilience_goals:
            self.resilience_goals.append(resilience_goal)
            self.resilience_goals[-1]['GoalMet'] = []

    def update(self, system):
        """
        | Method compares the demand and consumption of resources in the system and checks if the desired functionality level is met.
        | A boolean list contains the information at which time steps the desired functionality level is met.
        """
        resources = system.resources        
        for resilience_goal in self.resilience_goals:
            resource_parameters = resources.get(resilience_goal['Resource'])            
            total_demand = resource_parameters['DistributionModel'].get_total_demand(scope=resilience_goal['Scope'])
            total_consumption = resource_parameters['DistributionModel'].get_total_consumption(scope=resilience_goal['Scope'])
            if total_demand == 0:
                resilience_goal['GoalMet'].append(False)
            else:
                resilience_goal['GoalMet'].append(resilience_goal['DesiredFunctionalityLevel'] < total_consumption/total_demand)

    def calculate_resilience(self):
        """"
        | Method finds the time step at which the goal is met and MAINTAINED - the last time step at which the goal was not met.
        | Since the demand and consumption of resources are updated at each time step, the goal may be met at one time step and not met at the next time step.
        | If the goal is met at all time steps, the method returns 0.
        """
        for resilience_goal in self.resilience_goals:
            if False in resilience_goal['GoalMet']:
                resilience_goal['MetAtTimeStep'] = np.where(np.asarray(resilience_goal['GoalMet']) == False)[0][-1] + 1
            else:
                resilience_goal['MetAtTimeStep'] = 0
            del resilience_goal['GoalMet']
        return self.resilience_goals