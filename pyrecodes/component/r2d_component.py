from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent

class R2DComponent(StandardiReCoDeSComponent):
    """
    Class used to simulate components created using R2D outputs.
    At the moment, used only to identify R2D components in the system.

    TODO: Add specific R2D component methods and attributes. Future work.
    """
    def update(self, time_step: int) -> None:
        """
        Update the component based on the current time step.
        """
        super().update(time_step)
        self.update_r2d_dict()

    def update_r2d_dict(self, demand_types=[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value, StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]) -> None:
        for demand_type in demand_types:
            for resource in self.demand[demand_type].values():
                self.general_information[demand_type][resource.name] = resource.current_amount

class R2DBridge(R2DComponent):
    """
    Subclass used to identify bridges in a system. For now that's the only purpose.

    **TODO**: Add specific bridge methods and attributes. Future work.
    """
    pass

class R2DRoadway(R2DComponent):
    """
    Subclass used to identify roadways in a system. For now that's the only purpose.

    **TODO**: Add specific roadway methods and attributes. Future work.
    """
    pass

class R2DTunnel(R2DComponent):
    """
    Subclass used to identify tunnels in a system. For now that's the only purpose.

    **TODO**: Add specific tunnel methods and attributes. Future work.
    """
    pass

class R2DPipe(R2DComponent):
    """
    Subclass used to simulate pipes in a system when using the R2D files as inputs.
    """

    def __init__(self) -> None:
        super().__init__()
        self.damage_information = {'Location': [], 'Type': []}
        self.general_information = {'Status': 'OPEN'}

    def update_r2d_dict(self) -> None:
        """
        Update the resource-to-damage dictionary based on the current damage level of the pipe.
        """
        super().update_r2d_dict()
        if self.functionality_level < 1.0:
            self.general_information['Status'] = 'CLOSED'
        elif self.functionality_level == 1.0:
            self.general_information['Status'] = 'OPEN'
            self.damage_information  = {'Location': [], 'Type': []}

class R2DBuilding(R2DComponent):
    """
    Class used to simulate buildings in a system when using the R2D files as inputs.
    """
    pass