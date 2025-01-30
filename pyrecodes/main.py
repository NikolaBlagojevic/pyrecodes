"""
Module used to run the **pyrecodes** resilience assessment as defined in the component library and system configuration files.
"""
from pyrecodes.utilities import read_json_file, get_class
from pyrecodes.system.system import System

def form_component_library(input_dict: dict) -> dict:
    """Forms a component library based on the input dictionary.

    Args:
        input_dict (dict): The input dictionary containing component library configuration.

    Returns:
        dict: The component library dict.
    """
    component_library_target_class = get_class(input_dict['ComponentLibrary']['ComponentLibraryCreatorFileName'], 
                                                input_dict['ComponentLibrary']['ComponentLibraryCreatorClassName'], 
                                                "component_library_creator")
    component_library_object = component_library_target_class(input_dict['ComponentLibrary']['ComponentLibraryFile'])
    
    return component_library_object.form_library()

def create_system(input_dict: dict) -> System:
    """Creates a system object using the input dictionary.

    Args:
        input_dict (dict): The input dictionary containing System configuration.

    Returns:
        System: The created system object.
    """
    # Form the component library dict using the input dictionary.
    component_library = form_component_library(input_dict)

    # Read the system configuration file.
    system_configuration = read_json_file(input_dict['System']['SystemConfigurationFile'])
    
    # Extract the target SystemCreator class from the input dictionary and instantiate it.
    system_creator_target_class = get_class(input_dict['System']['SystemCreatorFileName'], input_dict['System']['SystemCreatorClassName'], 'system_creator')  
    system_creator = system_creator_target_class()
    
    # Extract the target System class from the input dictionary and instantiate it with the necessary arguments.
    system_target_class = get_class(input_dict['System']['SystemFileName'], input_dict['System']['SystemClassName'], 'system')
    system = system_target_class(system_configuration, component_library, system_creator)
    system.create_system()
    return system

def run(main_file: str) -> System:
    """Runs the resilience assessment for the system.

    Args:
        main_file (str): The name of the main JSON configuration file.

    Returns:
        System: The system object after running the resilience assessment.
    """
    # Read the main JSON configuration file and obtain the input dictionary.
    input_dict = read_json_file(main_file)    
    # Create the system object using the input dictionary.
    system = create_system(input_dict)
    # Start the resilience assessment for the system.
    system.start_resilience_assessment()
    # Return the system object.
    return system

def load_system(loadname, system_class_name='BuiltEnvironment', system_file_name='built_environment') -> System:
    """
    Loads a previously saved system. Does not yet work for systems which use SimCenter API infrastructure models.
    """
    target_system_class = get_class(system_file_name, system_class_name, 'system')
    system_object = target_system_class({}, {}, None) 
    return system_object.load_as_pickle(loadname)