from abc import ABC, abstractmethod
import math
import bisect
import numpy as np

ABS_TOL = 1e-10

class Relation(ABC):
    """
    Abstract class for all functions used to define relations between damage and functionality of a component and functionality and supply and demand.
    """

    @abstractmethod
    def get_output(self, input: float) -> float():
        pass

class ConcreteRelation(Relation):

    def get_output(self, input: float):
        pass

    def valid_input(self, input: float) -> bool:
        if 0.0 <= input <= 1.0:
            return True
        else:
            raise ValueError('Input must be between 0 and 1.')

class Constant(ConcreteRelation):
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            return 1.0

class Linear(ConcreteRelation):
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            return input

class ReverseLinear(ConcreteRelation):
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            return 1 - input

class Binary(ConcreteRelation):
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            if math.isclose(input, 1, abs_tol=ABS_TOL):
                return 1
            else:
                return 0

class ReverseBinary(ConcreteRelation):
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            if math.isclose(input, 0, abs_tol=ABS_TOL):
                return 1
            else:
                return 0

class MultipleStep(ConcreteRelation):
    """
    Multiple step relation between input and output.

    Step limits define the values at which the output changes. Step values define the output values.
    if limit smaller than the lowest limit, output is 0.0
    if limit larger than the largest limit, output is 1.0
    
    """
    def get_output(self, input: float) -> float:
        if self.valid_input(input):      
            # if math.isclose(input, 1.0, abs_tol=ABS_TOL):
            #     return 1.0
            # elif math.isclose(input, 0.0, abs_tol=ABS_TOL):
            #     return self.step_values[0]
            # else:
            #     step_id = bisect.bisect_left(self.step_limits, input)
            #     return self.step_values[step_id]
            for i in range(len(self.step_limits) - 1):
                if input < self.step_limits[0]:
                    return 0.0
                elif self.step_limits[i] <= input < self.step_limits[i + 1]:
                    return self.step_values[i]
                elif input >= self.step_limits[-1]:
                    return 1.0
        
    def set_steps(self, step_limits: list([float]), step_values: list([float])):   
        if len(step_limits) != len(step_values):
            raise ValueError('Number of step limits and step values should be the same.')
        else:
            self.step_limits = step_limits
            self.step_values = step_values