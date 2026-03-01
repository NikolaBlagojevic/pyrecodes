import os
import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes.system.system import System
from pyrecodes import main

FOLDER_NAME = "./tests/test_inputs"
MAIN_FILE = "test_inputs_ThreeLocalitiesCommunity_Main.json"

class TestMain():

    def test_form_component_library(self):
        input_dict = {
            "ComponentLibrary": {
                "ComponentLibraryCreatorClassName": "JSONComponentLibraryCreator",
                "ComponentLibraryCreatorFileName": "json_component_library_creator",
                "ComponentLibraryFile": "test_inputs_ThreeLocalitiesCommunity_ComponentLibrary.json"
            }
        }
        component_library = main.form_component_library(FOLDER_NAME, input_dict)
        assert isinstance(component_library, dict)

    def test_create_system(self):
        # Test creating a system object and check if it is an instance of System.System
        input_dict = read_json_file(f'{FOLDER_NAME}/{MAIN_FILE}')
        system = main.create_system(FOLDER_NAME, input_dict)
        assert isinstance(system, System)

    def test_run(self):
        # Test running the resilience assessment for the system and check if the returned value is a System.System object
        system = main.run(FOLDER_NAME, MAIN_FILE)
        assert isinstance(system, System)

    def test_load_system(self):
        # Test loading a previously saved system and check if it is an instance of System.System
        loadname = "./tests/test_inputs/test_system.pickle"
        system = main.load_system(loadname)
        assert isinstance(system, System)
