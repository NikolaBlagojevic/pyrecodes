from pyrecodes.subsystem_creator.subsystem_creator import SubsystemCreator
import copy

class JSONSubsystemCreator(SubsystemCreator):
    """
    Subsystem Creator where all components are explicitly specified in a JSON system configuration file.
    """

    def create_components_in_localities(self) -> None:
        components = []
        for component_type, amount in self.parameters.get('ComponentsInLocality', {}).items():
            component = self.get_component_object(component_type)
            self.component_configurator['Component'].set_parameters(component, [self.locality['LocalityName']])
            for _ in range(amount):
                components.append(copy.deepcopy(component))
        return components

    def create_components_between_localities(self) -> None:
        components = []
        for link_to, link_type_list in self.parameters.get('ComponentsBetweenLocalities', {}).items():
            for link_type in link_type_list:
                component = self.get_component_object(link_type)
                self.component_configurator['Component'].set_parameters(component, [self.locality['LocalityName'], link_to])
                components.append(component)
        return components
