from pyrecodes.subsystem_creator.subsystem_creator import SubsystemCreator
from pyrecodes.component.component import Component

class RecoveryResourceSuppliersCreator(SubsystemCreator):
    """
    Class to create recovery resource supplier components.
    """

    def create_components_in_localities(self) -> list[Component]:     
        return self.create_recovery_resource_suppliers()
        
    def create_recovery_resource_suppliers(self) -> list[Component]:    
        suppliers = []
        for component_name in self.parameters['ComponentName']:
            component_template = self.get_component_object(component_name)
            component = self.component_configurator['Component'].set_parameters(component_template, [self.locality['LocalityName']], component_data={}, component_damage_state=0)
            suppliers.append(component)
        return suppliers