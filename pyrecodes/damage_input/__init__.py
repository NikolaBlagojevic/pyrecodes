from pyrecodes.damage_input.list_damage_input import ListDamageInput

class FileDamageInput(ListDamageInput):

    def __init__(self, parameters):
        with open(parameters, 'r') as file:
            damage_input_str = file.read()
        damage_input = list(map(float, damage_input_str.replace('\n', '').split(',')))
        self.damage_levels = damage_input
