from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand


class SpatialResourceAggregator():
    """
    | Class to aggregate resources for a specific spatial unit. At the moment, the spatial unit is a locality.

    | Used to get the water demand in a locality at different time steps to send to water flow simulators.
    | **TODO**: Maybe connect this class with the resilience calculators, as it seems to be doing something similar.
    """

    def aggregate_per_locality(self, components: list[Component], resource_name: str, 
                               supply_or_demand=SupplyOrDemand.DEMAND.value,
                               supply_or_demand_type=StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value) -> float:
        """
        Aggregate the supply or demand for a resource per locality.
        """
        resource_per_locality = {}
        for component in components:
            if component.locality[0] in resource_per_locality.keys():
                resource_per_locality[component.locality[0]] += component.get_current_resource_amount(supply_or_demand, supply_or_demand_type, resource_name)
            else:
                resource_per_locality[component.locality[0]] = component.get_current_resource_amount(supply_or_demand, supply_or_demand_type, resource_name)
        return resource_per_locality
    
    def aggregate_total(self, components: list[Component], resource_name: str, 
                        supply_or_demand=SupplyOrDemand.DEMAND.value,
                        supply_or_demand_type=StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value) -> float:
        """
        Aggregate the total supply or demand for a resource in the system.
        """
        total_resource = 0
        for component in components:
            total_resource += component.get_current_resource_amount(supply_or_demand, supply_or_demand_type, resource_name)
        return total_resource