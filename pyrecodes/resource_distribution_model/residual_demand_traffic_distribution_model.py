from pyrecodes.resource_distribution_model.abstract_resource_distribution_model import AbstractResourceDistributionModel
from pyrecodes.resource_distribution_model.residual_demand_traffic_distribution_model_constructor import ResidualDemandTrafficDistributionModelConstructor
from pyrecodes.resource_distribution_model.spatial_resource_aggregator import SpatialResourceAggregator
from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand

class ResidualDemandTrafficDistributionModel(AbstractResourceDistributionModel):
    """
    | Class that connects pyrecodes with the residual demand traffic simulator.

    | **TODO**: Implement the class once the residual demand traffic distribution model is implemented.
    """

    def __init__(self, resource_name: str, resource_parameters: dict, components: list([Component])):
        self.constructor = ResidualDemandTrafficDistributionModelConstructor()
        self.constructor.construct(resource_name, resource_parameters, components, self)
        self.transfer_service_distribution_model = None #consider moving this into the constructor or finding a better solution-the point is to have an initial value for this property
        self.spatial_resource_aggregator = SpatialResourceAggregator()

    def distribute(self, time_step: int) -> None:
        if self.distribute_at_this_time_step(time_step):
            self.update_r2d_dict()
            self.update_od_matrix()
            self.distribute_traffic()

    def update_r2d_dict(self):
        # update the values for each component related to its functionality in the dict that follows the structure of the R2D JSON files 
        self.r2d_dict = self.r2d_dict

    def distribute_traffic(self):
        # Call the residual demand traffic simulator to distribute traffic. Not sure what to do with travel times atm, save them as file or store as a property?
        pass
        # self.travel_times = self.traffic_simulator(self.r2d_dict, self.od_matrix, hour_list=list(range(5, 24)), quarter_list=[0,1,2,3,4,5], closure_hours=[])
            
    def update_od_matrix(self):
        # modify the od matrix based on population dislocation 
        # if it's possible to create the od matrix based on r2d json, than this method is not needed
        population_per_locality = self.spatial_resource_aggregator.aggregate_per_locality(self.components, 'Shelter', supply_or_demand=SupplyOrDemand.SUPPLY.value, supply_or_demand_type=StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value)
        self.od_matrix = self.change_od_matrix_based_on_population_dislocation(population_per_locality)

    def change_od_matrix_based_on_population_dislocation(self, population_per_locality: dict) -> dict:
        # modify the od matrix based on population dislocation
        return self.od_matrix

    def get_total_supply(self, scope: str) -> float:
        pass

    def get_total_demand(self, scope: str) -> float:
        pass

    def get_total_consumption(self, scope: str) -> float:
        pass