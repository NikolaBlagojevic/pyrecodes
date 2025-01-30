from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand
from pyrecodes.utilities import format_locality_id
from pyrecodes.component_configurator.repair_configurator import RepairConfigurator

class ComponentConfigurator():    
    """
    Class that reads, modifies and sets component parameters unique to each component, different than the default parameters defined in component library, and defined during system creation.
    """

    SYSTEM_LEVEL_DATA = ['START_TIME_STEP', 'MAX_TIME_STEP']

    def __init__(self, system_level_data: dict, recovery_time_stepping: list) -> None:
        self.system_level_data = system_level_data
        self.set_recovery_time_stepping_rules(recovery_time_stepping)
    
    def set_parameters(self, component: Component, locality_strings: list, component_data={}, component_damage_state=0) -> Component:
        """
        Set component parameters not defined in the component library.
        """
        self.set_locality(component, locality_strings)
        self.set_recovery_time_steps(component)
        self.configure_recovery_model(component, component_data, component_damage_state)
        return component
    
    def set_locality(self, component: Component, locality_strings: list) -> None:
        component.set_locality([format_locality_id(locality_string) for locality_string in locality_strings])
    
    def set_recovery_time_steps(self, component: Component) -> None:
        """
        Set recovery time stepping rules for the component. These define at which time steps component's recovery will be simulated and thus reduce the computational cost.
        """
        component.set_recovery_time_steps(self.recovery_time_steps)

    def configure_recovery_model(self, component: Component, component_data: dict, component_damage_state: int) -> None:
        """
        Configure recovery model for the component by configuring the parameters of the recovery activities.
        TODO: Create a more general class "RecoveryActivityConfigurator" that configures all recovery activities once it is needed. For now only repair is configured.
        """
        if component_data and 'Repair' in component.recovery_model.recovery_activities.keys():
            self.set_repair_configurator(component)
            self.set_repair_parameters(component_data, component_damage_state) 
    
    def set_recovery_time_stepping_rules(self, recovery_time_stepping: list):
        """
        Set recovery time stepping rules for the component. If None, the component will be recovered at each time step.
        """
        if recovery_time_stepping is None:
            self.recovery_time_steps = list(range(self.system_level_data['START_TIME_STEP'], self.system_level_data['MAX_TIME_STEP']))
        else: 
            self.recovery_time_steps = []
            for time_stepping in recovery_time_stepping:
                self.recovery_time_steps += list(range(time_stepping['start'], time_stepping['end'], time_stepping['step']))    

    def set_repair_configurator(self, component: Component) -> None:
        self.repair_configurator = RepairConfigurator(component, self.system_level_data)        

    def set_repair_parameters(self, component_data: dict, component_damage_state: int) -> None:
        """
        Set repair parameters (duration and resource demand) for the component.
        """
        self.repair_configurator.set_parameters(component_data, component_damage_state, self.set_component_recovery_demand)

    def set_component_supply(self, component: Component, resource_name: str, 
                             resource_supply_amount: float, 
                             resource_supply_type=StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value) -> None:        
        component_supply = getattr(component, SupplyOrDemand.SUPPLY.value)[resource_supply_type]
        component_supply[resource_name].set_initial_amount(resource_supply_amount)

    def set_component_operation_demand(self, component: Component, resource_name: str, 
                             resource_demand_amount: float) -> None: 
        component_demand = getattr(component, SupplyOrDemand.DEMAND.value)[
                            StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]
        component_demand[resource_name].set_initial_amount(resource_demand_amount)

    @staticmethod
    def set_component_recovery_demand(component: Component, recovery_activity_name: str, 
                                      resource_name: str, resource_amount: float):
        if recovery_activity_name in component.recovery_model.recovery_activities.keys():
            component.recovery_model.recovery_activities[recovery_activity_name].demand[resource_name].set_initial_amount(
                resource_amount)