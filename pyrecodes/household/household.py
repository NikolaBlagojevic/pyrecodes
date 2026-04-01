from abc import abstractmethod
from pyrecodes.system.system import System

class Household:

    @abstractmethod
    def set_socioeconomic_parameters(self, parameters: dict):
        pass

    @abstractmethod
    def decide(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def get_demand(self):
        pass

    @abstractmethod
    def get_supply(self):
        pass

    @abstractmethod
    def map_buildings_to_households(self, built_environment: System):
        pass


    
