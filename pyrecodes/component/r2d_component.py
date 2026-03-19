from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import Bridge, Roadway, Tunnel

class R2DComponent(StandardiReCoDeSComponent):
    """
    Class used to simulate components created using R2D outputs.

    Note that SimCenter's infrastructure simulators (REWET, residual demand) only work with R2DComponent objects.
    """
    def update(self, time_step: int, *args) -> None:
        """
        Extend the parent method to update the R2D dictionary used to interface pyrecodes with SimCenter's infrastructure simulators.
        """
        super().update(time_step)
        self.update_r2d_dict()

    def update_r2d_dict(self, demand_types=[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]) -> None:
        """
        Update the R2D dictionary with the current resource demand of the component. SimCenter's infrastructure simulators get component's demand from this dictionary.
        """
        for demand_type in demand_types:
            for resource in self.demand[demand_type].values():
                self.general_information[demand_type][resource.name] = resource.current_amount

class R2DTransportationComponent(R2DComponent):
    """
    Subclass used to identify transportation components in a system. For now that's the only purpose.

    """

    def update_r2d_dict(self) -> None:
        """
        Update the resource-to-damage dictionary based on the current damage level of the pipe.
        """
        self.general_information['FunctionalityLevel'] = self.functionality_level

class R2DBridge(Bridge, R2DTransportationComponent):
    """R2D implementation of a bridge component."""
    def __init__(self) -> None:
        super().__init__()
        self.general_information = {'FunctionalityLevel': 1.0}

class R2DRoadway(Roadway, R2DTransportationComponent):
    """R2D implementation of a roadway component."""
    def __init__(self) -> None:
        super().__init__()
        self.general_information = {'FunctionalityLevel': 1.0}

class R2DTunnel(Tunnel, R2DTransportationComponent):
    """R2D implementation of a tunnel component."""
    def __init__(self) -> None:
        super().__init__()
        self.general_information = {'FunctionalityLevel': 1.0}

class R2DPipe(R2DComponent):
    """
    Subclass representing pipes in a water distribution system defined using the R2D files as inputs.
    """

    def __init__(self) -> None:
        super().__init__()
        self.damage_information = {'Location': [], 'Type': []}
        self.general_information = {'Status': 'OPEN'}

    def update_r2d_dict(self) -> None:
        """
        Extend the parent method to update the functionality parameter of an R2DPipe in the R2D dictionary based on its functionality level.
        """
        super().update_r2d_dict()
        if self.functionality_level < 1.0:
            self.general_information['Status'] = 'CLOSED'
        elif self.functionality_level == 1.0:
            self.general_information['Status'] = 'OPEN'
            self.damage_information  = {'Location': [], 'Type': []}

class R2DBuilding(R2DComponent):
    """
    Class used to represent buildings in a system when using the R2D files as inputs.
    """

    def __init__(self) -> None:
        super().__init__()
        self.general_information = {'PopulationRatio': 1.0}

    def update_r2d_dict(self):
        """
        Extend the parent method to update the ratio of the population in the building at a time step in the R2D dictionary based on the functionality level.
        The population ratio is used by SimCenter infrastructure simulators (residual demand) to calculate the demand for resources.
        """
        super().update_r2d_dict()
        self.general_information['PopulationRatio'] = self.functionality_level
    