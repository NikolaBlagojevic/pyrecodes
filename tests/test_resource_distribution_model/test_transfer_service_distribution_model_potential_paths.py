import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file

class TestTransferServiceDistributionModelPotentialPaths:

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(self.MAIN_FILE)
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
