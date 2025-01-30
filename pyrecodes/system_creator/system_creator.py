from abc import ABC, abstractmethod
from pyrecodes.component.component import Component
from pyrecodes.component_library_creator.component_library_creator import ComponentLibraryCreator

class SystemCreator(ABC):
    """
    Abstract class for creating a System from a file
    """

    @abstractmethod
    def setup(self, component_library: ComponentLibraryCreator, file_name: str) -> None:
        pass

    @abstractmethod
    def create_components(self) -> list[Component]:
        pass

    @abstractmethod
    def get_damage_input_type(self) -> str:
        pass

    @abstractmethod
    def get_damage_input_parameters(self) -> dict:
        pass

    @abstractmethod
    def get_resource_distribution_parameters(self) -> dict:
        pass