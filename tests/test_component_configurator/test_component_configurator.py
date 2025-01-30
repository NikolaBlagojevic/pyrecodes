from test_component_configurator_inputs import MAIN_FILE, SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE, LOCALITY_STRING, COMPONENT_DICT_REPAIR_COST_TESTS
import math
import pytest
import copy
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.system_creator.system_creator import SystemCreator
from pyrecodes.system_creator.concrete_system_creator import ConcreteSystemCreator
from pyrecodes.component_library_creator.json_component_library_creator import JSONComponentLibraryCreator
from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
from pyrecodes.component_configurator.repair_configurator import RepairConfigurator
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from tests.test_component_configurator.test_component_configurator_inputs import MAIN_FILE, SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE, LOCALITY_STRING, COMPONENT_DICT_REPAIR_COST_TESTS

class TestComponentConfigurator:

    @pytest.fixture()
    def system_creator(self) -> SystemCreator:
        return ConcreteSystemCreator()

    @pytest.fixture()
    def component_library(self) -> JSONComponentLibraryCreator:
        input_dict = read_json_file(MAIN_FILE)
        return main.form_component_library(input_dict)
    
    @pytest.fixture()
    def component_configurator(self) -> ComponentConfigurator:
        return ComponentConfigurator(SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE)
    
    @pytest.fixture()
    def DS3_building_component(self, component_library: dict) -> StandardiReCoDeSComponent:
        return copy.deepcopy(component_library['DS3_Building'])
    
    def test_init(self):
        component_configurator = ComponentConfigurator(SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE)
        assert component_configurator.system_level_data == SYSTEM_LEVEL_DATA_DICT
        assert component_configurator.recovery_time_steps == [i for i in range(0, 30, 1)] + [i for i in range(30, 80, 5)] + [i for i in range(80, 1000, 10)]

    def test_set_parameters(self, component_configurator: ComponentConfigurator, DS3_building_component: StandardiReCoDeSComponent):
        component_configurator.set_parameters(DS3_building_component, LOCALITY_STRING)
        assert DS3_building_component.locality == [10]
        assert DS3_building_component.recovery_model.recovery_time_steps == [i for i in range(0, 30, 1)] + [i for i in range(30, 80, 5)] + [i for i in range(80, 1000, 10)]

    def test_set_locality(self, component_configurator: ComponentConfigurator, DS3_building_component: StandardiReCoDeSComponent):
        component_configurator.set_locality(DS3_building_component, LOCALITY_STRING)
        assert DS3_building_component.locality == [10]
        component_configurator.set_locality(DS3_building_component, ['Locality 20'])
        assert DS3_building_component.locality == [20]
        component_configurator.set_locality(DS3_building_component, ['Locality -5'])
        assert DS3_building_component.locality == [-5]
        component_configurator.set_locality(DS3_building_component, ['Locality -5', 'Locality 10'])
        assert DS3_building_component.locality == [-5, 10]

    def test_set_recovery_time_steps(self, component_configurator: ComponentConfigurator, DS3_building_component: StandardiReCoDeSComponent):
        component_configurator.set_recovery_time_steps(DS3_building_component)
        assert DS3_building_component.recovery_model.recovery_time_steps == [i for i in range(0, 30, 1)] + [i for i in range(30, 80, 5)] + [i for i in range(80, 1000, 10)]
        component_configurator.set_recovery_time_stepping_rules([{"start": 10, "end": 20, "step": 2}])
        component_configurator.set_recovery_time_steps(DS3_building_component)
        assert DS3_building_component.recovery_model.recovery_time_steps == [i for i in range(10, 20, 2)]
        component_configurator.set_recovery_time_stepping_rules(None)
        component_configurator.set_recovery_time_steps(DS3_building_component)
        assert DS3_building_component.recovery_model.recovery_time_steps == [i for i in range(0, 100)]

    def test_configure_recovery_model(self, component_configurator: ComponentConfigurator, DS3_building_component: StandardiReCoDeSComponent):
        component_configurator.configure_recovery_model(DS3_building_component, component_data={}, component_damage_state=3)
        assert hasattr(component_configurator, 'repair_configurator') == False
        component_configurator.configure_recovery_model(DS3_building_component, component_data=COMPONENT_DICT_REPAIR_COST_TESTS, component_damage_state=3)
        assert isinstance(component_configurator.repair_configurator, RepairConfigurator)
        assert component_configurator.repair_configurator.component == DS3_building_component
        assert component_configurator.repair_configurator.system_level_data == SYSTEM_LEVEL_DATA_DICT
        assert DS3_building_component.recovery_model.recovery_activities['Financing'].demand['Money'].initial_amount == 0.1/DS3_building_component.recovery_model.recovery_activities['Financing'].duration
        assert math.isclose(DS3_building_component.recovery_model.recovery_activities['Repair'].duration, 120)

    def test_set_recovery_time_stepping_rules(self):
        component_configurator = ComponentConfigurator(SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE)
        assert component_configurator.recovery_time_steps == [i for i in range(0, 30, 1)] + [i for i in range(30, 80, 5)] + [i for i in range(80, 1000, 10)]
        component_configurator.set_recovery_time_stepping_rules(None)
        assert component_configurator.recovery_time_steps == [i for i in range(SYSTEM_LEVEL_DATA_DICT['START_TIME_STEP'], SYSTEM_LEVEL_DATA_DICT['MAX_TIME_STEP'])]
        component_configurator.set_recovery_time_stepping_rules([{"start": 10, "end": 20, "step": 2}])
        assert component_configurator.recovery_time_steps == [i for i in range(10, 20, 2)]
        component_configurator.set_recovery_time_stepping_rules(None)
        assert component_configurator.recovery_time_steps == [i for i in range(SYSTEM_LEVEL_DATA_DICT['START_TIME_STEP'], SYSTEM_LEVEL_DATA_DICT['MAX_TIME_STEP'])]

    def test_set_component_supply(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        component_configurator.set_component_supply(DS3_building_component, 'Shelter', 100)
        assert DS3_building_component.supply['Supply']['Shelter'].initial_amount == 100
        assert DS3_building_component.supply['Supply']['Shelter'].current_amount == 100
        component_configurator.set_component_supply(DS3_building_component, 'FunctionalHousing', 50)
        assert DS3_building_component.supply['Supply']['FunctionalHousing'].initial_amount == 50
        assert DS3_building_component.supply['Supply']['FunctionalHousing'].current_amount == 50
    
    def test_set_component_supply_wrong_resource(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        with pytest.raises(KeyError):
            component_configurator.set_component_supply(DS3_building_component, 'ElectricPower', 100)

    def test_set_component_supply_negative_amount(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        with pytest.raises(ValueError):
            component_configurator.set_component_supply(DS3_building_component, 'Shelter', -100)

    def test_set_component_operation_demand(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        component_configurator.set_component_operation_demand(DS3_building_component, 'Shelter', 100)
        assert DS3_building_component.demand['OperationDemand']['Shelter'].initial_amount == 100
        assert DS3_building_component.demand['OperationDemand']['Shelter'].current_amount == 100
        component_configurator.set_component_operation_demand(DS3_building_component, 'ElectricPower', 50)
        assert DS3_building_component.demand['OperationDemand']['ElectricPower'].initial_amount == 50
        assert DS3_building_component.demand['OperationDemand']['ElectricPower'].current_amount == 50
        component_configurator.set_component_operation_demand(DS3_building_component, 'ElectricPower', 70)
        assert DS3_building_component.demand['OperationDemand']['ElectricPower'].initial_amount == 70
        assert DS3_building_component.demand['OperationDemand']['ElectricPower'].current_amount == 70

    def test_set_component_operation_demand_wrong_resource(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        with pytest.raises(KeyError):
            component_configurator.set_component_operation_demand(DS3_building_component, 'DummyResource', 100)
    
    def test_set_component_operation_demand_negative_amount(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        with pytest.raises(ValueError):
            component_configurator.set_component_operation_demand(DS3_building_component, 'Shelter', -100)

    def test_set_component_recovery_demand(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        component_configurator.set_component_recovery_demand(DS3_building_component, 'Repair', 'RepairCrew_Buildings', 100)
        assert DS3_building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].initial_amount == 100
        assert DS3_building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].current_amount == 100
        component_configurator.set_component_recovery_demand(DS3_building_component, 'Repair', 'RepairCrew_Buildings', 50)
        assert DS3_building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].initial_amount == 50
        assert DS3_building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].current_amount == 50
        component_configurator.set_component_recovery_demand(DS3_building_component, 'RapidInspection', 'FirstResponderEngineer', 50)
        assert DS3_building_component.recovery_model.recovery_activities['RapidInspection'].demand['FirstResponderEngineer'].initial_amount == 50
        assert DS3_building_component.recovery_model.recovery_activities['RapidInspection'].demand['FirstResponderEngineer'].current_amount == 50
        component_configurator.set_component_recovery_demand(DS3_building_component, 'CleanUp', 'CleanUpCrew', 10)
        assert DS3_building_component.recovery_model.recovery_activities['CleanUp'].demand['CleanUpCrew'].initial_amount == 10
        assert DS3_building_component.recovery_model.recovery_activities['CleanUp'].demand['CleanUpCrew'].current_amount == 10

        component_configurator.set_component_recovery_demand(DS3_building_component, 'WrongActivity', 'CleanUpCrew', 20)
        assert DS3_building_component.recovery_model.recovery_activities['CleanUp'].demand['CleanUpCrew'].initial_amount == 10
        assert DS3_building_component.recovery_model.recovery_activities['CleanUp'].demand['CleanUpCrew'].current_amount == 10

    def test_set_component_recovery_demand_wrong_resource(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        with pytest.raises(KeyError):
            component_configurator.set_component_recovery_demand(DS3_building_component, 'Repair', 'DummyResource', 100)

    def test_set_component_recovery_demand_negative_amount(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        with pytest.raises(ValueError):
            component_configurator.set_component_recovery_demand(DS3_building_component, 'Repair', 'RepairCrew_Buildings', -100) 

    def test_set_recovery_demand_wrong_activity(self, DS3_building_component: StandardiReCoDeSComponent,
                                                    component_configurator: ComponentConfigurator):
        component_configurator.set_component_recovery_demand(DS3_building_component,
                                                                      'DummyActivity', 'RepairCrew', 100) 
        assert 'DummyActivity' not in DS3_building_component.recovery_model.recovery_activities.keys()

    def test_set_repair_cost(self, DS3_building_component: StandardiReCoDeSComponent, component_configurator: ComponentConfigurator):
        financing_duration = DS3_building_component.recovery_model.recovery_activities['Financing'].duration
        component_configurator.set_repair_configurator(DS3_building_component)
        component_configurator.set_repair_parameters(COMPONENT_DICT_REPAIR_COST_TESTS, 3)
        assert math.isclose(DS3_building_component.recovery_model.recovery_activities['Financing'].demand['Money'].initial_amount, 0.1/financing_duration)
        assert math.isclose(DS3_building_component.recovery_model.recovery_activities['Financing'].demand['Money'].current_amount, 0.1/financing_duration)
        COMPONENT_DICT_REPAIR_COST_TESTS['RecoveryModel']['Parameters']['Financing']['Demand'][0]['Amount'] = 200000
        component_configurator.set_repair_parameters(COMPONENT_DICT_REPAIR_COST_TESTS, 3)
        assert math.isclose(DS3_building_component.recovery_model.recovery_activities['Financing'].demand['Money'].initial_amount, 200000/financing_duration)
        assert math.isclose(DS3_building_component.recovery_model.recovery_activities['Financing'].demand['Money'].current_amount, 200000/financing_duration)
        DS3_building_component.recovery_model.recovery_activities['Financing'].duration = 5
        COMPONENT_DICT_REPAIR_COST_TESTS['RecoveryModel']['Parameters']['Financing']['Demand'][0]['Amount'] = 200000
        component_configurator.set_repair_parameters(COMPONENT_DICT_REPAIR_COST_TESTS, 3)
        assert math.isclose(DS3_building_component.recovery_model.recovery_activities['Financing'].demand['Money'].initial_amount, 200000/5)
        assert math.isclose(DS3_building_component.recovery_model.recovery_activities['Financing'].demand['Money'].current_amount, 200000/5)
