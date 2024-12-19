from pyrecodes.resilience_calculator.recodes_calculator import ReCoDeSCalculator
import numpy as np

class NISTGoalsCalculator(ReCoDeSCalculator):

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
        resources = system.resources
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