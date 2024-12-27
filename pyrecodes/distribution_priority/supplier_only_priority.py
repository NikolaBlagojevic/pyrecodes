from pyrecodes.component.component import Component
from pyrecodes.distribution_priority.distribution_priority import DistributionPriority
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent

class SupplierOnlyPriority(DistributionPriority):
    """
    | Find all components that have a supply for a specified resource and only include those components when distributing a resource.
    | Used for housing service distribution, as it only considers components with housing supply when distributing housing services. Makes housing distribution faster.
    | Considers Operation Demand only.
    """

    def __init__(self, resource_name: str, parameters: dict, components: list[Component]):
        self.resource_name = resource_name
        self.components = components
        self.set_distribution_priority(parameters)

    def set_distribution_priority(self, parameters) -> None:
        residential_building_ids = []
        for component_id, component in enumerate(self.components):
            if component.has_resource_supply(self.resource_name) > 0:
                residential_building_ids.append(component_id)
        self.distribution_priority = residential_building_ids, [
            StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value for _ in residential_building_ids]

    def get_component_priorities(self) -> list[int]:
        return self.distribution_priority