import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.subsystem_creator.json_subsystem_creator import JSONSubsystemCreator
from tests.test_subsystem_creator.test_subsystem_creator_inputs import MAIN_FILE, LOCALITY_CENTROID, PARAMETERS_BTS, PARAMETERS_LINKS, PARAMETERS_DIFFERENT_COMPONENTS, CONSTANTS

class TestJSONSubsystemCreator:

    @pytest.fixture
    def component_library(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.form_component_library(input_dict)
    
    def test_create_components_in_localities(self, component_library):
        json_subsystem_creator = JSONSubsystemCreator(component_library, LOCALITY_CENTROID, PARAMETERS_BTS, constants=CONSTANTS, damage_input={})
        components = json_subsystem_creator.create_components_in_localities()
        assert len(components) == 1
        assert components[0].name == 'BaseTransceiverStation_2'
    
        json_subsystem_creator = JSONSubsystemCreator(component_library, LOCALITY_CENTROID, PARAMETERS_LINKS, constants=CONSTANTS, damage_input={})
        components = json_subsystem_creator.create_components_in_localities()
        assert len(components) == 0

        json_subsystem_creator = JSONSubsystemCreator(component_library, LOCALITY_CENTROID, PARAMETERS_DIFFERENT_COMPONENTS, constants=CONSTANTS, damage_input={})
        components = json_subsystem_creator.create_components_in_localities()
        assert len(components) == 3
        assert components[0].name == 'BuildingStockUnit'
        assert components[1].name == 'BaseTransceiverStation_2'
        assert components[2].name == 'ElectricPowerPlant'

    def test_create_components_between_localities(self, component_library):
        json_subsystem_creator = JSONSubsystemCreator(component_library, LOCALITY_CENTROID, PARAMETERS_BTS, constants=CONSTANTS, damage_input={})
        components = json_subsystem_creator.create_components_between_localities()
        assert len(components) == 0
    
        json_subsystem_creator = JSONSubsystemCreator(component_library, LOCALITY_CENTROID, PARAMETERS_LINKS, constants=CONSTANTS, damage_input={})
        components = json_subsystem_creator.create_components_between_localities()
        assert len(components) == 2
        assert components[0].name == 'SuperLink'

        json_subsystem_creator = JSONSubsystemCreator(component_library, LOCALITY_CENTROID, PARAMETERS_DIFFERENT_COMPONENTS, constants=CONSTANTS, damage_input={})
        components = json_subsystem_creator.create_components_between_localities()
        assert len(components) == 0



    
    