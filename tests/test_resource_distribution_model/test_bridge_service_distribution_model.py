import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent

class TestBridgeServiceDistributionModel:

    MAIN_FILE = './tests/test_inputs/test_inputs_VirtualCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(self.MAIN_FILE)
        system = main.create_system(input_dict)
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
            assert isinstance(bridge, StandardiReCoDeSComponent)
            assert bridge.locality == target_locality_pair
    
    def test_map_links_to_bridges(self, distribution_models):
        distribution_models['BridgeService'].links_on_a_bridge = []
        distribution_models['BridgeService'].map_links_to_bridges()
        assert len(distribution_models['BridgeService'].links_on_a_bridge) == 4
        target_localities = [[201, 301], [301, 201], [301, 302], [302, 301]]
        for i, target_locality_pair in enumerate(target_localities):
            for link in distribution_models['BridgeService'].links_on_a_bridge[i]:
                assert link.locality == target_locality_pair
                assert not link.name == 'Bridge'
    
    def test_component_is_on_the_bridge(self, distribution_models):
        bridge = distribution_models['BridgeService'].bridges[0]
        component_on_bridge = distribution_models['BridgeService'].components[76]
        component_not_on_bridge = distribution_models['BridgeService'].components[0]
        assert distribution_models['BridgeService'].component_is_on_the_bridge(bridge, component_on_bridge) == True
        assert distribution_models['BridgeService'].component_is_on_the_bridge(bridge, component_not_on_bridge) == False
    
    def test_distribute(self, distribution_models):
        distribution_models['BridgeService'].distribute(0)
        target_EPTS = distribution_models['BridgeService'].components[70]
        target_PWP = distribution_models['BridgeService'].components[73]
        target_CWP = distribution_models['BridgeService'].components[76]       
        target_bridge = distribution_models['BridgeService'].bridges[0]
        assert target_CWP.supply['Supply']['CoolingWaterTransferService'].current_amount == 1000.0
        assert target_PWP.supply['Supply']['PotableWaterTransferService'].current_amount == 1000.0
        assert target_EPTS.supply['Supply']['ElectricPowerTransferService'].current_amount == 1000.0
        target_bridge.set_initial_damage_level(0.5)
        target_bridge.update(1)
        distribution_models['BridgeService'].distribute(0)
        assert target_CWP.supply['Supply']['CoolingWaterTransferService'].current_amount == 0
        assert target_PWP.supply['Supply']['PotableWaterTransferService'].current_amount == 0
        assert target_EPTS.supply['Supply']['ElectricPowerTransferService'].current_amount == 0
        