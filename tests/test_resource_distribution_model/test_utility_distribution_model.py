import pytest
import math
import numpy as np
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.distribution_priority.component_based_priority import ComponentBasedPriority
from pyrecodes.component.component import SupplyOrDemand
from pyrecodes.resource_distribution_model.transfer_service_distribution_model_potential_paths import TransferServiceDistributionModelPotentialPaths

class TestUtilityDistributionModel_ThreeLocalitiesCommunity():

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def distribution_models(self, system):
        distribution_models = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if 'TransferService' not in resource_name}
        return distribution_models 

    def test_init_(self, distribution_models: dict, system):
        assert distribution_models['ElectricPower'].system_matrix.RECOVERY_DEMAND_ROW_OFFSET == len(system.components)
        assert isinstance(distribution_models['ElectricPower'].priority, ComponentBasedPriority)
        assert isinstance(distribution_models['ElectricPower'].transfer_service_distribution_model, TransferServiceDistributionModelPotentialPaths)

    def test_distribute(self, distribution_models: dict, system):
        distribution_models['Communication'].distribute(time_step=0)
        assert np.all(distribution_models['Communication'].system_matrix.matrix[:, -1] == 1.0)
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        distribution_models['Communication'].components = system.components
        distribution_models['Communication'].distribute(system.time_step)
        assert np.all(distribution_models['Communication'].system_matrix.matrix[8, -1] == 0.0)

    def test_fill_system_matrix(self, distribution_models: dict, system):
        locality_matrix = []
        for component in distribution_models['ElectricPower'].components:
            locality_matrix.append([component.get_locality()[0], component.get_locality()[-1]])
        recovery_demand_matrix_part = np.concatenate(
            (locality_matrix, np.asarray([[0.0, 0.0, 1.0] for _ in distribution_models['ElectricPower'].components])),
            axis=1)
        target_initial_matrix_no_damage = np.concatenate(
            (np.asarray([[1, 1, 5.0, 0.0, 1.0], [1, 1, 0.0, 1.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 1.0, 1.0],
                         [3, 3, 0.0, 1.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        distribution_models['ElectricPower'].fill_system_matrix()
        assert np.all(distribution_models['ElectricPower'].system_matrix.matrix == target_initial_matrix_no_damage)

        target_initial_matrix_with_damage = np.concatenate(
            (np.asarray([[1, 1, 5.0, 0.0, 1.0], [1, 1, 0.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.0, 1.0],
                         [3, 3, 0.0, 0.6, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        
        system.set_initial_damage()
        system.time_step = 0
        system.update()
        distribution_models['ElectricPower'].components = system.components
        distribution_models['ElectricPower'].fill_system_matrix()
        assert np.all(distribution_models['ElectricPower'].system_matrix.matrix == target_initial_matrix_with_damage)
        
    def test_get_component_priorities(self, distribution_models: dict):
        target_priorities = [0, 1, 4, 7, 8]
        target_demand_types = ['OperationDemand' for _ in range(len(target_priorities))]
        component_rows, component_demand_types = distribution_models['ElectricPower'].get_component_priorities()
        assert target_priorities == component_rows
        assert target_demand_types == component_demand_types
    
    def test_set_component_row_based_on_demand_type(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].set_component_row_based_on_demand_type([1], ['OperationDemand']) == [1]
        assert distribution_models['ElectricPower'].set_component_row_based_on_demand_type([1], ['RecoveryDemand']) == [1 + len(distribution_models['ElectricPower'].components)]                          

    def test_add_supplier(self, distribution_models: dict):
        power_plant_row_id = 0
        target_component_is_supplier = [True, False, False]
        target_suppliers_length = [1, 0, 0]
        for target_bool, target_length, distribution_model in zip(target_component_is_supplier, target_suppliers_length,
                                                                  distribution_models.values()):
            distribution_model.system_matrix.fill_system_matrix()
            suppliers = []
            suppliers, component_is_supplier = distribution_model.add_supplier(power_plant_row_id, suppliers)
            assert len(suppliers) == target_length
            assert component_is_supplier == target_bool

    def test_add_supplier_with_damage(self, distribution_models: dict, system):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        target_damaged_supply_values = [5.0, 1.8, 0.0]
        for target_value, distribution_model in zip(target_damaged_supply_values, distribution_models.values()):
            distribution_model.components = system.components
            distribution_model.fill_system_matrix()
            suppliers = []
            for component_row_id in range(len(distribution_model.components)):
                suppliers, component_is_supplier = distribution_model.add_supplier(component_row_id, suppliers)
            if distribution_model.resource_name == 'Communication':
                assert len(suppliers) == 0
            else:
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

    def test_suppliers_meet_component_demand_with_damage(self, distribution_models: dict, system):
        system.set_initial_damage()
        system.time_step = 0
        system.update()
        building_stock_id = 8
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
        assert distribution_models['ElectricPower'].components[0].supply['Supply']['ElectricPower'].current_amount == 5.0
        suppliers = [{'StartLocality': 1, 'EndLocality': 1,
                      'CurrentSupply': 0.5, 'ConsumedAmount': 1.0,
                      'ComponentRowID': 0}]
        distribution_models['ElectricPower'].update_suppliers_based_on_consumption(suppliers)
        assert distribution_models['ElectricPower'].components[0].supply['Supply']['ElectricPower'].current_amount == 5.0
        
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
                distribution_model.components[power_plant_row_id], SupplyOrDemand.SUPPLY.value, 'Supply'),
                power_plant_supply)
            assert math.isclose(distribution_model.system_matrix.get_current_resource_amount(
                distribution_model.components[base_station_row_id], SupplyOrDemand.SUPPLY.value, 'Supply'),
                base_station_supply)

    def test_get_demand(self, distribution_models: dict):
        demand_of_the_power_plant = [0.0, 1.0, 1.0]
        power_plant_row_id = 0
        for target_demand, distribution_model in zip(demand_of_the_power_plant, distribution_models.values()):
            distribution_model.fill_system_matrix()
            assert distribution_model.get_demand(power_plant_row_id) == target_demand

    def test_get_transfer_service_demand(self, distribution_models: dict):
        component_row_BSU = 8
        component_row_EPP = 0
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

    def test_get_total_supply_with_damage(self, distribution_models: dict, system):
        target_supplies = [5.0, 1.8, 0.0]
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

    def test_get_total_demand_with_damage(self, distribution_models: dict, system):
        target_demands = [1.6, 1.0, 12.0]
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

    def test_get_total_consumption_with_damage(self, distribution_models: dict, system):
        target_demands = [1.6, 1.0, 0.0]
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        for target_demand, distribution_model in zip(target_demands, distribution_models.values()):
            distribution_model.components = system.components
            distribution_model.distribute(system.time_step)
            current_consumption = distribution_model.get_total_consumption()
            assert math.isclose(target_demand, current_consumption)