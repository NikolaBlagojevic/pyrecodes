import pytest
from pyrecodes.resource.concrete_resource import ConcreteResource
from pyrecodes.relation import relation

RESOURCE_NAME = 'Resource 1'
INITIAL_AMOUNT = 5.0
RESOURCE_PARAMETERS = {'Amount': 100, 'FunctionalityToAmountRelation': 'Linear', 'UnmetDemandToAmountRelation': 'Constant'}

class TestConcreteResource():
    RESOURCE_NAME = 'Resource 1'
    INITIAL_AMOUNT = 5.0

    def test_concrete_resource_initialization(self):
        resource = ConcreteResource('TestResource', RESOURCE_PARAMETERS)
        assert resource.name == 'TestResource'
        assert resource.initial_amount == 100
        assert resource.current_amount == 100
        assert isinstance(resource.component_functionality_to_amount, relation.Linear)
        assert isinstance(resource.unmet_demand_to_amount, relation.Constant)
    
    def test_concrete_resource_initialization_with_no_parameters(self):
        resource = ConcreteResource('TestResource', {})
        assert resource.name == 'TestResource'
        assert resource.initial_amount == 0
        assert resource.current_amount == 0
        assert isinstance(resource.component_functionality_to_amount, relation.Constant)
        assert isinstance(resource.unmet_demand_to_amount, relation.Constant)
    
    def test_set_initial_amount_positive(self):
        resource = ConcreteResource('TestResource', {})
        resource.set_initial_amount(50)
        assert resource.current_amount == 50 and resource.initial_amount == 50

    def test_set_initial_amount_negative(self):
        resource = ConcreteResource('TestResource', {})
        with pytest.raises(ValueError):
            resource.set_initial_amount(-50)
    
    def test_set_current_amount_positive(self):
        resource = ConcreteResource('TestResource', {})
        resource.set_current_amount(50)
        assert resource.current_amount == 50 and resource.initial_amount == 0

    def test_set_current_amount_negative(self):
        resource = ConcreteResource('TestResource', {})
        with pytest.raises(ValueError):
            resource.set_current_amount(-50)

    def test_set_relation(self):
        resource = ConcreteResource('TestResource', {})
        resource.set_relation('Linear', 'component_functionality_to_amount')
        assert isinstance(resource.component_functionality_to_amount, relation.Linear)
        resource.set_relation('Constant', 'unmet_demand_to_amount')
        assert isinstance(resource.unmet_demand_to_amount, relation.Constant)
        with pytest.raises(ValueError):
            resource.set_relation('NotARelation', 'component_functionality_to_amount')
    
    def test_update_based_on_component_functionality_linear_relation(self):
        parameters = {'Amount': 100, 'FunctionalityToAmountRelation': 'Linear'}
        resource = ConcreteResource('TestResource', parameters)

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
        resource = ConcreteResource('TestResource', parameters)

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
        resource = ConcreteResource('TestResource', parameters)

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
        resource = ConcreteResource('TestResource', parameters)

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
        resource = ConcreteResource('TestResource', parameters)
        with pytest.raises(ValueError):
            resource.update_based_on_component_functionality(-5)

    def test_update_based_on_unmet_demand_constant_relation(self):
        parameters = {'Amount': 100, 'UnmetDemandToAmountRelation': 'Constant'}
        resource = ConcreteResource('TestResource', parameters)

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
        resource = ConcreteResource('TestResource', parameters)

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
        resource = ConcreteResource('TestResource', parameters)
        with pytest.raises(ValueError):
            resource.update_based_on_unmet_demand(-5)

    def test_update_based_on_unmet_demand_binary_relation(self):
        parameters = {'Amount': 100, 'UnmetDemandToAmountRelation': 'Binary'}
        resource = ConcreteResource('TestResource', parameters)

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
        resource = ConcreteResource('TestResource', {'Amount': 100})
        # Non-consumable resources should not be affected by consumption
        resource.update_based_on_consumption(50)
        assert resource.initial_amount == 100
        assert resource.current_amount == 100