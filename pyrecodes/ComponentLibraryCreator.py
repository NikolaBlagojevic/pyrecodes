"""
Module used to create component library based on which system components are constructed.
"""

import json
from abc import ABC, abstractmethod
from pyrecodes import Component

class ComponentLibraryCreator(ABC):
    """
    Abstract class for ComponentLibraryCreator class used to create component library based on which system components are constructed.
    """

    library: dict

    @abstractmethod
    def form_library(self) -> dict:
        pass


class JSONComponentLibraryCreator(ComponentLibraryCreator):
    """
    Class to create a component library from a single JSON file containing component templates for each component type. 
    """

    library: dict

    def __init__(self, file_name: str) -> None:
        """
        Initiliaze the class. Read the component library JSON file.
        """
        self.file = None
        self.read_library_file(file_name)

    def read_library_file(self, file_name: str) -> None:
        with open(file_name, 'r') as file:
            self.file = json.load(file)

    def form_library(self) -> dict:
        """
        Form component library based on the component template specificed in the component library JSON file. Returns a dict with component templates.
        """
        component_library = dict()
        for component_name, component_params in self.file.items():
            component_library[component_name] = self.form_component(component_name, component_params)
        return component_library
    
    def form_component(self, component_name: str, component_parameters: dict) -> Component.Component:
        """
        Form and return a component object based on the input component_name and component_parameters to be used as component template in system creation.
        """
        target_object = getattr(Component, component_parameters['ComponentClass'])
        component = target_object()
        component.construct(component_name, component_parameters)     
        return component
