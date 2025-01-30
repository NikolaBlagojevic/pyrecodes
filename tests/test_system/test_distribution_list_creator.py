import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.system.distribution_list_creator import DistributionListCreator

MAIN_FILE = './tests/test_inputs/test_inputs_VirtualCommunity_Main.json'

class TestDistributionListCreator:

    @pytest.fixture
    def distribution_list_creator(self):
        input_dict = read_json_file(MAIN_FILE)
        system = main.create_system(input_dict)
        return DistributionListCreator(system.components, system.resources)
    
    def test_get_resource_distribution_dict(self, distribution_list_creator):
        target_dict = {'IndependentResources': [
                        'BridgeService', 'ElectricPowerTransferService', 
                        'PotableWaterTransferService',
                        'CoolingWaterTransferService', 'Shelter'],

                       'InterdependentResources': [                       
                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater', 
                       'CoolingWater', 'FunctionalHousing',

                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater',
                       'CoolingWater', 'FunctionalHousing',

                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater',
                       'CoolingWater', 'FunctionalHousing',

                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater',
                       'CoolingWater', 'FunctionalHousing',

                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater', 
                       'CoolingWater', 'FunctionalHousing',
                       
                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater', 
                       'CoolingWater', 'FunctionalHousing']}
        
        assert distribution_list_creator.get_resource_distribution_dict() == target_dict
    
    def test_get_resource_group(self, distribution_list_creator):
        assert distribution_list_creator.get_resource_group('Utilities') == ['ElectricPower', 
                                                                             'HighLevelCommunication',
                                                                             'LowLevelCommunication',
                                                                             'PotableWater', 
                                                                             'CoolingWater', 
                                                                             'Shelter', 
                                                                             'FunctionalHousing']
        assert distribution_list_creator.get_resource_group('TransferService') == ['ElectricPowerTransferService',                                                                             
                                                                                   'PotableWaterTransferService', 
                                                                                   'CoolingWaterTransferService']
        assert distribution_list_creator.get_resource_group('BridgeService') == ['BridgeService']

    def test_get_independent_interdependent_resources(self, distribution_list_creator):
        target_interdependent_resources = ['ElectricPower', 'HighLevelCommunication', 'LowLevelCommunication', 'PotableWater', 'CoolingWater', 'FunctionalHousing']
        target_independent_resources = ['BridgeService', 'ElectricPowerTransferService', 'PotableWaterTransferService', 'CoolingWaterTransferService', 'Shelter']
        target_resource_distribution_dict = {'IndependentResources': target_independent_resources, 'InterdependentResources': target_interdependent_resources}
        resource_distribution_dict = distribution_list_creator.get_independent_interdependent_resources({'IndependentResources': ['BridgeService', 'ElectricPowerTransferService', 'PotableWaterTransferService', 'CoolingWaterTransferService'], 
                                                                                                         'InterdependentResources': []})
        assert resource_distribution_dict == target_resource_distribution_dict
    
    def test_resource_is_interdependent(self, distribution_list_creator):
        for component in distribution_list_creator.components:
            if component.name == 'ElectricPowerPlant':
                assert distribution_list_creator.resource_is_interdependent('ElectricPower', component) == True
            elif component.name == 'CoolingWaterFacility':
                assert distribution_list_creator.resource_is_interdependent('CoolingWater', component) == True
            else:
                assert distribution_list_creator.resource_is_interdependent('ElectricPower', component) == False
                assert distribution_list_creator.resource_is_interdependent('CoolingWater', component) == False
                assert distribution_list_creator.resource_is_interdependent('BridgeService', component) == False
                assert distribution_list_creator.resource_is_interdependent('Shelter', component) == False

    def test_form_resource_distribution_vector(self, distribution_list_creator):
        interdependent_resources = ['ElectricPower', 'Communication', 'CoolingWater']
        vector = distribution_list_creator.form_resource_distribution_vector(interdependent_resources)
        assert vector == ['ElectricPower', 'Communication', 'CoolingWater', 'ElectricPower', 'Communication',
                          'CoolingWater', 'ElectricPower', 'Communication', 'CoolingWater']
