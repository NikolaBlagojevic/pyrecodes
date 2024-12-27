from pyrecodes.resource_distribution_model.abstract_resource_distribution_model import AbstractResourceDistributionModel
from pyrecodes.resource_distribution_model.concrete_resource_distribution_model_constructor import ConcreteResourceDistributionModelConstructor
from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand


class BridgeServiceDistributionModel(AbstractResourceDistributionModel):   
    """  
    | Class that captures the effect of bridge functionality on the functionality of components located on a bridge. If the bridge is not functional, the components (e.g., roadways, power lines) on the bridge are not functional either.
    | Bridge service cannot be consumable with the current implementation.
    """    

    def __init__(self, resource_name: str, resource_parameters: dict, components: list([Component])) -> None:
        self.constructor = ConcreteResourceDistributionModelConstructor()
        self.constructor.construct(resource_name, resource_parameters, components, self)
        self.find_bridges()
        self.map_links_to_bridges()
    
    def find_bridges(self):
        self.bridges = []
        for component in self.components:
            if self.component_is_a_bridge(component):
                self.bridges.append(component)
    
    def component_is_a_bridge(self, component):
        """
        | Method to identify components that are bridges.
        | This method is a workaround until a Bridge class is created. Then check the class name instead of the component name.
        """
        return 'Bridge' in component.name
    
    def map_links_to_bridges(self):
        """
        Find all links that are on a bridge.
        """
        self.links_on_a_bridge = [[] for _ in range(len(self.bridges))]
        for bridge_id, bridge_component in enumerate(self.bridges):
            for component in self.components:
                if self.component_is_on_the_bridge(component, bridge_component) and not(self.component_is_a_bridge(component)):
                    self.links_on_a_bridge[bridge_id].append(component)
    
    def component_is_on_the_bridge(self, component, bridge_component):
        """
        | Method to identify components that are on a bridge.
        | Assume bridges are in a single direction - that's why use sort.
        """
        component_localities = component.get_locality()
        bridges_localities = bridge_component.get_locality()
        return component_localities == bridges_localities 
    
    def distribute(self, time_step: int) -> None:
        if self.distribute_at_this_time_step(time_step):
            for bridge_id, bridge in enumerate(self.bridges):
                bridge_supply = bridge.get_current_resource_amount(SupplyOrDemand.SUPPLY.value, 
                                                        StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                                        self.resource_name)
                for link in self.links_on_a_bridge[bridge_id]:
                    bridge_demand = link.get_current_resource_amount(SupplyOrDemand.DEMAND.value, 
                                                        StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, 
                                                        self.resource_name)
                    percent_of_met_demand = min(1.0, bridge_supply/bridge_demand)
                    link.update_supply_based_on_unmet_demand(percent_of_met_demand)
    
    def get_total_supply(self) -> float:
        print(f'System supply for bridge service {self.resource_name} not defined yet.')
        return None
    
    def get_total_demand(self) -> float:
        print(f'System demand for bridge service {self.resource_name} not defined yet.')
        return None
    
    def get_total_consumption(self) -> float:
        print(f'System consumption for bridge service {self.resource_name} not defined yet.')
        return None

