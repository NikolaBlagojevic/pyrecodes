from pyrecodes.constants import SECONDS_IN_TIME_STEP
from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.r2d_component import R2DBuilding
from pyrecodes.resource_distribution_model.abstract_resource_distribution_model import AbstractResourceDistributionModel
from pyrecodes.resource_distribution_model.rewet_distribution_model_constructor import REWETDistributionModelConstructor
from pyrecodes.resource_distribution_model.spatial_resource_aggregator import SpatialResourceAggregator
from pyrecodes.component.component import SupplyOrDemand

class REWETDistributionModel(AbstractResourceDistributionModel):
    """
    | Class that connects pyrecodes with the REWET water flow simulator.
    """

    def __init__(self, resource_name: str, resource_parameters: dict, components: list[Component]):
        self.constructor = REWETDistributionModelConstructor()
        self.constructor.construct(resource_name, resource_parameters, components, self)
        self.transfer_service_distribution_model = None
        self.spatial_resource_aggregator = SpatialResourceAggregator()

    def distribute(self, time_step: int) -> None:
        if self.distribute_at_this_time_step(time_step):
            self.update_r2d_dict()
            self.met_demand_per_building = self.distribute_water(time_step)
            self.update_buildings_met_demand()

    def update_r2d_dict(self):
        """
        | Method to update the r2d_dict based on the current state of the components.
        | At the moment, the r2d_dict is created from scratch at each time step. Not efficient, optimize later.
        """
        self.r2d_dict = self.constructor.create_r2d_dict(self.components)

    def distribute_water(self, time_step: int) -> None:
        """
        | Method to distribute water using the REWET water flow simulator.
        | Returns a dictionary with the met demand for each building.
        | REWET outputs met demand ratios slightly higher than 1.0 and lower than 0.0, this is normalized to the [0, 1] range.
        """
        met_demand_per_building = self.flow_simulator.system_performance(self.r2d_dict, current_time=time_step*SECONDS_IN_TIME_STEP, next_time=(time_step+1)*SECONDS_IN_TIME_STEP)
        for building in met_demand_per_building.keys():
            met_demand_per_building[building] = max(0.0, min(1.0, met_demand_per_building[building]))
        return met_demand_per_building
    
    def update_buildings_met_demand(self) -> None:
        """
        | Update supply of buildings based on their met demand for water.
        | At the moment, updates only R2DBuilding components
        """
        for component in self.components:            
            if self.component_is_a_building(component) and self.component_has_demand_for_water(component):
                component.update_supply_based_on_unmet_demand(self.met_demand_per_building[component.aim_id])

    def component_is_a_building(self, component) -> bool:
        """
        | Method to check if a component is a building.
        | At the moment, only R2DBuilding components are considered buildings.
        """
        return isinstance(component, R2DBuilding)
    
    def component_has_demand_for_water(self, component: Component) -> bool:
        return component.get_current_resource_amount(SupplyOrDemand.DEMAND.value, 
                                                    StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, 
                                                    self.resource_name) > 0.0

    def get_total_supply(self, scope='All') -> float:
        """
        | Assume supply equal to consumption at this point. TODO: Figure out how to change later.
        """
        return self.get_total_consumption(scope)

    def get_total_demand(self, scope='All') -> float:
        if scope == "All":
            return self.spatial_resource_aggregator.aggregate_total(self.components, self.resource_name)
        elif "Locality" in scope:
            locality_id = int(scope[-1])
            return self.water_demand_per_locality[locality_id]

    def get_total_consumption(self, scope='All') -> float:
        total_consumption = 0
        if scope == "All":
            for component in self.components:
                component_demand = component.get_current_resource_amount(SupplyOrDemand.DEMAND.value, 
                                                                         StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, 
                                                                         self.resource_name)
                if component_demand > 0:
                    total_consumption += self.met_demand_per_building[component.aim_id] * component_demand
        else:
            raise ValueError('Scope of the resilience calculator not yet implemented in the REWET Distribution Model.') 
        
        return total_consumption

