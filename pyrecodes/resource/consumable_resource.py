from pyrecodes.resource.concrete_resource import ConcreteResource

class ConsumableResource(ConcreteResource):
    """
    | Class to simulate a resource whose supply decreases when it is consumed.

    | Both initial and current amounts are reduced by the consumption amount. 

    | The reason is that the initial amount represents the amount that the component provides when 
    functionality level is 1 and this value is also decreased for a consumable resource.
    """

    def update_based_on_consumption(self, consumption: float) -> None:
        self.initial_amount = max(self.initial_amount - consumption, 0)
        self.current_amount = max(self.current_amount - consumption, 0)