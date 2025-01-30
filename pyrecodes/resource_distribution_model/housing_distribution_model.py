from pyrecodes.resource_distribution_model.abstract_resource_distribution_model import AbstractResourceDistributionModel
from pyrecodes.resource_distribution_model.concrete_resource_distribution_model_constructor import ConcreteResourceDistributionModelConstructor
from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand

class HousingDistributionModel(AbstractResourceDistributionModel):
    """
    | Class to distribute housing resources in the system. 

    | This class checks whether people living in a house can keep living there - it compares a house's supply of housing with its demand for housing.
    | Does not account for temporary shelter or distribution of people between houses.
    """

    def __init__(self, resource_name: str, resource_parameters: dict, components: list[Component]):
        self.constructor = ConcreteResourceDistributionModelConstructor()
        self.constructor.construct(resource_name, resource_parameters, components, self)
        self.transfer_service_distribution_model = None

    def distribute(self, time_step: int) -> None:
        if self.distribute_at_this_time_step(time_step):
            for component in self.components:
                self.distribute_housing_within_component(component)
    
    def distribute_housing_within_component(self, component: Component) -> None:
        housing_supply = component.get_current_resource_amount(SupplyOrDemand.SUPPLY.value, 
                                                                StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                                                self.resource_name)
        housing_demand = component.get_current_resource_amount(SupplyOrDemand.DEMAND.value, 
                                                                StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, 
                                                                self.resource_name)   
        if housing_demand > 0.0:
            percent_of_met_demand = min(1.0, housing_supply/housing_demand)
            component.update_supply_based_on_unmet_demand(percent_of_met_demand)

    def get_total_supply(self, scope: str) -> float:
        components_to_include = self.get_scope(scope)
        total_supply = 0
        for component in components_to_include:
            housing_supply = component.get_current_resource_amount(SupplyOrDemand.SUPPLY.value, 
                                                                StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                                                self.resource_name)
            total_supply += housing_supply
        return total_supply            

    def get_total_demand(self, scope: str) -> float:
        components_to_include = self.get_scope(scope)
        total_demand = 0
        for component in components_to_include:
            housing_demand = component.get_current_resource_amount(SupplyOrDemand.DEMAND.value, 
                                                                StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, 
                                                                self.resource_name)
            total_demand += housing_demand
        return total_demand

    def get_total_consumption(self, scope: str) -> float:
        components_to_include = self.get_scope(scope)
        total_consumption = 0
        for component in components_to_include:
            housing_demand = component.get_current_resource_amount(SupplyOrDemand.DEMAND.value, 
                                                                StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, 
                                                                self.resource_name)
            housing_supply = component.get_current_resource_amount(SupplyOrDemand.SUPPLY.value, 
                                                                StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                                                self.resource_name)
            total_consumption += min(housing_demand, housing_supply)
        return total_consumption
