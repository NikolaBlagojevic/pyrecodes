from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from abc import ABC, abstractmethod

class AbstractResourceDistributionModel(ResourceDistributionModel):
    """
    Abstract class for the Resource Distribution Model.
    """

    def set_distribution_time_steps(self, distribution_time_steps: list) -> None:
        self.distribution_time_steps = distribution_time_steps
    
    @abstractmethod
    def distribute(self, time_step: int) -> None:
        pass

    def distribute_at_this_time_step(self, time_step: int) -> bool:
        """
        | Check whether to run resource distribution at a time step.

        | True if time step is in the distribution_time_steps list or if the list is empty - this implies that it was not specified by the user and the resource is distributed at each time step by default.
        """
        return time_step in self.distribution_time_steps or len(self.distribution_time_steps) == 0
    
    def get_scope(self, scope='All') -> list:
        """
        | Get the scope of the ReCoDeS Resilience Calculator to get total supply and demand.

        | Scope can be 'All', icnluding all components, or 'Locality X', including only components in the locality, where X is the locality number.
        """
        if scope == 'All':
            return self.components
        elif "Locality" in scope:
            locality_id = int(scope[-1])
            components_in_scope = []
            for component in self.components:
                if locality_id in component.locality:
                    components_in_scope.append(component)
            return components_in_scope
        else:
            raise ValueError('Scope of the Resilience Calculator not well defined: All or Locality X.')

    @abstractmethod
    def get_total_supply(self, scope: str) -> float:
        pass

    @abstractmethod
    def get_total_demand(self, scope: str) -> float:
        pass

    @abstractmethod
    def get_total_consumption(self, scope: str) -> float:
        pass
