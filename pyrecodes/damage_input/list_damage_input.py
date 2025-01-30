from pyrecodes.damage_input.damage_input import DamageInput

class ListDamageInput(DamageInput):
    """
    Class that reads the initial damage levels of components from a list specified in the system configuration file.
    """

    def __init__(self, parameters, system):
        self.damage_levels = parameters
        self.system = system

    def set_initial_damage(self):
        for damage_level, component in zip(self.damage_levels, self.system.components):
            component.set_initial_damage_level(damage_level)