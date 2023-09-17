"""
Module used to provide initial component damage information to the system class.

More details coming soon.
"""

from abc import ABC, abstractmethod
from pyrecodes import Component

class DamageInput(ABC):
    """
    Different methods for providing initial component damage information to the system class
    """

    @abstractmethod
    def get_initial_damage(self) -> None:
        pass

    @abstractmethod
    def set_initial_damage(self, components: list) -> None:
        pass

class ConcreteDamageInput(DamageInput):

    def __init__(self, parameters):
        self.parameters = parameters

    def get_initial_damage(self):
        pass

    def set_initial_damage(self, components: list([Component.Component])):
        self.get_initial_damage() 
        for damage_level, component in zip(self.damage_levels, components):
            component.set_initial_damage_level(damage_level)

class ListDamageInput(ConcreteDamageInput):

    def get_initial_damage(self):
        """
        self.parameters are set in the system class and contained in the system_creator.system_configuration
        """
        self.damage_levels = self.parameters

class R2DDamageInput(ConcreteDamageInput):
    DAMAGE_STATE_ID_POSITION_IN_COMPONENT_NAME = 2

    def get_initial_damage(self):
        pass

    def set_initial_damage(self, components: list([Component.Component])) -> None:
        for component in components:
            if self.component_is_damaged(component) or self.component_is_interface(component):
                component.set_initial_damage_level(1.0)

    def component_is_damaged(self, component: Component.Component) -> bool:
        damage_state = component.name[self.DAMAGE_STATE_ID_POSITION_IN_COMPONENT_NAME]
        if ('ResidentialBuilding' in component.name) and int(damage_state) > 0:
            return True
        else:
            return False
    
    def component_is_interface(self, component: Component.Component) -> bool:
        if isinstance(component, Component.InfrastructureInterface):
            return True
        else:
            return False

class FileDamageInput(ConcreteDamageInput):

    def get_initial_damage(self):
        with open(self.parameters, 'r') as file:
            damage_input_str = file.read()
        damage_input = list(map(float, damage_input_str.replace('\n', '').split(',')))
        self.damage_levels = damage_input
