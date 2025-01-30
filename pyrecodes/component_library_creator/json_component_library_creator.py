from pyrecodes.component_library_creator.component_library_creator import ComponentLibraryCreator
from pyrecodes.component.component import Component
from pyrecodes.utilities import get_class
import json

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
    
    def form_component(self, component_name: str, component_parameters: dict) -> Component:
        """
        Form and return a component object based on the input component_name and component_parameters to be used as component template in system creation.
        """
        target_class = get_class(component_parameters["ComponentClass"]["FileName"], 
                                 component_parameters['ComponentClass']['ClassName'], 
                                 "component")
        component = target_class()
        component.construct(component_name, component_parameters)     
        return component