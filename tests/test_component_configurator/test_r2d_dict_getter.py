import pytest
import copy
from pyrecodes.component_configurator.r2d_dict_getter import R2DDictGetter, R2DPipeDictGetter
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from test_component_configurator_inputs import MAIN_FILE
from pyrecodes.utilities import read_json_file
from pyrecodes import main

GENERAL_INFORMATION = {
    'Test': 'Test'
}
DAMAGE_INFORMATION = {
    'DamageTest': 'DamageTest'
}

@pytest.fixture()
def component_library():
    input_dict = read_json_file(MAIN_FILE)
    return main.form_component_library(input_dict)

@pytest.fixture()
def system_configuration() -> dict:
    input_dict = read_json_file(MAIN_FILE)
    system_configuration = read_json_file(input_dict['System']['SystemConfigurationFile'])
    return system_configuration

@pytest.fixture()
def component(component_library: dict):
    component = copy.deepcopy(component_library['DS3_Building'])
    component.general_information = GENERAL_INFORMATION
    component.damage_information = DAMAGE_INFORMATION
    return component

class TestR2DDictGetter:
    
    @pytest.fixture()
    def r2d_dict_getter(self, component) -> R2DDictGetter:
        return R2DDictGetter(component)
    
    def test_init(self, r2d_dict_getter: R2DDictGetter):
        assert isinstance(r2d_dict_getter.component, StandardiReCoDeSComponent)

    def test_get_dict(self, r2d_dict_getter: R2DDictGetter):
        r2d_dict = r2d_dict_getter.get_dict()
        assert r2d_dict['GeneralInformation'] == GENERAL_INFORMATION
        assert r2d_dict['Damage'] == {}


class TestR2DPipeDictGetter:
    
    @pytest.fixture()
    def r2d_pipe_dict_getter(self, component) -> R2DPipeDictGetter:
        return R2DPipeDictGetter(component)
    
    def test_get_dict(self, r2d_pipe_dict_getter):
        pipe_dict = r2d_pipe_dict_getter.get_dict()
        assert pipe_dict['GeneralInformation'] == GENERAL_INFORMATION
        assert pipe_dict['Damage'] == DAMAGE_INFORMATION