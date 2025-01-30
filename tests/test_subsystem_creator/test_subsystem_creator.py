import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.subsystem_creator.subsystem_creator import SubsystemCreator
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
from tests.test_subsystem_creator.test_subsystem_creator_inputs import MAIN_FILE, LOCALITY_CENTROID, PARAMETERS_BTS, CONSTANTS

class TestSubsystemCreator:

    @pytest.fixture
    def component_library(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.form_component_library(input_dict)
      
    @pytest.fixture
    def subsystem_creator(self, component_library) -> SubsystemCreator:
        return SubsystemCreator(component_library, LOCALITY_CENTROID, PARAMETERS_BTS, constants=CONSTANTS, damage_input={})
    
    def test_init(self, subsystem_creator):
        assert isinstance(subsystem_creator.component_library, dict)
        assert isinstance(subsystem_creator.locality, dict)
        assert isinstance(subsystem_creator.parameters, dict)
        assert isinstance(subsystem_creator.constants, dict)
        assert isinstance(subsystem_creator.damage_input, dict)
        assert isinstance(subsystem_creator.components, list)
        assert isinstance(subsystem_creator.component_configurator['Component'], ComponentConfigurator)

    def test_set_component_configurator(self, subsystem_creator):
        subsystem_creator.set_component_configurator()
        assert isinstance(subsystem_creator.component_configurator['Component'], ComponentConfigurator)

    def test_get_component_object(self, subsystem_creator):
        component_types = ['BaseTransceiverStation_2', 'SuperLink', 'BuildingStockUnit']
        for component_type in component_types:
            component = subsystem_creator.get_component_object(component_type)
            assert isinstance(component, StandardiReCoDeSComponent)
            assert component.name == component_type
    