from pyrecodes.component.component import Component
from pyrecodes.constants import RECOVERY_FINANCING_ACTIVITY_NAME, MONEY_RESOURCE_NAME

class RepairConfigurator():
    """
    | Class that configures repair parameters for components.
    | Repair parameters are repair duration and repair resource demand.

    | TODO: Create a more general class "RecoveryActivityConfigurator" that configures all recovery activities once it is needed. For now only repair is configured.
    """

    def __init__(self, component: Component, system_level_data: dict) -> None:
        self.component = component
        self.system_level_data = system_level_data

    def set_parameters(self, component_data: dict, component_DS: int, recovery_demand_setter: callable) -> None:
        self.set_repair_cost(component_data, recovery_demand_setter)
        self.set_repair_time(component_data)
        if len(self.component.recovery_model.recovery_activities['Repair'].demand) > 0:
            self.set_repair_demand(component_DS, recovery_demand_setter)

    def set_repair_cost(self, component_data: dict, recovery_demand_setter: callable) -> None:
        financing_activity = self.component.recovery_model.recovery_activities.get(RECOVERY_FINANCING_ACTIVITY_NAME, None)
        if financing_activity is not None:
            repair_cost = self.get_repair_cost(component_data)
            # TODO: Fix this line in the same way you fixed consumables in the pyrecodes_hospitals project. Consume money only once at the beginning of the financing activity.
            repair_cost_distributed_over_duration = repair_cost / self.component.recovery_model.recovery_activities[RECOVERY_FINANCING_ACTIVITY_NAME].duration
        else:
            repair_cost_distributed_over_duration = 0
        recovery_demand_setter(self.component, RECOVERY_FINANCING_ACTIVITY_NAME, MONEY_RESOURCE_NAME, repair_cost_distributed_over_duration)

    def get_repair_cost(self, component_data: dict) -> float:
        for resource in component_data['RecoveryModel']['Parameters'][RECOVERY_FINANCING_ACTIVITY_NAME]['Demand']:
            if resource['Resource'] == MONEY_RESOURCE_NAME:
                return resource['Amount']
        return 0
    
    def set_repair_time(self, component_data: dict) -> None:     
        """
        Set repair time for the component.
        
        Set when component is created based on info from component library. No need to change.

        Implement this method in the subclass, if necessary.
        """
        pass

    def set_repair_demand(self, component_DS: int, recovery_demand_setter: callable) -> None:
        """
        Set repair resource demand for the component.
        
        Set when component is created based on info from component library. No need to change. 
        
        Implement this method in the subclass, if necessary.
        """
        pass