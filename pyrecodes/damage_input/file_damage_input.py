from pyrecodes.damage_input.list_damage_input import ListDamageInput

class FileDamageInput(ListDamageInput):
    """
    Class that reads the initial damage levels of components from a text file.
    """

    def __init__(self, parameters, system):
        self.system = system
        self.read_initial_damage_file(parameters)

    def read_initial_damage_file(self, parameters):
        with open(parameters, 'r') as file:
            damage_input_str = file.read()
        damage_input = list(map(float, damage_input_str.replace('\n', '').split(',')))
        self.damage_levels = damage_input