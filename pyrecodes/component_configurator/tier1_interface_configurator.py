from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
from pyrecodes.component.component import Component

class Tier1InterfaceConfigurator(ComponentConfigurator):
    """
    Class that configures a Tier 1 or Tier 2 infrastructure interface component based on the infrastructure performance parameters provided in the system configuration file.
    """

    def set_parameters(self, component: Component, locality: dict, interface_parameters: dict) -> Component:
        super().set_parameters(component, locality)
        self.set_infrastructure_system_parameters(component, interface_parameters)
        return component

    def set_infrastructure_system_parameters(self, component: Component, interface_parameters: dict) -> None:
        component.set_supply_dynamics(interface_parameters)   
        if 'Demand' in interface_parameters:
            self.set_component_operation_demand(component, interface_parameters['Demand']['Resource'], interface_parameters['Demand']['Amount'])