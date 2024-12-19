import pytest
import numpy as np
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

class TestSingleResourceSystemMatrixCreator():    

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def distribution_models(self, system):
        distribution_models = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if 'TransferService' not in resource_name}
        return distribution_models    

    def test_initialize_system_matrix(self, distribution_models: dict, system):
        for distribution_model in distribution_models.values():
            distribution_model.system_matrix.initialize_system_matrix()
            assert np.all(distribution_model.system_matrix.matrix == np.zeros(
                (2 * len(system.components), distribution_models['ElectricPower'].system_matrix.NUM_COLUMN_SETS)))

    def test_calculate_num_rows_in_system_matrix(self, distribution_models: dict, system):
        assert distribution_models['ElectricPower'].system_matrix.calculate_num_rows_in_system_matrix() == len(
            system.components) * distribution_models['ElectricPower'].system_matrix.ROWS_PER_COMPONENT

    def test_calculate_num_columns_in_system_matrix(self, distribution_models: dict):
        assert distribution_models['ElectricPower'].system_matrix.calculate_num_columns_in_system_matrix() == \
               distribution_models['ElectricPower'].system_matrix.NUM_COLUMN_SETS

    def test_fill_operation_demand_row(self, distribution_models: dict):
        for resource_name, distribution_model in distribution_models.items():
            for i, component in enumerate(distribution_model.components):
                supply = distribution_model.system_matrix.get_current_resource_amount(component, 'supply',
                                                                                      StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value)
                demand = distribution_model.system_matrix.get_current_resource_amount(component, 'demand',
                                                                                      StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value)
                target_row = [component.get_locality()[0], component.get_locality()[-1], supply, demand, 1.0]
                distribution_model.system_matrix.fill_operation_demand_row(i, component)
                assert np.all(target_row == distribution_model.system_matrix.matrix[i, :])

    def test_fill_recovery_demand_row(self, distribution_models: dict):
        for resource_name, distribution_model in distribution_models.items():
            for i, component in enumerate(distribution_model.components):
                recovery_demand = distribution_model.system_matrix.get_current_resource_amount(component, 'demand',
                                                                                               StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value)
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
            (np.asarray([[1, 1, 5.0, 0.0, 1.0], [1, 1, 0.0, 1.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 1.0, 1.0],
                         [3, 3, 0.0, 1.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)

        assert np.all(target_power_matrix == distribution_models['ElectricPower'].system_matrix.matrix)
        target_communication_matrix = np.concatenate(
            (np.asarray([[1, 1, 0.0, 1.0, 1.0], [1, 1, 1.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 2.0, 0.0, 1.0],
                         [3, 3, 0.0, 1.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(target_communication_matrix == distribution_models['Communication'].system_matrix.matrix)

        target_cooling_water_matrix = np.concatenate(
            (np.asarray([[1, 1, 0.0, 1.0, 1.0], [1, 1, 0.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 3.0, 0.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.0, 1.0],
                         [3, 3, 0.0, 0.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(target_cooling_water_matrix == distribution_models['CoolingWater'].system_matrix.matrix)

    def test_fill_system_matrix_with_damage(self, distribution_models: dict, system):
        system.set_initial_damage()
        system.time_step = 1
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
            (np.asarray([[1, 1, 5.0, 0.0, 1.0], [1, 1, 0.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.0, 1.0],
                         [3, 3, 0.0, 0.6, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(np.isclose(target_power_matrix, distribution_models['ElectricPower'].system_matrix.matrix))

        target_communication_matrix = np.concatenate(
            (np.asarray([[1, 1, 0.0, 1.0, 1.0], [1, 1, 0.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 0.0, 1.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.0, 1.0],
                         [3, 3, 0.0, 10.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(np.isclose(target_communication_matrix, distribution_models['Communication'].system_matrix.matrix))

        target_cooling_water_matrix = np.concatenate(
            (np.asarray([[1, 1, 0.0, 1.0, 1.0], [1, 1, 0.0, 0.0, 1.0], [1, 2, 0.0, 0.0, 1.0], [1, 3, 0.0, 0.0, 1.0],
                         [2, 2, 1.8, 0.0, 1.0], [2, 1, 0.0, 0.0, 1.0], [2, 3, 0.0, 0.0, 1.0], [3, 3, 0.0, 0.0, 1.0],
                         [3, 3, 0.0, 0.0, 1.0], [3, 1, 0.0, 0.0, 1.0], [3, 2, 0.0, 0.0, 1.0]]),
             recovery_demand_matrix_part), axis=0)
        assert np.all(np.isclose(target_cooling_water_matrix, distribution_models['CoolingWater'].system_matrix.matrix))

    def test_get_component_properties(self, distribution_models: dict):
        
        electric_power_plant = distribution_models['ElectricPower'].components[0]
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
        building_stock_unit = distribution_models['ElectricPower'].components[8]
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
