import math
import numpy as np
import pytest
from pyrecodes import Component
from pyrecodes import ComponentLibraryCreator
from pyrecodes import DistributionPriority
from pyrecodes import System
from pyrecodes import SystemCreator
from pyrecodes import ResourceDistributionModel
from pyrecodes import main

class TestUtilityDistributionModelConstructor:

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    DUMMY_PRIORITY = {"Type": "ComponentTypeBasedPriority",
                    "Parameters": [
                        [
                            "BaseTransceiverStation_1",
                            "OperationDemand"
                        ],
                        [
                            "ElectricPowerPlant",
                            "OperationDemand"
                        ],
                        [
                            "CoolingWaterFacility",
                            "OperationDemand"
                        ],
                        [
                            "BuildingStockUnit",
                            "OperationDemand"
                        ]
                    ]}
    
    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def distribution_model_constructor(self):
        return ResourceDistributionModel.UtilityDistributionModelConstructor()
    
    @pytest.fixture
    def distribution_model(self, system):
        distribution_model = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if resource_name == 'ElectricPower'}
        return distribution_model  
       
    def test_set_components(self, distribution_model, distribution_model_constructor, system: System.System):
        component_subset = system.components[:10]
        distribution_model_constructor.set_components(component_subset, distribution_model['ElectricPower'])
        assert distribution_model['ElectricPower'].components == component_subset

    def test_set_resource_name(self, distribution_model, distribution_model_constructor):
        distribution_model_constructor.set_resource_name('DummyResource', distribution_model['ElectricPower'])
        assert distribution_model['ElectricPower'].resource_name == 'DummyResource'

    def test_set_priority_model(self, distribution_model, distribution_model_constructor, system):
        distribution_model_constructor.set_priority_model('ElectricPower', self.DUMMY_PRIORITY, system.components, distribution_model['ElectricPower'])
        assert isinstance(distribution_model['ElectricPower'].priority, DistributionPriority.ComponentTypeBasedPriority)
    
    def test_set_system_matrix(self, distribution_model, distribution_model_constructor, system):
        distribution_model_constructor.set_system_matrix(system.components, 'ElectricPower', distribution_model['ElectricPower'])
        assert isinstance(distribution_model['ElectricPower'].system_matrix, ResourceDistributionModel.SingleResourceSystemMatrixCreator)

class TestTransferServiceDistributionModelConstructor:

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def distribution_model_constructor(self):
        return ResourceDistributionModel.TransferServiceDistributionModelConstructor()
    
    @pytest.fixture
    def distribution_model(self, system):
        distribution_model = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if resource_name == 'SuperTransferService'}
        return distribution_model
    
    def test_set_components(self, distribution_model, distribution_model_constructor, system: System.System):
        component_subset = system.components[:10]
        distribution_model_constructor.set_components(component_subset, distribution_model['SuperTransferService'])
        assert distribution_model['SuperTransferService'].components == component_subset
    
    def test_set_resource_name(self, distribution_model, distribution_model_constructor):
        distribution_model_constructor.set_resource_name('DummyResource', distribution_model['SuperTransferService'])
        assert distribution_model['SuperTransferService'].resource_name == 'DummyResource'
    
class TestSingleResourceSystemMatrixCreator():

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def distribution_models(self, system):
        distribution_models = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if 'TransferService' not in resource_name}
        return distribution_models    

    def test_initialize_system_matrix(self, distribution_models: dict, system: System.System):
        for distribution_model in distribution_models.values():
            distribution_model.system_matrix.initialize_system_matrix()
            assert np.all(distribution_model.system_matrix.matrix == np.zeros(
                (2 * len(system.components), distribution_models['ElectricPower'].system_matrix.NUM_COLUMN_SETS)))

    def test_calculate_num_rows_in_system_matrix(self, distribution_models: dict, system: System.System):
        assert distribution_models['ElectricPower'].system_matrix.calculate_num_rows_in_system_matrix() == len(
            system.components) * distribution_models['ElectricPower'].system_matrix.ROWS_PER_COMPONENT

    def test_calculate_num_columns_in_system_matrix(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].system_matrix.calculate_num_columns_in_system_matrix() == \
               distribution_models['ElectricPower'].system_matrix.NUM_COLUMN_SETS

    def test_fill_operation_demand_row(self, distribution_models: dict):
        for resource_name, distribution_model in distribution_models.items():
            for i, component in enumerate(distribution_model.components):
                supply = distribution_model.system_matrix.get_current_resource_amount(component, 'supply',
                                                                                      Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value)
                demand = distribution_model.system_matrix.get_current_resource_amount(component, 'demand',
                                                                                      Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value)
                target_row = [component.get_locality()[0], component.get_locality()[-1], supply, demand, 1.0]
                distribution_model.system_matrix.fill_operation_demand_row(i, component)
                assert np.all(target_row == distribution_model.system_matrix.matrix[i, :])

    def test_fill_recovery_demand_row(self, distribution_models: dict):
        for resource_name, distribution_model in distribution_models.items():
            for i, component in enumerate(distribution_model.components):
                recovery_demand = distribution_model.system_matrix.get_current_resource_amount(component, 'demand',
                                                                                               Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value)
                target_row = [component.get_locality()[0], component.get_locality()[-1], 0.0, recovery_demand, 1.0]
                distribution_model.system_matrix.fill_recovery_demand_row(i, component)
                assert np.all(target_row == distribution_model.system_matrix.matrix[
                                                      i + distribution_model.system_matrix.RECOVERY_DEMAND_ROW_OFFSET,
                                                      :])

    def test_fill_system_matrix_no_damage(self, distribution_models: dict):
        for distribution_model in distribution_models.values():
            distribution_model.system_matrix.fill_system_matrix()

        locality_matrix = []
        for component in distribution_model.components:
            locality_matrix.append([component.get_locality()[0], component.get_locality()[-1]])

        recovery_demand_matrix_part = np.concatenate(
            (locality_matrix, np.asarray([[0.0, 0.0, 1.0] for _ in distribution_models['ElectricPower'].components])),
            axis=1)
        target_power_matrix = np.concatenate(
            (np.asarray([[1, 1, 0.0, 1.0, 1.0], [1, 1, 5.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 1.0, 1.0],
                         [3, 3, 0.0, 1.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)

        assert np.all(target_power_matrix == distribution_models['ElectricPower'].system_matrix.matrix)
        target_communication_matrix = np.concatenate(
            (np.asarray([[1, 1, 1.0, 0.0, 1.0], [1, 1, 0.0, 1.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 1.0, 1.0],
                         [3, 3, 2.0, 0.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(target_communication_matrix == distribution_models['Communication'].system_matrix.matrix)

        target_cooling_water_matrix = np.concatenate(
            (np.asarray([[1, 1, 0.0, 0.0, 1.0], [1, 1, 0.0, 1.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 3.0, 0.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.0, 1.0],
                         [3, 3, 0.0, 0.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(target_cooling_water_matrix == distribution_models['CoolingWater'].system_matrix.matrix)

    def test_fill_system_matrix_with_damage(self, distribution_models: dict, system: System.System):
        system.set_initial_damage()
        system.time_step = 0
        system.update()
        for distribution_model in distribution_models.values():
            distribution_model.components = system.components
            distribution_model.fill_system_matrix()
        locality_matrix = []
        for component in distribution_model.components:
            locality_matrix.append([component.get_locality()[0], component.get_locality()[-1]])

        recovery_demand_matrix_part = np.concatenate(
            (locality_matrix, np.asarray([[0.0, 0.0, 1.0] for _ in distribution_models['ElectricPower'].components])),
            axis=1)
        target_power_matrix = np.concatenate(
            (np.asarray([[1, 1, 0.0, 1.0, 1.0], [1, 1, 3.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.6, 1.0],
                         [3, 3, 0.0, 0.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(np.isclose(target_power_matrix, distribution_models['ElectricPower'].system_matrix.matrix))

        target_communication_matrix = np.concatenate(
            (np.asarray([[1, 1, 1.0, 0.0, 1.0], [1, 1, 0.0, 1.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 1.0, 1.0],
                         [3, 3, 0.0, 0.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(np.isclose(target_communication_matrix, distribution_models['Communication'].system_matrix.matrix))

        target_cooling_water_matrix = np.concatenate(
            (np.asarray([[1, 1, 0.0, 0.0, 1.0], [1, 1, 0.0, 1.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 1.8, 0.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.0, 1.0],
                         [3, 3, 0.0, 0.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(np.isclose(target_cooling_water_matrix, distribution_models['CoolingWater'].system_matrix.matrix))

    def test_get_component_properties(self, distribution_models: dict):
        
        electric_power_plant = distribution_models['ElectricPower'].components[1]
        component_properties = distribution_models['ElectricPower'].system_matrix.get_component_properties(
            electric_power_plant, [['supply', 'Supply'], ['demand', 'OperationDemand']])
        assert all(component_properties == [1, 1, 5, 0, 1])
        component_properties = distribution_models['ElectricPower'].system_matrix.get_component_properties(
            electric_power_plant, [['supply', 'Supply'], ['demand', 'RecoveryDemand']])
        assert all(component_properties == [1, 1, 5, 0, 1])
        component_properties = distribution_models['CoolingWater'].system_matrix.get_component_properties(
            electric_power_plant, [['supply', 'Supply'], ['demand', 'OperationDemand']])
        assert all(component_properties == [1, 1, 0, 1, 1])
        component_properties = distribution_models['Communication'].system_matrix.get_component_properties(
            electric_power_plant, [['supply', 'Supply'], ['demand', 'OperationDemand']])
        assert all(component_properties == [1, 1, 0, 1, 1])

    def test_get_current_resource_amount(self, distribution_models: dict):
        building_stock_unit = distribution_models['ElectricPower'].components[7]
        assert distribution_models['ElectricPower'].system_matrix.get_current_resource_amount(building_stock_unit,
                                                                                           'supply', 'Supply') == 0.0
        assert distribution_models['ElectricPower'].system_matrix.get_current_resource_amount(building_stock_unit,
                                                                                           'demand',
                                                                                           'OperationDemand') == 1.0
        assert distribution_models['CoolingWater'].system_matrix.get_current_resource_amount(building_stock_unit, 'demand',
                                                                                          'OperationDemand') == 0.0
        assert distribution_models['Communication'].system_matrix.get_current_resource_amount(building_stock_unit,
                                                                                           'demand',
                                                                                           'OperationDemand') == 1.0

    def test_set_demand_met_indicator(self, distribution_models: dict):
        distribution_models['ElectricPower'].system_matrix.set_demand_met_indicator(0, 0.5)
        distribution_models['CoolingWater'].system_matrix.set_demand_met_indicator(0, 0.5)
        distribution_models['Communication'].system_matrix.set_demand_met_indicator(0, 0.5)
        assert all([distribution_models['ElectricPower'].system_matrix.matrix[
                        0, distribution_models['ElectricPower'].system_matrix.DEMAND_MET_COL_ID] == 0.5,
                    distribution_models['CoolingWater'].system_matrix.matrix[
                        0, distribution_models['CoolingWater'].system_matrix.DEMAND_MET_COL_ID] == 0.5,
                    distribution_models['Communication'].system_matrix.matrix[
                        0, distribution_models['Communication'].system_matrix.DEMAND_MET_COL_ID] == 0.5])

    def test_get_demand(self, distribution_models: dict):
        assert all([distribution_models['ElectricPower'].system_matrix.get_demand(0) ==
                    distribution_models['ElectricPower'].system_matrix.matrix[
                        0, distribution_models['ElectricPower'].system_matrix.DEMAND_COL_ID],
                    distribution_models['Communication'].system_matrix.get_demand(0) ==
                    distribution_models['Communication'].system_matrix.matrix[
                        0, distribution_models['Communication'].system_matrix.DEMAND_COL_ID],
                    distribution_models['CoolingWater'].system_matrix.get_demand(0) ==
                    distribution_models['CoolingWater'].system_matrix.matrix[
                        0, distribution_models['CoolingWater'].system_matrix.DEMAND_COL_ID]])

    def test_get_initial_demand_met_indicators(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].system_matrix.get_initial_demand_met_indicator() == 1.0


class TestUtilityDistributionModel_ThreeLocalitiesCommunity():

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def distribution_models(self, system):
        distribution_models = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if 'TransferService' not in resource_name}
        return distribution_models 

    def test_init_(self, distribution_models: dict, system: System.System):
        assert distribution_models['ElectricPower'].system_matrix.RECOVERY_DEMAND_ROW_OFFSET == len(system.components)
        assert isinstance(distribution_models['ElectricPower'].priority, DistributionPriority.ComponentBasedPriority)
        assert isinstance(distribution_models['ElectricPower'].transfer_service_distribution_model, ResourceDistributionModel.TransferServiceDistributionModelPotentialPathSets)

    def test_distribute(self, distribution_models: dict, system: System.System):
        distribution_models['Communication'].distribute()
        assert np.all(distribution_models['Communication'].system_matrix.matrix[:, -1] == 1.0)
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        distribution_models['Communication'].components = system.components
        distribution_models['Communication'].distribute()
        assert np.all(distribution_models['Communication'].system_matrix.matrix[7, -1] == 0.0)

    def test_fill_system_matrix(self, distribution_models: dict, system: System.System):
        locality_matrix = []
        for component in distribution_models['ElectricPower'].components:
            locality_matrix.append([component.get_locality()[0], component.get_locality()[-1]])
        recovery_demand_matrix_part = np.concatenate(
            (locality_matrix, np.asarray([[0.0, 0.0, 1.0] for _ in distribution_models['ElectricPower'].components])),
            axis=1)
        target_initial_matrix_no_damage = np.concatenate(
            (np.asarray([[1, 1, 0.0, 1.0, 1.0], [1, 1, 5.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 1.0, 1.0],
                         [3, 3, 0.0, 1.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        distribution_models['ElectricPower'].fill_system_matrix()
        assert np.all(distribution_models['ElectricPower'].system_matrix.matrix == target_initial_matrix_no_damage)

        target_initial_matrix_with_damage = np.concatenate(
            (np.asarray([[1, 1, 0.0, 1.0, 1.0], [1, 1, 3.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.6, 1.0],
                         [3, 3, 0.0, 0.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        
        system.set_initial_damage()
        system.time_step = 0
        system.update()
        distribution_models['ElectricPower'].components = system.components
        distribution_models['ElectricPower'].fill_system_matrix()
        assert np.all(distribution_models['ElectricPower'].system_matrix.matrix == target_initial_matrix_with_damage)
        
    def test_get_component_priorities(self, distribution_models: dict):
        target_priorities = [1, 0, 4, 8, 7]
        target_demand_types = ['OperationDemand' for _ in range(len(target_priorities))]
        component_rows, component_demand_types = distribution_models['ElectricPower'].get_component_priorities()
        assert target_priorities == component_rows
        assert target_demand_types == component_demand_types
    
    def test_set_component_row_based_on_demand_type(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].set_component_row_based_on_demand_type([1], ['OperationDemand']) == [1]
        assert distribution_models['ElectricPower'].set_component_row_based_on_demand_type([1], ['RecoveryDemand']) == [1 + len(distribution_models['ElectricPower'].components)]                          

    def test_add_supplier(self, distribution_models: dict):
        power_plant_row_id = 1
        target_component_is_supplier = [True, False, False]
        target_suppliers_length = [1, 0, 0]
        for target_bool, target_length, distribution_model in zip(target_component_is_supplier, target_suppliers_length,
                                                                  distribution_models.values()):
            distribution_model.system_matrix.fill_system_matrix()
            suppliers = []
            suppliers, component_is_supplier = distribution_model.add_supplier(power_plant_row_id, suppliers)
            assert len(suppliers) == target_length
            assert component_is_supplier == target_bool

    def test_add_supplier_with_damage(self, distribution_models: dict, system: System.System):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        target_damaged_supply_values = [3.0, 1.8, 1.0]
        for target_value, distribution_model in zip(target_damaged_supply_values, distribution_models.values()):
            distribution_model.components = system.components
            distribution_model.fill_system_matrix()
            suppliers = []
            for component_row_id in range(len(distribution_model.components)):
                suppliers, component_is_supplier = distribution_model.add_supplier(component_row_id, suppliers)
            assert math.isclose(suppliers[0]['CurrentSupply'], target_value)
    
    def test_meet_component_demand_single_supplier(self, distribution_models: dict):
        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 5.0, 'ConsumedAmount': 0,
                      'ComponentRowID': 0}]
        componet_row_id = 7
        component_demand_type = 'OperationDemand'
        suppliers = distribution_models['ElectricPower'].meet_component_demand(suppliers, componet_row_id, component_demand_type)
        assert math.isclose(suppliers[0]['CurrentSupply'], 4.0)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 1.0)

        component_row_id = 4
        suppliers = distribution_models['ElectricPower'].meet_component_demand(suppliers, component_row_id, component_demand_type)
        assert math.isclose(suppliers[0]['CurrentSupply'], 3.0)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 2.0)

        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 0.0, 'ConsumedAmount': 0,
                      'ComponentRowID': 0}]
        
        component_row_id = 4
        suppliers = distribution_models['ElectricPower'].meet_component_demand(suppliers, componet_row_id, component_demand_type)
        assert math.isclose(suppliers[0]['CurrentSupply'], 0.0)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 0.0)
    
    def test_meet_component_demand_single_supplier(self, distribution_models: dict):
        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 5.0, 'ConsumedAmount': 0,
                      'ComponentRowID': 0}]
        componet_row_id = 7
        component_demand_type = 'OperationDemand'
        distribution_models['ElectricPower'].fill_system_matrix()

        suppliers = distribution_models['ElectricPower'].meet_component_demand(suppliers, componet_row_id, component_demand_type)
        assert math.isclose(suppliers[0]['CurrentSupply'], 4.0)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 1.0)

        component_row_id = 4
        suppliers = distribution_models['ElectricPower'].meet_component_demand(suppliers, component_row_id, component_demand_type)
        assert math.isclose(suppliers[0]['CurrentSupply'], 3.0)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 2.0)

        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 0.0, 'ConsumedAmount': 0,
                      'ComponentRowID': 0}]
        
        component_row_id = 4
        suppliers = distribution_models['ElectricPower'].meet_component_demand(suppliers, componet_row_id, component_demand_type)
        assert math.isclose(suppliers[0]['CurrentSupply'], 0.0)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 0.0)
    
    def test_meet_component_demand_multiple_suppliers(self, distribution_models: dict):
        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 0.5, 'ConsumedAmount': 0,
                      'ComponentRowID': 0},
                      {'StartLocality': 1, 'EndLocality': 1,
                       'CurrentSupply': 1.0, 'ConsumedAmount': 0,
                       'ComponentRowID': 8}]
        component_row_id = 7
        component_demand_type = 'OperationDemand'
        distribution_models['ElectricPower'].fill_system_matrix()

        suppliers = distribution_models['ElectricPower'].meet_component_demand(suppliers, component_row_id, component_demand_type)
        assert math.isclose(suppliers[0]['CurrentSupply'], 0.0)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 0.5)
        assert math.isclose(suppliers[1]['CurrentSupply'], 0.5)
        assert math.isclose(suppliers[1]['ConsumedAmount'], 0.5)

        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 0, 'ConsumedAmount': 0,
                      'ComponentRowID': 0},
                      {'StartLocality': 1, 'EndLocality': 1,
                       'CurrentSupply': 1.0, 'ConsumedAmount': 0,
                       'ComponentRowID': 8}]

        suppliers = distribution_models['ElectricPower'].meet_component_demand(suppliers, component_row_id, component_demand_type)
        assert math.isclose(suppliers[0]['CurrentSupply'], 0.0)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 0.0)
        assert math.isclose(suppliers[1]['CurrentSupply'], 0.0)
        assert math.isclose(suppliers[1]['ConsumedAmount'], 1.0)        

    def test_suppliers_meet_component_demand_no_damage(self, distribution_models: dict):
        building_stock_id = 7
        component_demand_type = 'OperationDemand'
        for distribution_model in distribution_models.values():
            distribution_model.fill_system_matrix()
            suppliers = []
            component_priorities, component_demand_types = distribution_model.get_component_priorities()
            for component_row_id, component_demand_type in zip(component_priorities, component_demand_types):                
                suppliers, component_is_supplier = distribution_model.add_supplier(component_row_id, suppliers) 
            component_demand = distribution_model.get_demand(building_stock_id)
            component_localities = [distribution_model.system_matrix.matrix[building_stock_id, distribution_model.system_matrix.START_LOCALITY_COL_ID],
                                distribution_model.system_matrix.matrix[building_stock_id, distribution_model.system_matrix.END_LOCALITY_COL_ID]]
            transfer_service_demand = distribution_model.get_transfer_service_demand(building_stock_id, component_demand_type)
            demand_after_distribution, suppliers= distribution_model.suppliers_meet_component_demand(suppliers, component_demand, component_localities, transfer_service_demand)
            assert math.isclose(demand_after_distribution, 0, abs_tol=1e-5)

    def test_suppliers_meet_component_demand_with_damage(self, distribution_models: dict, system: System.System):
        system.set_initial_damage()
        system.time_step = 0
        system.update()
        building_stock_id = 7
        component_demand_type = 'OperationDemand'
        target_demand_values = [0.0, 0.0, 1.0]
        set_supplier_amount = [2.0, 0.0, 0.0]
        for target_value, supplier_amount, distribution_model in zip(target_demand_values, set_supplier_amount,
                                                                     distribution_models.values()):
            distribution_model.components = system.components
            distribution_model.fill_system_matrix()
            suppliers = [{'StartLocality': 1, 'EndLocality': 1, 
                              'CurrentSupply': supplier_amount, 'ConsumedAmount': 0, 
                              'ComponentRowID': 0}]
            component_demand = distribution_model.get_demand(building_stock_id)
            component_localities = [distribution_model.system_matrix.matrix[building_stock_id, distribution_model.system_matrix.START_LOCALITY_COL_ID],
                                distribution_model.system_matrix.matrix[building_stock_id, distribution_model.system_matrix.END_LOCALITY_COL_ID]]
            transfer_service_demand = distribution_model.get_transfer_service_demand(building_stock_id, component_demand_type)
            demand_after_distribution, suppliers= distribution_model.suppliers_meet_component_demand(suppliers, 
                                                                                                    component_demand, 
                                                                                                    component_localities, 
                                                                                                    transfer_service_demand)
            assert math.isclose(demand_after_distribution, target_value, abs_tol=1e-10)

    def test_update_consumed_amounts(self, distribution_models: dict):
        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 0.5, 'ConsumedAmount': 0,
                      'ComponentRowID': 0}]
        initial_suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                              'CurrentSupply': 5.0, 'ConsumedAmount': 0,
                              'ComponentRowID': 0}]
        distribution_models['ElectricPower'].update_consumed_amounts(suppliers, initial_suppliers)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 4.5)
        distribution_models['ElectricPower'].update_consumed_amounts(suppliers, initial_suppliers)
        assert math.isclose(suppliers[0]['ConsumedAmount'], 9.0)
    
    def test_update_suppliers_based_on_consumption(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].components[1].supply['Supply']['ElectricPower'].current_amount == 5.0
        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 0.5, 'ConsumedAmount': 1.0,
                      'ComponentRowID': 1}]
        distribution_models['ElectricPower'].update_suppliers_based_on_consumption(suppliers)
        assert distribution_models['ElectricPower'].components[1].supply['Supply']['ElectricPower'].current_amount == 5.0
        
    def test_reduce_component_supply(self, distribution_models: dict):
        power_plant_row_id = 1
        base_station_row_id = 0
        percent_of_met_demand = 0.4
        reduced_supply_of_the_power_plant = [0.0, 0.0, 0.0]
        reduced_supply_of_the_base_station = [0.0, 0.0, 0.0]
        for power_plant_supply, base_station_supply, distribution_model in zip(reduced_supply_of_the_power_plant,
                                                                               reduced_supply_of_the_base_station,
                                                                               distribution_models.values()):
            distribution_model.reduce_component_supply(power_plant_row_id, percent_of_met_demand)
            distribution_model.reduce_component_supply(base_station_row_id, percent_of_met_demand)
            assert math.isclose(distribution_model.system_matrix.get_current_resource_amount(
                distribution_model.components[power_plant_row_id], Component.SupplyOrDemand.SUPPLY.value, 'Supply'),
                power_plant_supply)
            assert math.isclose(distribution_model.system_matrix.get_current_resource_amount(
                distribution_model.components[base_station_row_id], Component.SupplyOrDemand.SUPPLY.value, 'Supply'),
                base_station_supply)

    def test_get_demand(self, distribution_models: dict):
        demand_of_the_power_plant = [0.0, 1.0, 1.0]
        power_plant_row_id = 1
        for target_demand, distribution_model in zip(demand_of_the_power_plant, distribution_models.values()):
            distribution_model.fill_system_matrix()
            assert distribution_model.get_demand(power_plant_row_id) == target_demand

    def test_get_transfer_service_demand(self, distribution_models: dict):
        component_row_BSU = 7
        component_row_EPP = 1
        component_demand_type = 'OperationDemand'
        assert distribution_models['ElectricPower'].get_transfer_service_demand(component_row_BSU, component_demand_type) == 1.0
        assert distribution_models['Communication'].get_transfer_service_demand(component_row_BSU, component_demand_type) == 1.0
        assert distribution_models['CoolingWater'].get_transfer_service_demand(component_row_EPP, component_demand_type) == 1.0

    def test_modify_demand_to_account_for_resource_transfer(self, distribution_models: dict):
        # TODO: Improve the test. Test more cases. Use Virtual Community.
        supplier_start_locality = 1
        supplier_end_locality = 1
        component_demand = 10
        component_localities = [3, 3]
        transfer_service_demand = 5
        assert distribution_models['ElectricPower'].modify_demand_to_account_for_resource_transfer(supplier_start_locality,                                                                                                   
                                                                                                    supplier_end_locality,
                                                                                                    component_demand,
                                                                                                    component_localities,
                                                                                                    transfer_service_demand)[0] == component_demand
        for component in distribution_models['ElectricPower'].components:
            if component.name == 'SuperLink':
                component.set_initial_damage_level(1.0)
                component.update(1)
        assert distribution_models['ElectricPower'].modify_demand_to_account_for_resource_transfer(supplier_start_locality,
                                                                                                    supplier_end_locality,
                                                                                                    component_demand,
                                                                                                    component_localities,
                                                                                                    transfer_service_demand)[0] == math.inf

    def test_get_locality_pairs(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].get_locality_pairs(1, 1, [1, 1]) == [[1, 1]]
        assert distribution_models['ElectricPower'].get_locality_pairs(1, 2, [1, 1]) == [[1, 1], [2, 1]]
        assert distribution_models['ElectricPower'].get_locality_pairs(1, 3, [1, 2]) == [[1, 1], [1, 2], [3, 1], [3, 2]]
        assert distribution_models['ElectricPower'].get_locality_pairs(1, 3, [1, 3]) == [[1, 1], [1, 3], [3, 1], [3, 3]]
        assert distribution_models['ElectricPower'].get_locality_pairs(2, 1, [2, 2]) == [[1, 2], [2, 2]]
    
    def test_get_best_path_functionality(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].get_best_path_functionality([[1, 1]], 10) == 1.0
        assert distribution_models['ElectricPower'].get_best_path_functionality([[1, 2], [1, 3]], 10) == 1.0

        for component in distribution_models['ElectricPower'].components:
            if component.name == 'SuperLink':
                component.set_initial_damage_level(1.0)
                component.update(1)
            
        assert distribution_models['ElectricPower'].get_best_path_functionality([[1, 1], [1, 2]], 10) == 1.0
        assert distribution_models['ElectricPower'].get_best_path_functionality([[1, 2], [1, 3]], 10) == 0.0
        assert distribution_models['ElectricPower'].get_best_path_functionality([[1, 3], [2, 1]], 10) == 0.0
    
    def test_get_path_functionality(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].get_path_functionality(1, 2, 10) == 1.0
        assert distribution_models['ElectricPower'].get_path_functionality(1, 1, 10) == 1.0
        assert distribution_models['ElectricPower'].get_path_functionality(1, 3, 1001) == 0.0

        for component in distribution_models['ElectricPower'].components:
            if component.name == 'SuperLink':
                component.set_initial_damage_level(1.0)
                component.update(1)
            
        assert distribution_models['ElectricPower'].get_path_functionality(1, 1, 1000) == 1.0
        assert distribution_models['ElectricPower'].get_path_functionality(1, 2, 1) == 0.0

    def test_get_optimal_path(self, distribution_models: dict):
        distribution_models['ElectricPower'].transfer_service_distribution_model.set_potential_paths('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_potential_path_sets.json')
        assert distribution_models['ElectricPower'].get_optimal_path(2, 1) == (1000, 0)
        assert distribution_models['Communication'].get_optimal_path(2, 1) == (math.inf, None)

        for component in distribution_models['ElectricPower'].components:
            if component.name == 'SuperLink':
                component.set_initial_damage_level(1.0)
                component.update(1)
        
        assert distribution_models['ElectricPower'].get_optimal_path(2, 1) == (0, 0)

    def test_get_scope(self, distribution_models: dict):
        distribution_models['ElectricPower'].fill_system_matrix()
        
        target_all_components_id = list(range(2 * len(distribution_models['ElectricPower'].components)))
        assert distribution_models['ElectricPower'].get_scope() == target_all_components_id

        target_locality_1_components_id = [0, 1, 2, 3, 5, 9, 11, 12, 13, 14, 16, 20]
        assert distribution_models['ElectricPower'].get_scope('Locality 1')[0].tolist() == target_locality_1_components_id

        with pytest.raises(ValueError):
            distribution_models['ElectricPower'].get_scope('1')
    
    def test_get_total_supply_no_damage(self, distribution_models: dict):
        target_supplies = [5.0, 3.0, 3.0]
        for target_supply, distribution_model in zip(target_supplies, distribution_models.values()):
            distribution_model.fill_system_matrix()
            current_supply = distribution_model.get_total_supply()
            assert math.isclose(target_supply, current_supply)

    def test_get_total_supply_with_damage(self, distribution_models: dict, system: System.System):
        target_supplies = [3.0, 1.8, 1.0]
        system.set_initial_damage()
        system.time_step = 0
        system.update()
        for target_supply, distribution_model in zip(target_supplies, distribution_models.values()):
            distribution_model.components = system.components
            distribution_model.fill_system_matrix()
            current_supply = distribution_model.get_total_supply()
            assert math.isclose(target_supply, current_supply)

    def test_get_total_demand_no_damage(self, distribution_models: dict):
        target_demands = [4.0, 1.0, 3.0]
        for target_demand, distribution_model in zip(target_demands, distribution_models.values()):
            distribution_model.fill_system_matrix()
            current_demand = distribution_model.get_total_demand()
            assert math.isclose(target_demand, current_demand)

    def test_get_total_demand_with_damage(self, distribution_models: dict, system: System.System):
        target_demands = [2.6, 1.0, 12.0]
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        for target_demand, distribution_model in zip(target_demands, distribution_models.values()):
            distribution_model.components = system.components
            distribution_model.fill_system_matrix()
            current_demand = distribution_model.get_total_demand()
            assert math.isclose(target_demand, current_demand)

    def test_get_system_consumption_no_damage(self, distribution_models: dict):
        target_consumptions = [4.0, 1.0, 3.0]
        for target_consumption, distribution_model in zip(target_consumptions, distribution_models.values()):
            distribution_model.fill_system_matrix()
            current_consumption = distribution_model.get_total_consumption()
            assert math.isclose(target_consumption, current_consumption)

    def test_get_total_consumption_with_damage(self, distribution_models: dict, system: System.System):
        target_demands = [2.6, 1.0, 1.0]
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        for target_demand, distribution_model in zip(target_demands, distribution_models.values()):
            distribution_model.components = system.components
            distribution_model.distribute()
            current_consumption = distribution_model.get_total_consumption()
            assert math.isclose(target_demand, current_consumption)

class TestUtilityDistributionModel_NorthEast_SF():

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Main.json'
    RECOVERY_RESOURCE_SUPPLY = {"FirstResponderEngineer": 5,
                                "SeniorEngineer": 4,
                                "Contractor": 10,
                                "Money": 5500000000,
                                "PlanCheckEngineeringTeam": 10,
                                "SitePreparationCrew": 10,
                                "CleanUpCrew": 10,
                                "EngineeringDesignTeam": 10,
                                "DemolitionCrew": 10,
                                "RepairCrew": 500}
   
    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        system =  main.create_system(input_dict)
        self.set_recovery_resource_supply(system.components)
        emergency_response_center = system.components[0]
        return system

    @pytest.fixture
    def distribution_models(self, system):
        distribution_models = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if 'TransferService' not in resource_name}
        return distribution_models 

    def set_recovery_resource_supply(self, components: list([Component.Component])):
        emergency_response_center = components[0]
        for resource_name, resource_amount in self.RECOVERY_RESOURCE_SUPPLY.items():
            emergency_response_center.supply['Supply'][resource_name].initial_amount = resource_amount
            emergency_response_center.supply['Supply'][resource_name].current_amount = resource_amount

    def test_housing_distribution_no_damage(self, distribution_models: dict):
        distribution_models['Shelter'].distribute()
        target_total_supply = 0
        for component in distribution_models['Shelter'].components[1:]:
            assert component.supply['Supply']['Shelter'].current_amount == component.demand['OperationDemand'][
                    'Shelter'].current_amount
            target_total_supply += component.supply['Supply']['Shelter'].current_amount
        assert target_total_supply == distribution_models['Shelter'].get_total_consumption()
        assert target_total_supply == distribution_models['Shelter'].get_total_supply()

    def test_housing_distribution_with_damage(self, system: System.System, distribution_models: dict):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        distribution_models['Shelter'].components = system.components
        distribution_models['Shelter'].distribute()
        target_total_supply = 0
        target_total_demand = 0
        for component in distribution_models['Shelter'].components[1:]:      
            if component.name in ['DS0_ResidentialBuilding', 'DS1_ResidentialBuilding']:
                assert component.supply['Supply']['Shelter'].current_amount == component.demand['OperationDemand']['Shelter'].current_amount
                target_total_supply += component.supply['Supply']['Shelter'].current_amount
            else:
                assert math.isclose(component.supply['Supply']['Shelter'].current_amount, 0)
            assert component.supply['Supply']['Shelter'].initial_amount == component.demand['OperationDemand']['Shelter'].current_amount
            target_total_demand += component.demand['OperationDemand']['Shelter'].current_amount

        assert math.isclose(target_total_supply, distribution_models['Shelter'].get_total_consumption())
        assert math.isclose(target_total_supply, distribution_models['Shelter'].get_total_supply())
        assert target_total_demand == distribution_models['Shelter'].get_total_demand()

    def test_recovery_resource_distribution_no_damage(self, distribution_models: dict):
        for resource_name, distribution_model in distribution_models.items():
            if not (resource_name == 'Shelter'):
                distribution_model.distribute()
                assert distribution_model.get_total_consumption() == 0
                assert distribution_model.get_total_demand() == 0
                assert distribution_model.get_total_supply() == self.RECOVERY_RESOURCE_SUPPLY[resource_name]

        for component in distribution_models['Shelter'].components:
            for recovery_activity in component.recovery_model.recovery_activities.values():
                assert list(recovery_activity.demand_met.values())[0] == 1.0

    def test_rapid_inspection_distribution_with_damage(self, system: System.System, distribution_models: dict):
        system.set_initial_damage()
        system.time_step = 0
        system.update()  
        buildings_need_inspection = 14
        distribution_models['FirstResponderEngineer'].components = system.components
        distribution_models['FirstResponderEngineer'].distribute()
        assert math.isclose(distribution_models['FirstResponderEngineer'].get_total_consumption(), buildings_need_inspection*0.1)
        assert math.isclose(distribution_models['FirstResponderEngineer'].get_total_demand(), buildings_need_inspection*0.1)
        assert distribution_models['FirstResponderEngineer'].get_total_supply() == self.RECOVERY_RESOURCE_SUPPLY['FirstResponderEngineer']
        
        for component in distribution_models['FirstResponderEngineer'].components:
            for recovery_activity in component.recovery_model.recovery_activities.values():
                assert list(recovery_activity.demand_met.values())[0] == 1.0

    def test_detailed_inspection_distribution_with_damage(self, system: System.System, distribution_models: dict):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.recover()   
        system.time_step = 2
        system.update()                         
        demand_per_component = 2
        components_with_demand_id = [component_id for component_id, component in enumerate(system.components) if 'SeniorEngineer' in component.demand['RecoveryDemand']]         
        distribution_models['SeniorEngineer'].components = system.components
        distribution_models['SeniorEngineer'].distribute()
        component_priorities, demand_type = distribution_models['SeniorEngineer'].get_component_priorities()              
        assert math.isclose(distribution_models['SeniorEngineer'].get_total_consumption(), min(self.RECOVERY_RESOURCE_SUPPLY['SeniorEngineer'], len(components_with_demand_id)*demand_per_component))
        assert math.isclose(distribution_models['SeniorEngineer'].get_total_demand(), len(components_with_demand_id)*demand_per_component)
        assert distribution_models['SeniorEngineer'].get_total_supply() == self.RECOVERY_RESOURCE_SUPPLY['SeniorEngineer']
        num_components_with_met_demand = math.floor(self.RECOVERY_RESOURCE_SUPPLY['SeniorEngineer'] / demand_per_component)
        counter = 0
        for component_offset_id in component_priorities[1:]:  
            component_id = component_offset_id - distribution_models['SeniorEngineer'].system_matrix.RECOVERY_DEMAND_ROW_OFFSET
            component = system.components[component_id]                        
            if component.name in ['DS2_ResidentialBuilding', 'DS3_ResidentialBuilding', 'DS4_ResidentialBuilding'] and component_id in components_with_demand_id:
                if counter < num_components_with_met_demand:
                    assert list(component.recovery_model.recovery_activities['DetailedInspection'].demand_met.values())[0] == 1.0
                    counter += 1
                else:
                    assert list(component.recovery_model.recovery_activities['DetailedInspection'].demand_met.values())[0] == 0.0
        
    def test_consumable_resource_with_money(self, system: System.System, distribution_models: dict):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        total_money_demand = 0
        for component in system.components:
            for recovery_activity in component.recovery_model.recovery_activities.values():
                if recovery_activity.name != 'Financing' or recovery_activity.name != 'Repair':
                    recovery_activity.level = 1.0
                elif recovery_activity.name == 'Financing':
                    total_money_demand += recovery_activity.demand['Money'].current_amount                   
        system.update()
        distribution_models['Money'].components = system.components
        distribution_models['Money'].distribute()
        target_consumed_supply = self.RECOVERY_RESOURCE_SUPPLY['Money'] - total_money_demand
        assert math.isclose(distribution_models['Money'].components[0].supply['Supply']['Money'].current_amount, target_consumed_supply)

class TestTransferServiceDistributionModelPotentialPathSet:

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        system =  main.create_system(input_dict)
        return system
    
    @pytest.fixture
    def distribution_models(self, system):
        distribution_models = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if 'TransferService' in resource_name}
        return distribution_models

    def test_find_connecting_link(self, distribution_models: dict):
        path_string = 'from 1 to 3'
        start_locality = 1
        next_locality = 3
        distribution_models['SuperTransferService'].find_connecting_link(path_string, start_locality, next_locality)
        assert distribution_models['SuperTransferService'].potential_paths[path_string][-1][-1].locality[0] == 1
        assert distribution_models['SuperTransferService'].potential_paths[path_string][-1][-1].locality[1] == 3

        path_string = 'from 2 to 3'
        start_locality = 2
        next_locality = 3
        distribution_models['SuperTransferService'].find_connecting_link(path_string, start_locality, next_locality)
        assert distribution_models['SuperTransferService'].potential_paths[path_string][-1][-1].locality[0] == 2
        assert distribution_models['SuperTransferService'].potential_paths[path_string][-1][-1].locality[1] == 3

    def test_get_start_end_locality_from_path_string(self, distribution_models: dict):
        path_string = 'from 10 to 20'
        start_locality, end_locality = distribution_models['SuperTransferService'].get_start_end_locality_from_path_string(path_string)
        assert start_locality == 10
        assert end_locality == 20
    
    def test_get_path_supply(self, distribution_models: dict):
        path = [distribution_models['SuperTransferService'].components[2], distribution_models['SuperTransferService'].components[3]]
        assert distribution_models['SuperTransferService'].get_path_supply(path) == 1000.0
        distribution_models['SuperTransferService'].components[2].set_initial_damage_level(0.5)
        distribution_models['SuperTransferService'].components[2].update(1)
        assert distribution_models['SuperTransferService'].get_path_supply(path) == 500.0

    def test_get_optimal_path(self, distribution_models: dict):
        optimal_transfer_supply, optimal_path = distribution_models['SuperTransferService'].get_optimal_path(1, 3)
        assert optimal_transfer_supply == 1000.0
        assert optimal_path == 0

        distribution_models['SuperTransferService'].components[3].set_initial_damage_level(0.5)
        distribution_models['SuperTransferService'].components[3].update(1)
        optimal_transfer_supply, optimal_path = distribution_models['SuperTransferService'].get_optimal_path(1, 3)
        assert optimal_transfer_supply == 1000.0
        assert optimal_path == 1

        distribution_models['SuperTransferService'].components[2].set_initial_damage_level(0.5)
        distribution_models['SuperTransferService'].components[2].update(1)
        optimal_transfer_supply, optimal_path = distribution_models['SuperTransferService'].get_optimal_path(1, 3)
        assert optimal_transfer_supply == 500.0
        assert optimal_path == 0

class TestBridgeServiceDistributionModel:

    MAIN_FILE = './tests/test_inputs/test_inputs_VirtualCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        system =  main.create_system(input_dict)
        return system
    
    @pytest.fixture
    def distribution_models(self, system):
        distribution_models = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if 'Bridge' in resource_name}
        return distribution_models
    
    def test_find_bridges(self, distribution_models):
        distribution_models['BridgeService'].bridges = []
        distribution_models['BridgeService'].find_bridges()
        assert len(distribution_models['BridgeService'].bridges) == 4
        target_localities = [[201, 301], [301, 201], [301, 302], [302, 301]]
        for target_locality_pair, bridge in zip(target_localities, distribution_models['BridgeService'].bridges):
            assert isinstance(bridge, Component.Bridge)
            assert bridge.locality == target_locality_pair
    
    def test_map_links_to_bridges(self, distribution_models):
        distribution_models['BridgeService'].links_on_a_bridge = []
        distribution_models['BridgeService'].map_links_to_bridges()
        assert len(distribution_models['BridgeService'].links_on_a_bridge) == 4
        target_localities = [[201, 301], [301, 201], [301, 302], [302, 301]]
        for i, target_locality_pair in enumerate(target_localities):
            for link in distribution_models['BridgeService'].links_on_a_bridge[i]:
                assert link.locality == target_locality_pair
                assert not isinstance(link, Component.Bridge)
    
    def test_component_is_on_the_bridge(self, distribution_models):
        bridge = distribution_models['BridgeService'].bridges[0]
        component_on_bridge = distribution_models['BridgeService'].components[77]
        component_not_on_bridge = distribution_models['BridgeService'].components[0]
        assert distribution_models['BridgeService'].component_is_on_the_bridge(bridge, component_on_bridge) == True
        assert distribution_models['BridgeService'].component_is_on_the_bridge(bridge, component_not_on_bridge) == False
    
    def test_distribute(self, distribution_models):
        distribution_models['BridgeService'].distribute()
        target_EPTS = distribution_models['BridgeService'].components[75]
        target_PWP = distribution_models['BridgeService'].components[76]
        target_CWP = distribution_models['BridgeService'].components[77]       
        target_bridge = distribution_models['BridgeService'].bridges[0]
        assert target_CWP.supply['Supply']['CoolingWaterTransferService'].current_amount == 1000.0
        assert target_PWP.supply['Supply']['PotableWaterTransferService'].current_amount == 1000.0
        assert target_EPTS.supply['Supply']['ElectricPowerTransferService'].current_amount == 1000.0
        target_bridge.set_initial_damage_level(0.5)
        target_bridge.update(1)
        distribution_models['BridgeService'].distribute()
        assert target_CWP.supply['Supply']['CoolingWaterTransferService'].current_amount == 0
        assert target_PWP.supply['Supply']['PotableWaterTransferService'].current_amount == 0
        assert target_EPTS.supply['Supply']['ElectricPowerTransferService'].current_amount == 0
        
  
        
