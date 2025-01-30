from pyrecodes.resource_distribution_model.abstract_resource_distribution_model import AbstractResourceDistributionModel
from pyrecodes.resource_distribution_model.residual_demand_traffic_distribution_model_constructor import ResidualDemandTrafficDistributionModelConstructor
from pyrecodes.resource_distribution_model.spatial_resource_aggregator import SpatialResourceAggregator
from pyrecodes.component.component import Component

import subprocess
import os

class ResidualDemandTrafficDistributionModel(AbstractResourceDistributionModel):

    def __init__(self, resource_name: str, resource_parameters: dict, components: list[Component]):
        self.constructor = ResidualDemandTrafficDistributionModelConstructor()
        self.constructor.construct(resource_name, resource_parameters, components, self)
        self.transfer_service_distribution_model = None #consider moving this into the constructor or finding a better solution-the point is to have an initial value for this property
        self.spatial_resource_aggregator = SpatialResourceAggregator()
        self.travel_times = []

    def distribute(self, time_step: int) -> None:
        """
        | Calculate travel times if the model is supposed to distribute traffic at this time step.
        | If not, append an empty list to the travel_times list to keep the length of the list consistent with the number of time steps.
        """
        if self.distribute_at_this_time_step(time_step):
            self.update_r2d_dict()
            self.distribute_traffic()
        else:
            self.travel_times.append([])

    def update_r2d_dict(self):
        """
        | Method to update the r2d_dict based on the current state of the components.
        | At the moment, the r2d_dict is created from scratch at each time step. Not efficient, optimize later.
        """
        self.r2d_dict = self.constructor.create_r2d_dict(self.components)

    def distribute_traffic(self) -> None:
        """
        | Run the traffic simulator to calculate travel times.
        | Supress output to the console from low-level libraries.
        """
        with open(os.devnull, 'w') as devnull:
            original_stdout_fd = os.dup(1) 
            try:
                os.dup2(devnull.fileno(), 1) 
                self.travel_times.append(self.flow_simulator.simulate(self.r2d_dict))
            finally:
                os.dup2(original_stdout_fd, 1)  
                os.close(original_stdout_fd) 
          
    def get_total_supply(self, scope: str) -> float:
        """
        Supply is calculated the same as consumption.
        """
        return self.get_total_consumption(scope)

    def get_total_demand(self, scope: str) -> float:
        """
        | Demand for the transportation service is the number of agents that need to travel from one location to another.
        | If traffic is not distributed at the current time step, demand is 0.
        """
        if scope == 'All':
            if len(self.travel_times[-1]) > 0:
                return len(self.travel_times[-1])
            else:
                return 0
        else:
            raise ValueError("Scope not implemented. Only 'All' is supported.")

    def get_total_consumption(self, scope: str) -> float:
        """
        | Consumption of the transportation service is the number of agents whose travel time is not extended beyond the pre-disaster time times the TRIP_CUTOFF_THRESHOLD.
        | If traffic is not distributed at the current time step, consumption is 0.
        """
        if scope == 'All':
            if len(self.travel_times[-1]) > 0:
                completed_trips = 0
                for agent_pre_disaster, agent_now in zip(self.travel_times[0]['travel_time_used'], self.travel_times[-1]['travel_time_used']):
                    if agent_pre_disaster * self.TRIP_CUTOFF_THRESHOLD >= agent_now:
                        completed_trips += 1
                return completed_trips
            else:
                return 0
        else:
            raise ValueError("Scope not implemented. Only 'All' is supported.")
        
