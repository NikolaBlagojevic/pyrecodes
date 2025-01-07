from abc import ABC, abstractmethod
import math

ABS_TOL = 1e-10

class Relation(ABC):
    """
    Class used to define various relations between component attributes in pyrecodes.
    """
    @abstractmethod
    def __init__(self, parameters: dict):
        pass

    @abstractmethod
    def get_output(self, input: float) -> float:
        pass

class ConcreteRelation(Relation):

    def __init__(self, parameters={}):
        pass

    def get_output(self, input: float):
        pass

    def valid_input(self, input: float) -> bool:
        if 0.0 <= input <= 1.0:
            return True
        else:
            raise ValueError('Input must be between 0 and 1.')

class Constant(ConcreteRelation):
    """
    Class for a relation that always returns 1.0 for any valid input.
    """
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            return 1.0

class Linear(ConcreteRelation):
    """
    Class for a relation that returns the input value - that is the relation between the input and output is linear with a coefficient of 1.
    """
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            return input

class ReverseLinear(ConcreteRelation):
    """
    Class for a relation that returns 1 - input value.
    """
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            return 1 - input

class Binary(ConcreteRelation):
    """
    Class for a binary relation that returns 1 if input is 1 and 0 otherwise.
    """
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            if math.isclose(input, 1, abs_tol=ABS_TOL):
                return 1
            else:
                return 0

class ReverseBinary(ConcreteRelation):
    """
    Class for a binary relation that returns 1 if input is 0 and 0 otherwise.
    """
    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            if math.isclose(input, 0, abs_tol=ABS_TOL):
                return 1
            else:
                return 0

class MultipleStep(ConcreteRelation):
    """
    | Multiple step relation between input and output.

    | Step limits define the values at which the output changes. Step values define the output values.
    | if limit smaller than the lowest limit, output is 0.0
    | if limit larger than the largest limit, output is 1.0

    | Note: input has to be rounded, otherwise comparison does not work. 
    """

    def __init__(self, parameters={}):
        self.set_steps(parameters.get('StepLimits', []), parameters.get('StepValues', []))

    def get_output(self, input: float) -> float:
        if self.valid_input(input):
            input = round(input, int(math.log10(1 / ABS_TOL)))
            input_step = self.get_step_id(input)
            return self.step_values[input_step]
            
    def get_step_id(self, input: float) -> int:
        for i in range(len(self.step_limits) - 1):
            if self.step_limits[i] <= input < self.step_limits[i + 1]:
                return i
        if input < self.step_limits[0]:
            return 0
        elif input >= self.step_limits[-1]:
            return len(self.step_limits) - 1
        
    def set_steps(self, step_limits: list[float], step_values: list[float]):   
        if len(step_limits) != len(step_values):
            raise ValueError('Number of step limits and step values should be the same.')
        else:
            self.step_limits = step_limits
            self.step_values = step_values