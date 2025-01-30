from pyrecodes.component.component import Component
from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
import copy

class SubsystemCreator():
    """
    Create a Subsystem within the System class.
    """

    def __init__(self, component_library: dict, locality: dict, parameters: dict, constants={}, damage_input={}) -> None:
        self.locality = locality
        self.parameters = parameters
        self.component_library = component_library
        self.constants = constants
        self.damage_input = damage_input
        self.components = []
        self.component_configurator = dict()
        self.set_component_configurator()
    
    def set_component_configurator(self) -> None:
        system_level_data = {key: self.constants.get(key, None) for key in ComponentConfigurator.SYSTEM_LEVEL_DATA}
        recovery_time_stepping = self.parameters.get('RecoveryTimeStepping', None)
        self.component_configurator['Component'] = ComponentConfigurator(system_level_data, recovery_time_stepping)
    
    def get_component_object(self, component_type: str) -> Component:
        component_template = copy.deepcopy(self.component_library[component_type])
        component = self.sample_random_variables_for_component(component_template)
        return component
    
    def sample_random_variables_for_component(self, component: Component) -> Component:
        """
        Resample all random variables in the component template to ensure they differ between components.

        At the moment, only random variables that are considered are the duration of recovery activities.

        TODO: Extend this method to sample other random variables. Find a generic way of finding random variables of a component.        
        """
        for recovery_activity, recovery_activity_parameters in component.recovery_model.parameters.items():
            component.recovery_model.recovery_activities[recovery_activity].set_duration(recovery_activity_parameters.get('Duration', ''))
        return component
    
    def create_components_in_localities(self) -> None:
        """
        Implement this method in subclasses if needed.
        """
        return []

    def create_components_between_localities(self) -> None:
        """
        Implement this method in subclasses if needed.
        """
        return []
