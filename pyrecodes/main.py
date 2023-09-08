"""
Module used to run the **pyrecodes** resilience assessment as defined in the component library and system configuration files.
"""

from pyrecodes import ComponentLibraryCreator
from pyrecodes import SystemCreator
from pyrecodes import System
import json

def read_file(file_name: str) -> dict:
    """Reads a JSON file and returns its contents as a dictionary.

    Args:
        file_name (str): The name of the JSON file to be read.

    Returns:
        dict: The dictionary representation of the JSON data.
    """
    with open(file_name, 'r') as file:
        file = json.load(file)
    return file

def form_component_library(input_dict: dict) -> dict:
    """Forms a component library based on the input dictionary.

    Args:
        input_dict (dict): The input dictionary containing component library configuration.

    Returns:
        dict: The component library dict.
    """
    # Extract the target ComponentLibraryCreator class from the input dictionary and instantiate it.
    component_library_target_object = getattr(ComponentLibraryCreator, input_dict['ComponentLibrary']['ComponentLibraryCreatorClass'])  
    component_library_object = component_library_target_object(input_dict['ComponentLibrary']['ComponentLibraryFile'])
    
    # Call the 'form_library()' method on the component_library_object and return the component library as a dict.
    return component_library_object.form_library()

def create_system(input_dict: dict) -> System.System:
    """Creates a system object using the input dictionary.

    Args:
        input_dict (dict): The input dictionary containing System configuration.

    Returns:
        System.System: The created system object.
    """
    # Form the component library dict using the input dictionary.
    component_library = form_component_library(input_dict)

    # Read the system configuration file.
    system_configuration = read_file(input_dict['System']['SystemConfigurationFile'])
    
    # Extract the target SystemCreator class from the input dictionary and instantiate it.
    system_creator_target_object = getattr(SystemCreator, input_dict['System']['SystemCreatorClass'])  
    system_creator = system_creator_target_object()
    
    # Extract the target System class from the input dictionary and instantiate it with the necessary arguments.
    system_target_object = getattr(System, input_dict['System']['SystemClass']) 
    system = system_target_object(system_configuration, component_library, system_creator)
    system.create_system()
    return system

def run(main_file: str) -> System.System:
    """Runs the resilience assessment for the system.

    Args:
        main_file (str): The name of the main JSON configuration file.

    Returns:
        System.System: The system object after running the resilience assessment.
    """
    # Read the main JSON configuration file and obtain the input dictionary.
    input_dict = read_file(main_file)    
    # Create the system object using the input dictionary.
    system = create_system(input_dict)
    # Start the resilience assessment for the system.
    system.start_resilience_assessment()
    # Return the system object.
    return system

def load_system(loadname, system_class_name='BuiltEnvironmentSystem') -> System.System:
    target_system_class = getattr(System, system_class_name)
    system_object = target_system_class({}, {}, None) 
    return system_object.load_as_pickle(loadname)