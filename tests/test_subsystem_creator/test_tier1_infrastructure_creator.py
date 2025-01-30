import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.subsystem_creator.tier1_infrastructure_creator import Tier1InfrastructureCreator
from pyrecodes.component_configurator.tier1_interface_configurator import Tier1InterfaceConfigurator
from tests.test_subsystem_creator.test_subsystem_creator_inputs import MAIN_FILE_ALAMEDA, LOCALITY_CENTROID, PARAMETERS_INFRASTRUCTURE_INTERFACE, CONSTANTS

class TestTier1InfrastructureCreator:

    @pytest.fixture
    def component_library(self):
        input_dict = read_json_file(MAIN_FILE_ALAMEDA)
        return main.form_component_library(input_dict)
    
    @pytest.fixture
    def tier1_infrastructure_creator(self, component_library):
        return Tier1InfrastructureCreator(component_library, LOCALITY_CENTROID, PARAMETERS_INFRASTRUCTURE_INTERFACE, constants=CONSTANTS, damage_input={})
    
    def test_create_components_in_localities(self, tier1_infrastructure_creator):
        components = tier1_infrastructure_creator.create_components_in_localities()
        assert len(components) == 1
        assert components[0].name == 'ElectricPowerSupplySystem'

    def test_set_component_configurator(self, tier1_infrastructure_creator):
        tier1_infrastructure_creator.set_component_configurator()
        assert isinstance(tier1_infrastructure_creator.component_configurator['Component'], Tier1InterfaceConfigurator)