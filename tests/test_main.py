import os
from pyrecodes import System
from pyrecodes import main

# Define the path to the test JSON configuration files
TEST_DATA_PATH = "tests/test_inputs/"

def test_read_file():
    # Test reading a JSON file and check if the returned value is a dictionary
    file_name = os.path.join(TEST_DATA_PATH, "test_inputs_ThreeLocalitiesCommunity_Main.json")
    data = main.read_file(file_name)
    assert isinstance(data, dict)

def test_form_component_library():
    # Test forming a component library and check if the returned value is a dictionary
    input_dict = {
        "ComponentLibrary": {
            "ComponentLibraryCreatorClass": "JSONComponentLibraryCreator",
            "ComponentLibraryFile": "./tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_ComponentLibrary.json"
        }
    }
    component_library = main.form_component_library(input_dict)
    assert isinstance(component_library, dict)

def test_create_system():
    # Test creating a system object and check if it is an instance of System.System
    file_name = os.path.join(TEST_DATA_PATH, "test_inputs_ThreeLocalitiesCommunity_Main.json")
    input_dict = main.read_file(file_name)
    system = main.create_system(input_dict)
    assert isinstance(system, System.System)

def test_run():
    # Test running the resilience assessment for the system and check if the returned value is a System.System object
    main_file = os.path.join(TEST_DATA_PATH, "test_inputs_ThreeLocalitiesCommunity_Main.json")
    system = main.run(main_file)
    assert isinstance(system, System.System)

def test_load_system():
    # Test loading a previously saved system and check if it is an instance of System.System
    loadname = os.path.join(TEST_DATA_PATH, "test_inputs_Example_3.pickle")
    system = main.load_system(loadname)
    assert isinstance(system, System.System)
