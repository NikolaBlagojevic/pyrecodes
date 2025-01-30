import pytest
import math
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import Component
from pyrecodes.component.component import SupplyOrDemand
from pyrecodes.component_recovery_model.component_level_recovery_activities_model import ComponentLevelRecoveryActivitiesModel
from pyrecodes.resource import concrete_resource
from pyrecodes.resource import consumable_resource
from pyrecodes.relation import relation
from test_component_inputs import COMPONENT_NAME, COMPONENT_PARAMETERS, RECOVERY_TIME_STEPS_DENSE, RECOVERY_TIME_STEPS_SPARSE

class TestStandardiReCoDeSComponent():

    @pytest.fixture
    def component(self) -> StandardiReCoDeSComponent:
        return StandardiReCoDeSComponent()

    def test_init(self, component):
        assert component.functionality_level == 1.0
        assert component.functional == []
        assert component.recovery_model == None
        assert component.locality == None
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value] == {}
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value] == {}
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

    def test_str(self, component):
        component.set_name(COMPONENT_NAME)
        component.set_locality(1)
        assert component.__str__() == f'{COMPONENT_NAME} | Locality: {1}'
    
    def test_construct(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        assert component.name == COMPONENT_NAME
        assert isinstance(component.recovery_model, ComponentLevelRecoveryActivitiesModel)
        assert component.recovery_model.recovery_activities['Repair'].rate == 0.01
        assert component.recovery_model.recovery_activities['Repair'].duration == 100
        assert isinstance(component.recovery_model.damage_to_functionality_relation, relation.ReverseLinear)

        for resource_name, resource_parameters in COMPONENT_PARAMETERS['Supply'].items():
            assert component.supply['Supply'][resource_name].initial_amount == resource_parameters['Amount']
            assert component.supply['Supply'][resource_name].current_amount == resource_parameters['Amount']
            assert isinstance(component.supply['Supply'][resource_name].component_functionality_to_amount, getattr(relation, resource_parameters['FunctionalityToAmountRelation']))
            assert isinstance(component.supply['Supply'][resource_name].unmet_demand_to_amount, getattr(relation, resource_parameters['UnmetDemandToAmountRelation']))

        for resource_name, resource_parameters in COMPONENT_PARAMETERS['OperationDemand'].items():
            assert component.demand['OperationDemand'][resource_name].initial_amount == resource_parameters['Amount']
            assert component.demand['OperationDemand'][resource_name].current_amount == resource_parameters['Amount']
            assert isinstance(component.demand['OperationDemand'][resource_name].component_functionality_to_amount, getattr(relation, resource_parameters['FunctionalityToAmountRelation']))
    
    def test_set_recovery_model(self, component):
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        assert isinstance(component.recovery_model, ComponentLevelRecoveryActivitiesModel)
        assert component.recovery_model.recovery_activities['Repair'].rate == 0.01
        assert component.recovery_model.recovery_activities['Repair'].duration == 100
        assert isinstance(component.recovery_model.damage_to_functionality_relation, relation.ReverseLinear)

    def test_set_recovery_time_steps(self, component):
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        component.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        assert component.recovery_model.recovery_time_steps == RECOVERY_TIME_STEPS_SPARSE
        component.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        assert component.recovery_model.recovery_time_steps == RECOVERY_TIME_STEPS_DENSE
  
    def test_set_supply(self, component):
        assert component.demand['OperationDemand'] == {}
        assert component.supply['Supply'] == {}
        component.set_supply(COMPONENT_PARAMETERS['Supply'])        
        for resource_name, resource_parameters in COMPONENT_PARAMETERS['Supply'].items():
            assert component.supply['Supply'][resource_name].initial_amount == resource_parameters['Amount']
            assert component.supply['Supply'][resource_name].current_amount == resource_parameters['Amount']
            assert isinstance(component.supply['Supply'][resource_name].component_functionality_to_amount, getattr(relation, resource_parameters['FunctionalityToAmountRelation']))
            assert isinstance(component.supply['Supply'][resource_name].unmet_demand_to_amount, getattr(relation, resource_parameters['UnmetDemandToAmountRelation']))

    def test_operation_demand(self, component): 
        component.set_operation_demand(COMPONENT_PARAMETERS['OperationDemand'])
        for resource_name, resource_parameters in COMPONENT_PARAMETERS['OperationDemand'].items():
            assert component.demand['OperationDemand'][resource_name].initial_amount == resource_parameters['Amount']
            assert component.demand['OperationDemand'][resource_name].current_amount == resource_parameters['Amount']
            assert isinstance(component.demand['OperationDemand'][resource_name].component_functionality_to_amount, getattr(relation, resource_parameters['FunctionalityToAmountRelation']))
    
    def test_set_initial_damage_level(self, component):
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        component.set_initial_damage_level(0.5)
        assert component.get_damage_level() == 0.5
        component.set_initial_damage_level(1.0)
        assert component.get_damage_level() == 1.0
        component.set_initial_damage_level(0.0)
        assert component.get_damage_level() == 0.0
        with pytest.raises(ValueError):
            component.set_initial_damage_level(-0.5)
        with pytest.raises(ValueError):
            component.set_initial_damage_level(1.5)
    
    def test_get_damage_level(self, component):
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        component.set_initial_damage_level(0.5)
        assert component.get_damage_level() == 0.5
        component.set_initial_damage_level(1.0)
        assert component.get_damage_level() == 1.0
        component.set_initial_damage_level(0.0)
        assert component.get_damage_level() == 0.0

    def test_set_name(self, component):
        component.set_name(COMPONENT_NAME)
        assert component.name == COMPONENT_NAME
        another_name = 'TestComponent2'
        component.set_name(another_name)
        assert component.name == another_name
    
    def test_set_get_locality(self, component):
        component.set_locality([0])
        assert component.get_locality() == [0]
        component.set_locality([0, 1])
        assert component.get_locality() == [0, 1]
    
    def test_has_operation_demand(self, component):
        assert component.has_operation_demand() == False
        component.set_operation_demand(COMPONENT_PARAMETERS['OperationDemand']) 
        assert component.has_operation_demand() == True
        component.set_operation_demand(COMPONENT_PARAMETERS['OperationDemand']) 
        assert component.has_operation_demand() == True
    
    def test_has_resource_supply(self, component):
        assert component.has_resource_supply('SupplyResource1') == False
        component.set_supply(COMPONENT_PARAMETERS['Supply'])
        assert component.has_resource_supply('SupplyResource1') == True
        assert component.has_resource_supply('SupplyResource2') == True
        assert component.has_resource_supply('SupplyResource3') == False

    def test_unmet_demand_can_affect_resource_supply(self, component):
        assert component.unmet_demand_can_affect_resource_supply('SupplyResource1') == False
        component.set_supply(COMPONENT_PARAMETERS['Supply'])
        assert component.unmet_demand_can_affect_resource_supply('SupplyResource1') == True
        assert component.unmet_demand_can_affect_resource_supply('SupplyResource2') == False
        assert component.unmet_demand_can_affect_resource_supply('SupplyResource3') == False

    def test_add_resources_supply(self, component):
        component = StandardiReCoDeSComponent()
        component.add_resources(SupplyOrDemand.SUPPLY.value,
                                StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                COMPONENT_PARAMETERS['Supply'])
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value] == {}
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}
        assert len(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]) == 2
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource1'].name == 'SupplyResource1'
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource1'].initial_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource1'].current_amount == 10
        assert isinstance(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                           'SupplyResource1'].component_functionality_to_amount, relation.Constant)
        assert isinstance(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                            'SupplyResource1'].unmet_demand_to_amount, relation.Binary)
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource2'].name == 'SupplyResource2'
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource2'].initial_amount == 100
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource2'].current_amount == 100
        assert isinstance(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                           'SupplyResource2'].component_functionality_to_amount, relation.Linear)
        assert isinstance(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                            'SupplyResource2'].unmet_demand_to_amount, relation.Constant)
    
    def test_add_resources_demand(self, component):
        component.add_resources(SupplyOrDemand.DEMAND.value,
                                StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, 
                                COMPONENT_PARAMETERS['OperationDemand'])
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}
        assert len(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]) == len(COMPONENT_PARAMETERS['OperationDemand'])
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource1'].name == 'DemandResource1'
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource1'].initial_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource1'].current_amount == 1
        assert isinstance(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                           'DemandResource1'].component_functionality_to_amount, relation.Constant)
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource2'].name == 'DemandResource2'
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource2'].initial_amount == 5
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource2'].current_amount == 5
        assert isinstance(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                           'DemandResource2'].component_functionality_to_amount, relation.Binary)
        
    def test_add_one_resource_wrong_supply_key_string(self, component):
        with pytest.raises(KeyError):
            component.add_resources(SupplyOrDemand.SUPPLY.value, 
                                    'supply', 
                                    COMPONENT_PARAMETERS['Supply'])

    def test_add_one_resource_wrong_demand_key_string(self, component):
        with pytest.raises(KeyError):
            component.add_resources(SupplyOrDemand.DEMAND.value, 
                                    'operation_demand', 
                                    COMPONENT_PARAMETERS['OperationDemand'])

    def test_add_multiple_resources(self, component):
        resource_dict = {"SupplyResource1": {
                "Amount": 10,
                "FunctionalityToAmountRelation": "Constant",
                "UnmetDemandToAmountRelation": "Binary"
                }
            }
        for _ in range(5):
            component.add_resources(SupplyOrDemand.SUPPLY.value,
                                    StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                    resource_dict)

        for resource in component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value].values():
            assert resource.name == 'SupplyResource1'
            assert resource.initial_amount == 10
            assert resource.current_amount == 10
        
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value] == {}
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

    def test_form_resource_non_consumable(self, component):
        resource_dict = {"SupplyResource1": {
                "Amount": 10,
                "FunctionalityToAmountRelation": "Constant",
                "UnmetDemandToAmountRelation": "Binary"
                }
            }
        resource_name, resource_parameters = list(resource_dict.items())[0]
        resource = component.form_resource(resource_name, resource_parameters)
        assert isinstance(resource, concrete_resource.ConcreteResource)
        assert resource.name == 'SupplyResource1'
        assert resource.initial_amount == 10
        assert resource.current_amount == 10
        assert isinstance(resource.component_functionality_to_amount, relation.Constant)
        assert isinstance(resource.unmet_demand_to_amount, relation.Binary)
    
    def test_form_resource_consumable(self, component):
        resource_dict = {"SupplyResource1": {
                "ResourceClass": {"FileName": "consumable_resource", "ClassName": "ConsumableResource"},
                "Amount": 10,
                "FunctionalityToAmountRelation": "Constant",
                "UnmetDemandToAmountRelation": "Binary"
                }
            }
        resource_name, resource_parameters = list(resource_dict.items())[0]
        resource = component.form_resource(resource_name, resource_parameters)
        assert isinstance(resource, consumable_resource.ConsumableResource)
        assert resource.name == 'SupplyResource1'
        assert resource.initial_amount == 10
        assert resource.current_amount == 10
        assert isinstance(resource.component_functionality_to_amount, relation.Constant)
        assert isinstance(resource.unmet_demand_to_amount, relation.Binary)
    
    def test_get_current_resource_amount_no_damage(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        assert component.get_current_resource_amount(SupplyOrDemand.SUPPLY.value, 
                                                    StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                    'SupplyResource1') == 10
        assert component.get_current_resource_amount(SupplyOrDemand.SUPPLY.value, 
                                                    StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                    'SupplyResource2') == 100
        assert component.get_current_resource_amount(SupplyOrDemand.DEMAND.value,
                                                    StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value,
                                                    'DemandResource1') == 1
        assert component.get_current_resource_amount(SupplyOrDemand.DEMAND.value,
                                                    StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value,
                                                    'DemandResource2') == 5
    
    def test_get_current_resource_amount_with_damage(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        component.set_initial_damage_level(0.5)
        component.update(1)
        assert component.get_current_resource_amount(SupplyOrDemand.SUPPLY.value,
                                                    StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                    'SupplyResource1') == 10
        assert component.get_current_resource_amount(SupplyOrDemand.SUPPLY.value,
                                                    StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                    'SupplyResource2') == 50
        assert component.get_current_resource_amount(SupplyOrDemand.DEMAND.value,
                                                    StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value,
                                                    'DemandResource1') == 1
        assert component.get_current_resource_amount(SupplyOrDemand.DEMAND.value,
                                                    StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value,
                                                    'DemandResource2') == 0
        
    def test_update_functionality(self, component):
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        damage_level = 0.23
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        assert math.isclose(component.functionality_level, 0.77)

        damage_level = 0.56
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        assert math.isclose(component.functionality_level, 0.44)

        damage_level = 0.1
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        assert math.isclose(component.functionality_level, 0.9)
    
    def test_check_if_functional_partial_damage(self, component):
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        damage_level = 0.23
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.check_if_functional(time_step=1)
        assert component.functional == [1]

    def test_check_if_functional_full_damage(self, component):
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        damage_level = 1.0
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.check_if_functional(time_step=5)   
        assert component.functional == []
    
    def test_check_if_functional_during_recovery_dense(self, component):
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        component.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        damage_level = 1.0
        component.set_initial_damage_level(damage_level)
        for time_step in range(150):
            component.update_functionality()
            component.check_if_functional(time_step=time_step)
            component.recover(time_step=time_step)
        assert component.functional == list(range(1, 150))

    def test_check_if_functional_during_recovery_sparse(self, component):
        COMPONENT_PARAMETERS['RecoveryModel']['DamageFunctionalityRelation']['Type'] = 'ReverseBinary'
        COMPONENT_PARAMETERS['RecoveryModel']['Parameters']['Repair']['Duration'] = {
            "Deterministic": {
                "Value": 7
            }
        }
        component.set_recovery_model(COMPONENT_PARAMETERS['RecoveryModel'])
        component.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        damage_level = 1.0
        component.set_initial_damage_level(damage_level)
        for time_step in range(150):
            component.update_functionality()
            component.check_if_functional(time_step=time_step)
            component.recover(time_step=time_step)
        assert component.functional == list(range(11, 150))
    
    def test_update_resources_based_on_component_functionality(self, component):
        COMPONENT_PARAMETERS['RecoveryModel']['DamageFunctionalityRelation']['Type'] = 'ReverseLinear'
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        damage_level = 0.23
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.update_resources_based_on_component_functionality(SupplyOrDemand.SUPPLY.value,
                                                                    StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value)
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            10)
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].current_amount,
                            100*0.77)
        
        component.update_resources_based_on_component_functionality(SupplyOrDemand.DEMAND.value,
                                                                    StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value)
        assert math.isclose(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource1'].current_amount,
                            1)
        assert math.isclose(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource2'].current_amount,
                            0)
        
    def test_update_supply_based_on_component_functionality(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        damage_level = 0.4
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.update_supply_based_on_component_functionality()
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            10)
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].current_amount,
                            100*0.6)
    
    def test_update_operation_demand(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        assert math.isclose(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource1'].current_amount,
                            1)
        assert math.isclose(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource2'].current_amount,
                            5)    
        damage_level = 1.0
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.update_operation_demand()
        assert math.isclose(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource1'].current_amount,
                            1)
        assert math.isclose(component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource2'].current_amount,
                            0)
    
    def test_update_recovery_demand(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        component.update_recovery_demand()
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}
        component.set_initial_damage_level(0.5)
        component.update_recovery_demand()
        assert math.isclose(component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value][
                                'RecoveryResource1'].current_amount,
                            0.1)
        component.set_initial_damage_level(0)
        component.update_recovery_demand()
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

    def test_set_recovery_model_activities_demand_to_met(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        assert component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] == 1.0
        component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] = 0.5
        component.set_recovery_model_activities_demand_to_met()
        assert component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] == 1.0
    
    def test_update_supply_based_on_unmet_demand(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        percent_of_met_demand = 0.6
        component.update_supply_based_on_unmet_demand(percent_of_met_demand)
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            0)
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].current_amount,
                            100)
    
    def test_update_supply_based_on_consumption(self, component):
        COMPONENT_PARAMETERS['Supply']['SupplyResource1']['ResourceClass'] = {'FileName': 'consumable_resource', 'ClassName': 'ConsumableResource'}
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        component.update_supply_based_on_consumption('SupplyResource1', 1)
        component.update_supply_based_on_consumption('SupplyResource2', 1)
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            9)  
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].initial_amount,
                            9) 
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].current_amount,
                            100)
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].initial_amount,
                            100)
        
        component.update_supply_based_on_consumption('SupplyResource1', 10)
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            0)  
        assert math.isclose(component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].initial_amount,
                            0) 
    
    def test_set_met_demand_for_recovery_activities(self, component):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        component.set_met_demand_for_recovery_activities('RecoveryResource1', 0.3)
        assert component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] == 0.3

        component.set_met_demand_for_recovery_activities('RecoveryResource1', 1.0)
        assert component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] == 1.0

    def test_recover_dense(self, component):
        COMPONENT_PARAMETERS['RecoveryModel']['Parameters']['Repair']['Duration'] = {
            "Deterministic": {
                "Value": 100
            }
        }
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        component.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        component.set_initial_damage_level(0.4)
        component.update(0)
        assert math.isclose(component.get_damage_level(), 0.4)
        component.recover(0)
        assert math.isclose(component.get_damage_level(), 0.396)

        component.set_met_demand_for_recovery_activities('RecoveryResource1', 0.0)
        component.recover(1)
        assert math.isclose(component.get_damage_level(), 0.396)

        component.set_met_demand_for_recovery_activities('RecoveryResource1', 1.0)
        component.recover(2)
        assert math.isclose(component.get_damage_level(), 0.392)
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0, 2]

        for time_step in range (3, 101):
            component.recover(time_step)
        assert component.get_damage_level() == 0.0
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0, 2] + list(range(3, 101))

    def test_recover_sparse(self, component):
        COMPONENT_PARAMETERS['RecoveryModel']['DamageFunctionalityRelation']['Type'] = 'ReverseLinear'
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        component.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        component.set_initial_damage_level(0.4)
        component.update(0)
        assert math.isclose(component.get_damage_level(), 0.4)
        component.recover(0)
        assert math.isclose(component.get_damage_level(), 0.396)

        component.set_met_demand_for_recovery_activities('RecoveryResource1', 0.0)
        component.recover(1)
        assert math.isclose(component.get_damage_level(), 0.396)

        component.set_met_demand_for_recovery_activities('RecoveryResource1', 1.0)
        component.recover(2)
        assert math.isclose(component.get_damage_level(), 0.396)
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0]

        component.recover(3)
        assert math.isclose(component.get_damage_level(), 0.396)
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0]

        component.recover(4)
        assert math.isclose(component.get_damage_level(), 0.396)
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0]

        component.set_met_demand_for_recovery_activities('RecoveryResource1', 0.0)
        component.recover(5)
        assert math.isclose(component.get_damage_level(), 0.396)
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0]

        component.set_met_demand_for_recovery_activities('RecoveryResource1', 1.0)
        component.recover(6)
        assert math.isclose(component.get_damage_level(), 0.396)
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0]

        component.recover(10)
        assert math.isclose(component.get_damage_level(), 0.376)
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0, 6, 7, 8, 9, 10]

        for time_step in range (11, 106):
            component.recover(time_step)
        assert component.get_damage_level() == 0.0
        assert component.recovery_model.recovery_activities['Repair'].time_steps == [0] + list(range(6, 105))

    def test_update_dense_recovery(self, component):
        COMPONENT_PARAMETERS['RecoveryModel']['DamageFunctionalityRelation']['Type'] = 'ReverseLinear'
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        component.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        component.update(0)
        assert component.functionality_level == 1
        assert component.functional == [0]
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 100
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 5
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

        component.set_initial_damage_level(0.4)
        component.update(1)
        assert component.functionality_level == 0.6
        assert component.functional == [0, 1]
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 60
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 0
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]['RecoveryResource1'].current_amount == 0.1

        component.recover(2)
        component.update(2)
        assert component.functionality_level == 0.604
        assert component.functional == [0, 1, 2]
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 60.4
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 0
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]['RecoveryResource1'].current_amount == 0.1

        for time_step in range (3, 102):
            component.recover(time_step)
            component.update(time_step)
        assert component.get_damage_level() == 0.0
        assert component.recovery_model.recovery_activities['Repair'].time_steps == list(range(2, 102))
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 100
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 5
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

    def test_update_sparse_recovery(self, component):
        COMPONENT_PARAMETERS['RecoveryModel']['DamageFunctionalityRelation']['Type'] = 'ReverseLinear'
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        component.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        component.update(0)
        assert component.functionality_level == 1
        assert component.functional == [0]
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 100
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 5
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

        component.set_initial_damage_level(0.4)
        component.update(1)
        assert component.functionality_level == 0.6
        assert component.functional == [0, 1]
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 60
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 0
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]['RecoveryResource1'].current_amount == 0.1

        component.recover(2)
        component.update(2)
        assert component.functionality_level == 0.6
        assert component.functional == [0, 1, 2]
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 60
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 0
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]['RecoveryResource1'].current_amount == 0.1

        component.recover(5)
        component.update(5)
        assert component.functionality_level == 0.62
        assert component.functional == [0, 1, 2, 5]
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 62
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 0
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]['RecoveryResource1'].current_amount == 0.1

        for time_step in range (6, 102):
            component.recover(time_step)
            component.update(time_step)
        assert component.get_damage_level() == 0.0
        assert component.recovery_model.recovery_activities['Repair'].time_steps == list(range(1, 101))
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 100
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 5
        assert component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}
