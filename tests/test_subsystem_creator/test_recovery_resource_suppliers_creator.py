import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.subsystem_creator.recovery_resource_suppliers_creator import RecoveryResourceSuppliersCreator
from tests.test_subsystem_creator.test_subsystem_creator_inputs import MAIN_FILE_ALAMEDA, LOCALITY_CENTROID, PARAMETERS_ERC, PARAMETERS_ERC_2, CONSTANTS

class TestRecoveryResourceSuppliersCreator:

    @pytest.fixture
    def component_library(self):
        input_dict = read_json_file(MAIN_FILE_ALAMEDA)
        return main.form_component_library(input_dict)

    @pytest.fixture
    def recovery_resource_suppliers_creator(self, component_library):
        return RecoveryResourceSuppliersCreator(component_library, LOCALITY_CENTROID, PARAMETERS_ERC, constants=CONSTANTS, damage_input={})
    
    @pytest.fixture
    def recovery_resource_suppliers_creator_2(self, component_library):
        return RecoveryResourceSuppliersCreator(component_library, LOCALITY_CENTROID, PARAMETERS_ERC_2, constants=CONSTANTS, damage_input={})
    
    def test_create_components_in_localities(self, recovery_resource_suppliers_creator):
        components = recovery_resource_suppliers_creator.create_components_in_localities()
        assert len(components) == 1
        assert components[0].name == 'EmergencyResponseCenter'

    def test_create_components_in_localities_2(self, recovery_resource_suppliers_creator_2):
        components = recovery_resource_suppliers_creator_2.create_components_in_localities()
        assert len(components) == 2
        assert components[0].name == 'EmergencyResponseCenter'
        assert components[1].name == 'EmergencyResponseCenter'
        
