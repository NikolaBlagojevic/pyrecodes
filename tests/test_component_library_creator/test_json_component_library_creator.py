import pytest
from pyrecodes.component_library_creator.component_library_creator import ComponentLibraryCreator
from pyrecodes.component_library_creator.json_component_library_creator import JSONComponentLibraryCreator


class TestJSONComponentLibraryCreator_ThreeLocalitiesCommunity():
    COMPONENT_LIBRARY_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_ComponentLibrary.json'

    @pytest.fixture
    def component_library_creator(self):
        return JSONComponentLibraryCreator(self.COMPONENT_LIBRARY_FILE)

    def test_init(self, component_library_creator: ComponentLibraryCreator):
        for component_name, component_parameters in component_library_creator.file.items():
            assert 'ComponentClass' in component_parameters
            assert 'RecoveryModel' in component_parameters
            assert 'ClassName' in component_parameters['RecoveryModel']
            assert 'FileName' in component_parameters['RecoveryModel']
            assert 'Parameters' in component_parameters['RecoveryModel']
            assert'DamageFunctionalityRelation' in component_parameters['RecoveryModel']
            if component_name != 'BuildingStockUnit' and component_name != 'SuperLink':
                assert 'Supply' in component_parameters
                assert 'OperationDemand' in component_parameters

    def test_form_component_BTS1(self, component_library_creator: ComponentLibraryCreator):
        component_name = 'BaseTransceiverStation_1'
        component_parameters = component_library_creator.file[component_name]
        component = component_library_creator.form_component(component_name, component_parameters)
        assert type(component).__name__ == 'StandardiReCoDeSComponent'
        assert type(component.recovery_model).__name__ == 'ComponentLevelRecoveryActivitiesModel'
        assert component.recovery_model.recovery_activities['Repair'].duration == 10
        assert type(component.recovery_model.damage_to_functionality_relation).__name__ == 'ReverseBinary'
        assert component.supply['Supply']['Communication'].initial_amount == 1
        assert component.supply['Supply']['Communication'].current_amount == 1
        assert type(component.supply['Supply']['Communication'].component_functionality_to_amount).__name__ == 'Linear'
        assert type(component.supply['Supply']['Communication'].unmet_demand_to_amount).__name__ == 'Binary'
        assert component.demand['OperationDemand']['ElectricPower'].initial_amount == 1
        assert component.demand['OperationDemand']['ElectricPower'].current_amount == 1
        assert type(component.demand['OperationDemand'][
                                  'ElectricPower'].component_functionality_to_amount).__name__ == 'Linear'
    
    def test_form_component_BSU(self, component_library_creator: ComponentLibraryCreator):
        component_name = 'BuildingStockUnit'
        component_parameters = component_library_creator.file[component_name]
        component = component_library_creator.form_component(component_name, component_parameters)
        assert type(component).__name__ == 'BuildingWithEmergencyCalls'
        assert type(component.recovery_model).__name__ == 'ComponentLevelRecoveryActivitiesModel'
        assert component.recovery_model.recovery_activities['Repair'].duration == 10
        assert type(component.recovery_model.damage_to_functionality_relation).__name__ == 'ReverseLinear'
        assert component.demand['OperationDemand']['Communication'].initial_amount == 1
        assert component.demand['OperationDemand']['Communication'].current_amount == 1
        assert type(component.demand['OperationDemand'][
                                  'Communication'].component_functionality_to_amount).__name__ == 'Constant'
        assert component.demand['OperationDemand']['ElectricPower'].initial_amount == 1
        assert component.demand['OperationDemand']['ElectricPower'].current_amount == 1
        assert type(component.demand['OperationDemand'][
                                  'ElectricPower'].component_functionality_to_amount).__name__ == 'Linear'

    def test_form_library(self, component_library_creator: ComponentLibraryCreator):
        component_library = component_library_creator.form_library()
        component_type_names = ['BaseTransceiverStation_1', 'BaseTransceiverStation_2', 'ElectricPowerPlant',
                                'CoolingWaterFacility', 'BuildingStockUnit', 'SuperLink']
        components_in_library = [component_type_name in component_library for component_type_name in
                                 component_type_names]
        assert len(component_library) == 6 and all(components_in_library)
