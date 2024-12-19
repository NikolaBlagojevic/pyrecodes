from pyrecodes.damage_input.damage_input import DamageInput
from pyrecodes.utilities import read_json_file
from pyrecodes.component.r2d_component import R2DPipe
from pyrecodes.component.infrastructure_interface import InfrastructureInterface
from pyrecodes.component_recovery_model.no_recovery_activity_model import NoRecoveryActivityModel
from pyrecodes.component.component import Component
from pyrecodes.component.r2d_component import R2DComponent

class R2DDamageInput(DamageInput):
    DAMAGE_STATE_ID_POSITION_IN_COMPONENT_NAME = 2

    def __init__(self, parameters, system):
        self.parameters = parameters
        self.system = system

    def set_initial_damage(self) -> None:
        self.set_damage_in_the_distribution_model()
        self.set_initial_component_damage_level()

    def set_initial_component_damage_level(self) -> None:
        for component in self.system.components:
            if self.component_is_damaged(component) and not(self.component_is_interface(component)):
                component.set_initial_damage_level(1.0)

    def set_damage_in_the_distribution_model(self) -> None:
        for resource_name in self.parameters["DistributionModelDamage"]:
            distribution_model = self.system.resources[resource_name]['DistributionModel'] 
            r2d_state = distribution_model.r2d_dict
            r2d_damage = self.configure_damage_file(r2d_state)  
            # TODO: Check if this can be done in a better way. 
            # Problem is I need to call the flow simulator here so it modifies the damage of the components specified in the R2D file.
            # Why not have that done in the R2D file itself?
            state_with_damage = distribution_model.flow_simulator.update_state_with_damages(r2d_damage, damage_time=0, state=r2d_state)
            # TODO: Generalize this method to other infrastructure systems.
            self.set_water_system_component_damage_information(state_with_damage)

    def configure_damage_file(self, r2d_dict) -> dict:
        # Configure the damage file to only take components which are in the state dict.
        # It can happen that some components are out of the state dict but are in the damage file.
        # This is due to the localities constraining the location of components included in the state dict.
        r2d_damage = read_json_file(self.parameters['DamageFile'])
        configured_r2d_damage = {}
        for asset_type, asset_values in r2d_dict.items():
            configured_r2d_damage[asset_type] = {}
            for asset_subtype in asset_values.keys():
                configured_r2d_damage[asset_type][asset_subtype] = {key: value for key, value in r2d_damage[asset_type][asset_subtype].items() if key in r2d_dict[asset_type][asset_subtype]}
        return configured_r2d_damage
    
    def set_water_system_component_damage_information(self, pipe_damage: dict) -> None:
        for component in self.system.components:
            if isinstance(component, R2DPipe):
                component.damage_information = pipe_damage[component.aim_id]['Damage']

    def component_is_damaged(self, component: Component) -> bool:
        # R2D Damage Input only assigns damage to R2D components.
        if issubclass(type(component), R2DComponent):
            if isinstance(component.recovery_model, NoRecoveryActivityModel):
                return False
            else:
                return True
        else:
            return False
    
    def component_is_interface(self, component: Component) -> bool:
        if isinstance(component, InfrastructureInterface):
            return True
        else:
            return False