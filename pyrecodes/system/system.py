from abc import ABC, abstractmethod
from pyrecodes.component.component import Component
from pyrecodes.system_creator.system_creator import SystemCreator

class System(ABC):
    """
    Interface class representing a generic system for resilience assessment.

    Attributes:
        | components (list[Component]): List of system components represented as Component objects.
        | resources (dict): Dictionary containing resource parameters.
        | system_creator (SystemCreator): The system creator object responsible for system initialization.

    """
    components: list[Component]
    resources: dict
    system_creator: SystemCreator

    @abstractmethod
    def __init__(self, system_configuration_file: dict, component_library: dict, system_creator: SystemCreator):
        """
        Constructor method for the System class. Initializes the system with the given configuration.

        Args:
            | configuration_file (dict): The configuration file for the system.
            | component_library (dict): The component library containing system components' configurations.
            | system_creator (SystemCreator): The system creator object responsible for system initialization.
        """
        pass

    @abstractmethod
    def set_configuration_file(self, system_configuration: dict):
        """
        Sets the configuration file for the system.

        Args:
            system_configuration (dict): System configuration dictionary.
        """
        pass

    @abstractmethod
    def set_component_library(self, component_library: dict):
        """
        Sets the component library for the system.

        Args:
            component_library (dict): The component library to set for the system.
        """
        pass

    @abstractmethod
    def create_system(self, system_creator: SystemCreator):
        """
        Creates the system based on the provided SystemCreator object.

        Args:
            system_creator (SystemCreator): The system creator object responsible for system initialization.
        """
        pass

    @abstractmethod
    def set_initial_damage(self):
        """
        Sets the initial damage state of the system components.
        """
        pass

    @abstractmethod
    def start_resilience_assessment(self):
        """
        Initiates the resilience assessment for the system. This is the entry point for running the assessment.
        """
        pass

    @abstractmethod
    def distribute_resources(self):
        """
        Distributes resources among the system component's.
        """
        pass

    @abstractmethod
    def update(self):
        """
        Updates the system state at a time step of the resilience assessment.
        """
        pass

    @abstractmethod
    def recover(self):
        """
        Simulates the recovery process in the system.
        """
        pass

    @abstractmethod
    def calculate_resilience(self):
        """
        Calculates and returns the resilience metric for the system.
        """
        pass