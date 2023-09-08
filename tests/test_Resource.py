import pytest
from pyrecodes import Resource
from pyrecodes import Relation


class TestResource():
    test_resource_name = 'Resource 1'
    test_initial_amount = 5.0

    def test_concrete_resource_initialization(self):
        parameters = {'Amount': 100, 'FunctionalityToAmountRelation': 'Linear', 'UnmetDemandToAmountRelation': 'Constant'}
        resource = Resource.ConcreteResource('TestResource', parameters)
        assert resource.name == 'TestResource'
        assert resource.initial_amount == 100
        assert resource.current_amount == 100
        assert isinstance(resource.component_functionality_to_amount, Relation.Linear)
        assert isinstance(resource.unmet_demand_to_amount, Relation.Constant)
    
    def test_concrete_resource_initialization_with_no_parameters(self):
        resource = Resource.ConcreteResource('TestResource', {})
        assert resource.name == 'TestResource'
        assert resource.initial_amount == 0
        assert resource.current_amount == 0
        assert isinstance(resource.component_functionality_to_amount, Relation.Constant)
        assert isinstance(resource.unmet_demand_to_amount, Relation.Constant)
    
    def test_set_initial_amount_positive(self):
        resource = Resource.ConcreteResource('TestResource', {})
        resource.set_initial_amount(50)
        assert resource.current_amount == 50 and resource.initial_amount == 50

    def test_set_initial_amount_negative(self):
        resource = Resource.ConcreteResource('TestResource', {})
        with pytest.raises(ValueError):
            resource.set_initial_amount(-50)
    
    def test_set_current_amount_positive(self):
        resource = Resource.ConcreteResource('TestResource', {})
        resource.set_current_amount(50)
        assert resource.current_amount == 50 and resource.initial_amount == 0

    def test_set_current_amount_negative(self):
        resource = Resource.ConcreteResource('TestResource', {})
        with pytest.raises(ValueError):
            resource.set_current_amount(-50)

    def test_set_relation(self):
        resource = Resource.ConcreteResource('TestResource', {})
        resource.set_relation('Linear', 'component_functionality_to_amount')
        assert isinstance(resource.component_functionality_to_amount, Relation.Linear)
        resource.set_relation('Constant', 'unmet_demand_to_amount')
        assert isinstance(resource.unmet_demand_to_amount, Relation.Constant)
        with pytest.raises(ValueError):
            resource.set_relation('NotARelation', 'component_functionality_to_amount')
    
    def test_update_based_on_component_functionality_linear_relation(self):
        parameters = {'Amount': 100, 'FunctionalityToAmountRelation': 'Linear'}
        resource = Resource.ConcreteResource('TestResource', parameters)

        # Set the component functionality level to 0.5
        resource.update_based_on_component_functionality(0.5)
        # The current amount should be 0.5 * 100 = 50
        assert resource.current_amount == 50
        assert resource.initial_amount == 100

        # Set the component functionality level to 0
        resource.update_based_on_component_functionality(0)
        # The current amount should be 0 * 100 = 0
        assert resource.current_amount == 0
        assert resource.initial_amount == 100

        # Set the component functionality level to 1
        resource.update_based_on_component_functionality(1)
        # The current amount should be 1 * 100 = 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100
    
    def test_update_based_on_component_functionality_binary_relation(self):
        parameters = {'Amount': 100, 'FunctionalityToAmountRelation': 'Binary'}
        resource = Resource.ConcreteResource('TestResource', parameters)

        # Set the component functionality level to 0.5
        resource.update_based_on_component_functionality(0.5)
        # The current amount should be 0.0 * 100 = 0.0
        assert resource.current_amount == 0.0
        assert resource.initial_amount == 100

        # Set the component functionality level to 0
        resource.update_based_on_component_functionality(0)
        # The current amount should be 0 * 100 = 0
        assert resource.current_amount == 0
        assert resource.initial_amount == 100

        # Set the component functionality level to 1
        resource.update_based_on_component_functionality(1)
        # The current amount should be 1 * 100 = 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100

    def test_update_based_on_component_functionality_linear_relation(self):
        parameters = {'Amount': 100, 'FunctionalityToAmountRelation': 'Linear'}
        resource = Resource.ConcreteResource('TestResource', parameters)

        # Set the component functionality level to 0.5
        resource.update_based_on_component_functionality(0.5)
        # The current amount should be 0.5 * 100 = 50
        assert resource.current_amount == 50
        assert resource.initial_amount == 100

        # Set the component functionality level to 0
        resource.update_based_on_component_functionality(0)
        # The current amount should be 0 * 100 = 0
        assert resource.current_amount == 0
        assert resource.initial_amount == 100

        # Set the component functionality level to 1
        resource.update_based_on_component_functionality(1)
        # The current amount should be 1 * 100 = 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100
    
    def test_update_based_on_component_functionality_constant_relation(self):
        parameters = {'Amount': 100, 'FunctionalityToAmountRelation': 'Constant'}
        resource = Resource.ConcreteResource('TestResource', parameters)

        # Set the component functionality level to 0.5
        resource.update_based_on_component_functionality(0.5)
        # The current amount should be 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100

        # Set the component functionality level to 0
        resource.update_based_on_component_functionality(0)
        # The current amount should be 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100

        # Set the component functionality level to 1
        resource.update_based_on_component_functionality(1)
        # The current amount should be 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100
    
    def test_update_based_on_component_functionality_wrong_input(self):
        parameters = {'Amount': 100, 'FunctionalityToAmountRelation': 'Linear'}
        resource = Resource.ConcreteResource('TestResource', parameters)
        with pytest.raises(ValueError):
            resource.update_based_on_component_functionality(-5)

    def test_update_based_on_unmet_demand_constant_relation(self):
        parameters = {'Amount': 100, 'UnmetDemandToAmountRelation': 'Constant'}
        resource = Resource.ConcreteResource('TestResource', parameters)

        # Set the unmet demand to 0.5
        resource.update_based_on_unmet_demand(0.5)
        # The current amount should be 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100

        # Set the unmet demand to 0
        resource.update_based_on_unmet_demand(0)
        # The current amount should be 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100

        # Set the unmet demand to 1
        resource.update_based_on_unmet_demand(1)
        # The current amount should be 100
        assert resource.current_amount == 100
        assert resource.initial_amount == 100
    
    def test_update_based_on_unmet_demand_linear_relation(self):
        parameters = {'Amount': 100, 'UnmetDemandToAmountRelation': 'Linear'}
        resource = Resource.ConcreteResource('TestResource', parameters)

        # Set the unmet demand to 0.5
        resource.update_based_on_unmet_demand(0.5)
        # The current amount should be 50
        assert resource.current_amount == 50
        assert resource.initial_amount == 100

        # Set the unmet demand to 0
        resource.update_based_on_unmet_demand(0)
        # The current amount should be 100
        assert resource.current_amount == 0
        assert resource.initial_amount == 100

        # Set the unmet demand to 1
        resource.update_based_on_unmet_demand(1)
        # The current amount should still be 0
        assert resource.current_amount == 0
        assert resource.initial_amount == 100
    
    def test_update_based_on_unmet_demand_wrong_input(self):
        parameters = {'Amount': 100, 'UnmetDemandToAmountRelation': 'Linear'}
        resource = Resource.ConcreteResource('TestResource', parameters)
        with pytest.raises(ValueError):
            resource.update_based_on_unmet_demand(-5)

    def test_update_based_on_unmet_demand_binary_relation(self):
        parameters = {'Amount': 100, 'UnmetDemandToAmountRelation': 'Binary'}
        resource = Resource.ConcreteResource('TestResource', parameters)

        # Set the unmet demand to 0.5
        resource.update_based_on_unmet_demand(0.5)
        # The current amount should be 100
        assert resource.current_amount == 0
        assert resource.initial_amount == 100

        # Set the unmet demand to 0
        resource.update_based_on_unmet_demand(0)
        # The current amount should be 100
        assert resource.current_amount == 0
        assert resource.initial_amount == 100

        # Set the unmet demand to 1
        resource.update_based_on_unmet_demand(1)
        # The current amount should still be 0
        assert resource.current_amount == 0
        assert resource.initial_amount == 100
    
    def test_non_consumable_resource_update_based_on_consumption(self):
        resource = Resource.NonConsumableResource('TestResource', {'Amount': 100})
        # Non-consumable resources should not be affected by consumption
        resource.update_based_on_consumption(50)
        assert resource.initial_amount == 100
        assert resource.current_amount == 100
    
    def test_consumable_resource_update_based_on_consumption(self):
        resource = Resource.ConsumableResource('TestResource', {'Amount': 100})
        # Consumable resource with initial amount 100
        resource.update_based_on_consumption(30)
        # After consumption of 30, the initial and current amounts should be reduced by 30
        assert resource.initial_amount == 70
        assert resource.current_amount == 70

    def test_consumable_resource_update_based_on_consumption_exhausted(self):
        resource = Resource.ConsumableResource('TestResource', {'Amount': 30})
        # Consumable resource with initial amount 30
        resource.update_based_on_consumption(50)
        # If consumption exceeds the initial amount, the current amount should be 0
        assert resource.initial_amount == 0
        assert resource.current_amount == 0
     



