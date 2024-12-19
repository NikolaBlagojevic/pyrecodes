from pyrecodes.resource.consumable_resource import ConsumableResource

class TestConsumableResource():

    def test_consumable_resource_update_based_on_consumption(self):
        resource = ConsumableResource('TestResource', {'Amount': 100})
        # Consumable resource with initial amount 100
        resource.update_based_on_consumption(30)
        # After consumption of 30, the initial and current amounts should be reduced by 30
        assert resource.initial_amount == 70
        assert resource.current_amount == 70

    def test_consumable_resource_update_based_on_consumption_exhausted(self):
        resource = ConsumableResource('TestResource', {'Amount': 30})
        # Consumable resource with initial amount 30
        resource.update_based_on_consumption(50)
        # If consumption exceeds the initial amount, the current amount should be 0
        assert resource.initial_amount == 0
        assert resource.current_amount == 0