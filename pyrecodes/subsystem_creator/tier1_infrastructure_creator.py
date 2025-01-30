from pyrecodes.subsystem_creator.subsystem_creator import SubsystemCreator
from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
from pyrecodes.component_configurator.tier1_interface_configurator import Tier1InterfaceConfigurator
from pyrecodes.component.component import Component

class Tier1InfrastructureCreator(SubsystemCreator):
    """
    Class to create Tier 1 or Tier 2 infrastructure interface components.
    """

    def set_component_configurator(self) -> None:
        system_level_data = {key: self.constants.get(key, None) for key in ComponentConfigurator.SYSTEM_LEVEL_DATA}
        recovery_time_stepping = self.parameters.get('RecoveryTimeStepping', None)
        self.component_configurator['Component'] = Tier1InterfaceConfigurator(system_level_data, recovery_time_stepping)
    
    def create_components_in_localities(self) -> list[Component]:
        return self.create_infrastructure_service_supplier()
        
    def create_infrastructure_service_supplier(self) -> list[Component]:
        components = []
        for component_name in self.parameters['ComponentName']:
            component_template = self.get_component_object(component_name)
            component = self.component_configurator['Component'].set_parameters(component_template, [self.locality['LocalityName']], self.parameters)
            components.append(component)
        return components