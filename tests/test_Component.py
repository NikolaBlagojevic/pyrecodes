
import pytest
import math
from pyrecodes import ComponentRecoveryModel
from pyrecodes import Relation
from pyrecodes import Component
from pyrecodes import Resource

component_name = 'TestComponent'
component_parameters = {
        "ComponentClass": "StandardiReCoDeSComponent",
        "RecoveryModel": {
            "Type": "ComponentLevelRecoveryActivitiesModel",
            "Parameters": {
                "Repair": {
                    "Duration": {
                        "Deterministic": {
                            "Value": 100
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "RecoveryResource1",
                            "Amount": 0.1
                        }],
                    }
                },
            "DamageFunctionalityRelation": {
                "Type": "ReverseLinear"
            }
        },
        "Supply": {
            "SupplyResource1": {
                "Amount": 10,
                "FunctionalityToAmountRelation": "Constant",
                "UnmetDemandToAmountRelation": "Binary"
            },
            "SupplyResource2": {
                "Amount": 100,
                "FunctionalityToAmountRelation": "Linear",
                "UnmetDemandToAmountRelation": "Constant"
            }
        },
        "OperationDemand": {
            "DemandResource1": {
                "Amount": 1,
                "FunctionalityToAmountRelation": "Constant"
            },
            "DemandResource2": {
                "Amount": 5,
                "FunctionalityToAmountRelation": "Binary"
            }
        }
    }

class TestStandardiReCoDeSComponent():

    @pytest.fixture
    def component(self) -> Component.StandardiReCoDeSComponent:
        return Component.StandardiReCoDeSComponent()

    def test_init(self, component):
        assert component.functionality_level == 1.0
        assert component.functional == []
        assert component.recovery_model == None
        assert component.locality == None
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value] == {}
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value] == {}
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

    def test_str(self, component):
        component.set_name(component_name)
        component.set_locality(1)
        assert component.__str__() == f'{component_name} | Locality: {1}'
    
    def test_construct(self, component):
        component.construct(component_name, component_parameters)
        assert component.name == component_name
        assert isinstance(component.recovery_model, ComponentRecoveryModel.ComponentLevelRecoveryActivitiesModel)
        assert component.recovery_model.recovery_activities['Repair'].rate == 0.01
        assert component.recovery_model.recovery_activities['Repair'].duration == 100
        assert isinstance(component.recovery_model.damage_to_functionality_relation, Relation.ReverseLinear)

        for resource_name, resource_parameters in component_parameters['Supply'].items():
            assert component.supply['Supply'][resource_name].initial_amount == resource_parameters['Amount']
            assert component.supply['Supply'][resource_name].current_amount == resource_parameters['Amount']
            assert isinstance(component.supply['Supply'][resource_name].component_functionality_to_amount, getattr(Relation, resource_parameters['FunctionalityToAmountRelation']))
            assert isinstance(component.supply['Supply'][resource_name].unmet_demand_to_amount, getattr(Relation, resource_parameters['UnmetDemandToAmountRelation']))

        for resource_name, resource_parameters in component_parameters['OperationDemand'].items():
            assert component.demand['OperationDemand'][resource_name].initial_amount == resource_parameters['Amount']
            assert component.demand['OperationDemand'][resource_name].current_amount == resource_parameters['Amount']
            assert isinstance(component.demand['OperationDemand'][resource_name].component_functionality_to_amount, getattr(Relation, resource_parameters['FunctionalityToAmountRelation']))
    
    def test_set_recovery_model(self, component):
        component.set_recovery_model(component_parameters['RecoveryModel'])
        assert isinstance(component.recovery_model, ComponentRecoveryModel.ComponentLevelRecoveryActivitiesModel)
        assert component.recovery_model.recovery_activities['Repair'].rate == 0.01
        assert component.recovery_model.recovery_activities['Repair'].duration == 100
        assert isinstance(component.recovery_model.damage_to_functionality_relation, Relation.ReverseLinear)
  
    def test_set_supply(self, component):
        assert component.demand['OperationDemand'] == {}
        assert component.supply['Supply'] == {}
        component.set_supply(component_parameters['Supply'])        
        for resource_name, resource_parameters in component_parameters['Supply'].items():
            assert component.supply['Supply'][resource_name].initial_amount == resource_parameters['Amount']
            assert component.supply['Supply'][resource_name].current_amount == resource_parameters['Amount']
            assert isinstance(component.supply['Supply'][resource_name].component_functionality_to_amount, getattr(Relation, resource_parameters['FunctionalityToAmountRelation']))
            assert isinstance(component.supply['Supply'][resource_name].unmet_demand_to_amount, getattr(Relation, resource_parameters['UnmetDemandToAmountRelation']))

    def test_operation_demand(self, component): 
        component.set_operation_demand(component_parameters['OperationDemand'])
        for resource_name, resource_parameters in component_parameters['OperationDemand'].items():
            assert component.demand['OperationDemand'][resource_name].initial_amount == resource_parameters['Amount']
            assert component.demand['OperationDemand'][resource_name].current_amount == resource_parameters['Amount']
            assert isinstance(component.demand['OperationDemand'][resource_name].component_functionality_to_amount, getattr(Relation, resource_parameters['FunctionalityToAmountRelation']))
    
    def test_set_initial_damage_level(self, component):
        component.set_recovery_model(component_parameters['RecoveryModel'])
        component.set_initial_damage_level(0.5)
        assert component.get_damage_level() == 0.5
        component.set_initial_damage_level(1.0)
        assert component.get_damage_level() == 1.0
        component.set_initial_damage_level(0.0)
        assert component.get_damage_level() == 0.0
        with pytest.raises(ValueError):
            component.set_initial_damage_level(-0.5)

    def test_set_name(self, component):
        component.set_name(component_name)
        assert component.name == component_name
        another_name = 'TestComponent2'
        component.set_name(another_name)
        assert component.name == another_name
    
    def test_set_locality(self, component):
        component.set_locality([0])
        assert component.get_locality() == [0]
        component.set_locality([0, 1])
        assert component.get_locality() == [0, 1]
    
    def test_has_operation_demand(self, component):
        assert component.has_operation_demand() == False
        component.set_operation_demand(component_parameters['OperationDemand']) 
        assert component.has_operation_demand() == True
    
    def test_has_resource_supply(self, component):
        assert component.has_resource_supply('SupplyResource1') == False
        component.set_supply(component_parameters['Supply'])
        assert component.has_resource_supply('SupplyResource1') == True
        assert component.has_resource_supply('SupplyResource2') == True
        assert component.has_resource_supply('SupplyResource3') == False

    def test_unmet_demand_can_affect_resource_supply(self, component):
        assert component.unmet_demand_can_affect_resource_supply('SupplyResource1') == False
        component.set_supply(component_parameters['Supply'])
        assert component.unmet_demand_can_affect_resource_supply('SupplyResource1') == True
        assert component.unmet_demand_can_affect_resource_supply('SupplyResource2') == False
        assert component.unmet_demand_can_affect_resource_supply('SupplyResource3') == False

    def test_add_resources_supply(self, component):
        component = Component.StandardiReCoDeSComponent()
        component.add_resources(Component.SupplyOrDemand.SUPPLY.value,
                                Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                component_parameters['Supply'])
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value] == {}
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}
        assert len(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]) == 2
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource1'].name == 'SupplyResource1'
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource1'].initial_amount == 10
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource1'].current_amount == 10
        assert isinstance(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                           'SupplyResource1'].component_functionality_to_amount, Relation.Constant)
        assert isinstance(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                            'SupplyResource1'].unmet_demand_to_amount, Relation.Binary)
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource2'].name == 'SupplyResource2'
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource2'].initial_amount == 100
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                        'SupplyResource2'].current_amount == 100
        assert isinstance(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                           'SupplyResource2'].component_functionality_to_amount, Relation.Linear)
        assert isinstance(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                            'SupplyResource2'].unmet_demand_to_amount, Relation.Constant)
    
    def test_add_resources_demand(self, component):
        component.add_resources(Component.SupplyOrDemand.DEMAND.value,
                                Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, 
                                component_parameters['OperationDemand'])
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}
        assert len(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]) == 2
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource1'].name == 'DemandResource1'
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource1'].initial_amount == 1
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource1'].current_amount == 1
        assert isinstance(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                           'DemandResource1'].component_functionality_to_amount, Relation.Constant)
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource2'].name == 'DemandResource2'
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource2'].initial_amount == 5
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                        'DemandResource2'].current_amount == 5
        assert isinstance(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                           'DemandResource2'].component_functionality_to_amount, Relation.Binary)
        
    def test_add_one_resource_wrong_supply_key_string(self, component):
        with pytest.raises(KeyError):
            component.add_resources(Component.SupplyOrDemand.SUPPLY.value, 
                                    'supply', 
                                    component_parameters['Supply'])

    def test_add_one_resource_wrong_demand_key_string(self, component):
        with pytest.raises(KeyError):
            component.add_resources(Component.SupplyOrDemand.DEMAND.value, 
                                    'operation_demand', 
                                    component_parameters['OperationDemand'])

    def test_add_multiple_resources(self, component):
        resource_dict = {"SupplyResource1": {
                "Amount": 10,
                "FunctionalityToAmountRelation": "Constant",
                "UnmetDemandToAmountRelation": "Binary"
                }
            }
        for _ in range(5):
            component.add_resources(Component.SupplyOrDemand.SUPPLY.value,
                                    Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                    resource_dict)

        for resource in component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value].values():
            assert resource.name == 'SupplyResource1'
            assert resource.initial_amount == 10
            assert resource.current_amount == 10
        
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value] == {}
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

    def test_form_resource_non_consumable(self, component):
        resource_dict = {"SupplyResource1": {
                "Amount": 10,
                "FunctionalityToAmountRelation": "Constant",
                "UnmetDemandToAmountRelation": "Binary"
                }
            }
        resource_name, resource_parameters = list(resource_dict.items())[0]
        resource = component.form_resource(resource_name, resource_parameters)
        assert isinstance(resource, Resource.NonConsumableResource)
        assert resource.name == 'SupplyResource1'
        assert resource.initial_amount == 10
        assert resource.current_amount == 10
        assert isinstance(resource.component_functionality_to_amount, Relation.Constant)
        assert isinstance(resource.unmet_demand_to_amount, Relation.Binary)
    
    def test_form_resource_consumable(self, component):
        resource_dict = {"SupplyResource1": {
                "ResourceClass": "ConsumableResource",
                "Amount": 10,
                "FunctionalityToAmountRelation": "Constant",
                "UnmetDemandToAmountRelation": "Binary"
                }
            }
        resource_name, resource_parameters = list(resource_dict.items())[0]
        resource = component.form_resource(resource_name, resource_parameters)
        assert isinstance(resource, Resource.ConsumableResource)
        assert resource.name == 'SupplyResource1'
        assert resource.initial_amount == 10
        assert resource.current_amount == 10
        assert isinstance(resource.component_functionality_to_amount, Relation.Constant)
        assert isinstance(resource.unmet_demand_to_amount, Relation.Binary)
    
    def test_get_current_resource_amount_no_damage(self, component):
        component.construct(component_name, component_parameters)
        assert component.get_current_resource_amount(Component.SupplyOrDemand.SUPPLY.value, 
                                                    Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                    'SupplyResource1') == 10
        assert component.get_current_resource_amount(Component.SupplyOrDemand.SUPPLY.value, 
                                                    Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                    'SupplyResource2') == 100
        assert component.get_current_resource_amount(Component.SupplyOrDemand.DEMAND.value,
                                                    Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value,
                                                    'DemandResource1') == 1
        assert component.get_current_resource_amount(Component.SupplyOrDemand.DEMAND.value,
                                                    Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value,
                                                    'DemandResource2') == 5
    
    def test_get_current_resource_amount_with_damage(self, component):
        component.construct(component_name, component_parameters)
        component.set_initial_damage_level(0.5)
        component.update(1)
        assert component.get_current_resource_amount(Component.SupplyOrDemand.SUPPLY.value,
                                                    Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                    'SupplyResource1') == 10
        assert component.get_current_resource_amount(Component.SupplyOrDemand.SUPPLY.value,
                                                    Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                    'SupplyResource2') == 50
        assert component.get_current_resource_amount(Component.SupplyOrDemand.DEMAND.value,
                                                    Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value,
                                                    'DemandResource1') == 1
        assert component.get_current_resource_amount(Component.SupplyOrDemand.DEMAND.value,
                                                    Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value,
                                                    'DemandResource2') == 0
        
    def test_update_functionality(self, component):
        component.set_recovery_model(component_parameters['RecoveryModel'])
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
        component.set_recovery_model(component_parameters['RecoveryModel'])
        damage_level = 0.23
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.check_if_functional(time_step=1)
        assert component.functional == [1]

    def test_check_if_functional_full_damage(self, component):
        component.set_recovery_model(component_parameters['RecoveryModel'])
        damage_level = 1.0
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.check_if_functional(time_step=5)   
        assert component.functional == []
    
    def test_check_if_functional_during_recovery(self, component):
        component.set_recovery_model(component_parameters['RecoveryModel'])
        damage_level = 1.0
        component.set_initial_damage_level(damage_level)
        for time_step in range(150):
            component.update_functionality()
            component.check_if_functional(time_step=time_step)
            component.recover(time_step=time_step)
        assert component.functional == list(range(1, 150))
    
    def test_update_resources_based_on_component_functionality(self, component):
        component.construct(component_name, component_parameters)
        damage_level = 0.23
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.update_resources_based_on_component_functionality(Component.SupplyOrDemand.SUPPLY.value,
                                                                    Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value)
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            10)
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].current_amount,
                            100*0.77)
        
        component.update_resources_based_on_component_functionality(Component.SupplyOrDemand.DEMAND.value,
                                                                    Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value)
        assert math.isclose(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource1'].current_amount,
                            1)
        assert math.isclose(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource2'].current_amount,
                            0)
        
    def test_update_supply_based_on_component_functionality(self, component):
        component.construct(component_name, component_parameters)
        damage_level = 0.4
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.update_supply_based_on_component_functionality()
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            10)
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].current_amount,
                            100*0.6)
    
    def test_update_operation_demand(self, component):
        component.construct(component_name, component_parameters)
        assert math.isclose(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource1'].current_amount,
                            1)
        assert math.isclose(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource2'].current_amount,
                            5)    
        damage_level = 1.0
        component.set_initial_damage_level(damage_level)
        component.update_functionality()
        component.update_operation_demand()
        assert math.isclose(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource1'].current_amount,
                            1)
        assert math.isclose(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value][
                                'DemandResource2'].current_amount,
                            0)
    
    def test_update_recovery_demand(self, component):
        component.construct(component_name, component_parameters)
        component.update_recovery_demand()
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}
        component.set_initial_damage_level(0.5)
        component.update_recovery_demand()
        assert math.isclose(component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value][
                                'RecoveryResource1'].current_amount,
                            0.1)
        component.set_initial_damage_level(0)
        component.update_recovery_demand()
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

    def test_set_recovery_model_activities_demand_to_met(self, component):
        component.construct(component_name, component_parameters)
        assert component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] == 1.0
        component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] = 0.5
        component.set_recovery_model_activities_demand_to_met()
        assert component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] == 1.0
    
    def test_update_supply_based_on_unmet_demand(self, component):
        component.construct(component_name, component_parameters)
        percent_of_met_demand = 0.6
        component.update_supply_based_on_unmet_demand(percent_of_met_demand)
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            0)
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].current_amount,
                            100)
    
    def test_update_supply_based_on_consumption(self, component):
        component_parameters['Supply']['SupplyResource1']['ResourceClass'] = 'ConsumableResource'
        component.construct(component_name, component_parameters)
        component.update_supply_based_on_consumption('SupplyResource1', 1)
        component.update_supply_based_on_consumption('SupplyResource2', 1)
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            9)  
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].initial_amount,
                            9) 
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].current_amount,
                            100)
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource2'].initial_amount,
                            100)
        
        component.update_supply_based_on_consumption('SupplyResource1', 10)
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].current_amount,
                            0)  
        assert math.isclose(component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value][
                                'SupplyResource1'].initial_amount,
                            0) 
    
    def test_set_met_demand_for_recovery_activities(self, component):
        component.construct(component_name, component_parameters)
        component.set_met_demand_for_recovery_activities('RecoveryResource1', 0.3)
        assert component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] == 0.3

        component.set_met_demand_for_recovery_activities('RecoveryResource1', 1.0)
        assert component.recovery_model.recovery_activities['Repair'].demand_met['RecoveryResource1'] == 1.0

    def test_recover(self, component):
        component.construct(component_name, component_parameters)
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

    def test_update(self, component):
        component.construct(component_name, component_parameters)
        component.update(0)
        assert component.functionality_level == 1
        assert component.functional == [0]
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 100
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 5
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}

        component.set_initial_damage_level(0.4)
        component.update(1)
        assert component.functionality_level == 0.6
        assert component.functional == [0, 1]
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 60
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 0
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]['RecoveryResource1'].current_amount == 0.1

        component.recover(2)
        component.update(2)
        assert component.functionality_level == 0.604
        assert component.functional == [0, 1, 2]
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 60.4
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 0
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]['RecoveryResource1'].current_amount == 0.1

        for time_step in range (3, 102):
            component.recover(time_step)
            component.update(time_step)
        assert component.get_damage_level() == 0.0
        assert component.recovery_model.recovery_activities['Repair'].time_steps == list(range(2, 102))
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource1'].current_amount == 10
        assert component.supply[Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value]['SupplyResource2'].current_amount == 100
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource1'].current_amount == 1
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]['DemandResource2'].current_amount == 5
        assert component.demand[Component.StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] == {}
    

class TestBuildingStockUnitWithEmergencyCalls():

    @pytest.fixture
    def component(self) -> Component.StandardiReCoDeSComponent:
        return Component.BuildingStockUnitWithEmergencyCalls()
    
    @pytest.fixture
    def component_parameters(self):
        component_parameters['ComponentClass'] = 'BuidlingStockUnitWithEmergencyCalls'
        component_parameters['OperationDemand']['Communication'] = {'Amount': 1.0, 
                                                                    'FunctionalityToAmountRelation': 'Linear',
                                                                    'PostDisasterIncreaseDueToEmergencyCalls': 'True'}
        return component_parameters

    def test_update_communication_demand(self, component, component_parameters):
        component.construct(component_name, component_parameters)
        initial_communication_demand = component.demand['OperationDemand']['Communication'].current_amount
        time_steps = [0, 1, 5, 10, 50]
        target_communication_demands = [initial_communication_demand,
                                        initial_communication_demand * component.COMMUNICATION_DEMAND_MULTIPLIER,
                                        initial_communication_demand * component.COMMUNICATION_DEMAND_MULTIPLIER * math.exp(
                                            component.COMMUNICATION_DEMAND_EXP_DECREASE_COEFF * 4),
                                        initial_communication_demand,
                                        initial_communication_demand]
        for time_step, target_communication_demand in zip(time_steps, target_communication_demands):
            component.update_communication_demand(time_step)
            assert math.isclose(target_communication_demand,
                                component.demand['OperationDemand']['Communication'].current_amount)

    def test_modify_emergency_calls(self, component, component_parameters):
        component.construct(component_name, component_parameters)
        initial_communication_demand = component.demand['OperationDemand']['Communication'].current_amount
        component.COMMUNICATION_RESOURCE_NAME = 'Communication'
        time_steps = [1, 3, 50]
        target_communication_demands = [initial_communication_demand * component.COMMUNICATION_DEMAND_MULTIPLIER,
                                        initial_communication_demand * component.COMMUNICATION_DEMAND_MULTIPLIER * math.exp(
                                            component.COMMUNICATION_DEMAND_EXP_DECREASE_COEFF * 2),
                                        initial_communication_demand]
        for time_step, target_communication_demand in zip(time_steps, target_communication_demands):
            communication_demand = component.modify_emergency_calls_demand(initial_communication_demand, time_step)
            assert math.isclose(communication_demand, target_communication_demand)
    
    def test_check_if_demand_increase_considered(self, component, component_parameters):
        component.check_if_demand_increase_considered('DemandResource1', component_parameters['OperationDemand']['DemandResource1'])
        assert component.COMMUNICATION_RESOURCE_NAME == ''

        component.check_if_demand_increase_considered('SupplyResource1', component_parameters['Supply']['SupplyResource1'])
        assert component.COMMUNICATION_RESOURCE_NAME == ''

        component.check_if_demand_increase_considered('Communication', component_parameters['OperationDemand']['Communication'])
        assert component.COMMUNICATION_RESOURCE_NAME == 'Communication'

class TestInfrastructureInterface():

    supply_dict_simple = {
        "TestInterface": {
                            "Resource": "SupplyInterfaceResource1",
                            "Amount": [100, 200],
                            "RestoredIn": [
                                {
                                    "Lognormal": {
                                        "Median": 20,
                                        "Dispersion": 0
                                    }
                                },
                                {
                                    "Deterministic": {
                                        "Value": 50
                                    }
                                }
                            ],
                            "Demand": {
                                "Resource": "DemandInterfaceResource1",
                                "Amount": 5
                            }
                        }
    }

    supply_dict_complicated = {
        "TestInterface": {
                            "Resource": "SupplyInterfaceResource1",
                            "Amount": [100, 50, 0, 200, 500, 600],
                            "RestoredIn": [
                                {
                                    "Deterministic": {
                                        "Value": 0
                                    }
                                },
                                {
                                    "Lognormal": {
                                        "Median": 20,
                                        "Dispersion": 0
                                    }
                                },
                                {
                                    "Deterministic": {
                                        "Value": 50
                                    }
                                },
                                {
                                    "Deterministic": {
                                        "Value": 80
                                    }
                                },
                                {
                                    "Deterministic": {
                                        "Value": 150
                                    }
                                },
                                {
                                    "Deterministic": {
                                        "Value": 200
                                    }
                                }
                            ],
                            "Demand": {
                                "Resource": "DemandInterfaceResource1",
                                "Amount": 5
                            }
                        }
    }

    @pytest.fixture
    def component(self) -> Component.StandardiReCoDeSComponent:
        return Component.InfrastructureInterface()
    
    @pytest.fixture
    def component_parameters(self) -> dict:
        component_parameters['ComponentClass'] = 'InfrastructureInterface'
        component_parameters['RecoveryModel']['Type'] = 'InfrastructureInterfaceRecoveryModel'
        component_parameters['Supply'] = {'SupplyInterfaceResource1': {'Amount': 0}}                                          
        return component_parameters

    def test_set_supply_dynamics_simple(self, component, component_parameters):
        component.construct(component_name, component_parameters)
        component.set_supply_dynamics(self.supply_dict_simple['TestInterface'])
        assert component.supply['Supply']['SupplyInterfaceResource1'].initial_amount == 200
        assert component.recovery_model.recovery_activities[component.recovery_model.RECOVERY_ACTIVITY_NAME].duration == 50
        assert isinstance(component.recovery_model.damage_to_functionality_relation, Relation.MultipleStep)
        assert component.recovery_model.damage_to_functionality_relation.step_values == [0.5, 1]
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[0], 0.4)
        assert component.recovery_model.damage_to_functionality_relation.step_limits[1] == 1
    
    def test_set_supply_dynamics_complicated(self, component, component_parameters):
        component.construct(component_name, component_parameters)
        component.set_supply_dynamics(self.supply_dict_complicated['TestInterface'])
        assert component.supply['Supply']['SupplyInterfaceResource1'].initial_amount == 600
        assert component.recovery_model.recovery_activities[component.recovery_model.RECOVERY_ACTIVITY_NAME].duration == 200
        assert isinstance(component.recovery_model.damage_to_functionality_relation, Relation.MultipleStep)
        assert component.recovery_model.damage_to_functionality_relation.step_values == [1/6, 1/12, 0, 1/3, 5/6, 1.0]
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[0], 0)
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[1], 0.1)
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[2], 0.25)
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[3], 0.4)
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[4], 0.75)
        assert component.recovery_model.damage_to_functionality_relation.step_limits[-1] == 1
    
    def test_supply_dynamics_values(self, component, component_parameters):
        component.construct(component_name, component_parameters)
        component.set_supply_dynamics(self.supply_dict_complicated['TestInterface'])
        component.supply['Supply']['SupplyInterfaceResource1'].component_functionality_to_amount = Relation.Linear()
        assert component.supply['Supply']['SupplyInterfaceResource1'].initial_amount == 600
        component.set_initial_damage_level(1.0)
        component.update(0)
        assert component.supply['Supply']['SupplyInterfaceResource1'].current_amount == 100
        recovery_time_step_ranges = [1, 5, 20, 21, 35, 50, 60, 85, 130, 180, 200, 500]
        target_supply_amounts = [100, 100, 50, 50, 50, 0, 200, 200, 500, 500, 600]
        for i, recovery_time_step_upper_bound in enumerate(recovery_time_step_ranges[1:]):
            recovery_time_step_lower_bound = recovery_time_step_ranges[i]
            for time_step in range(recovery_time_step_lower_bound, recovery_time_step_upper_bound):
                component.recover(time_step)
                component.update(time_step)
            assert math.isclose(component.supply['Supply']['SupplyInterfaceResource1'].current_amount,
                                target_supply_amounts[i])
