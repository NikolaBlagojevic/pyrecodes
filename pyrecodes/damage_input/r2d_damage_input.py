from pyrecodes.damage_input.damage_input import DamageInput
from pyrecodes.utilities import read_json_file
from pyrecodes.component.r2d_component import R2DPipe
from pyrecodes.component.infrastructure_interface import InfrastructureInterface
from pyrecodes.component_recovery_model.no_recovery_activity_model import NoRecoveryActivityModel
from pyrecodes.component.component import Component
from pyrecodes.component.r2d_component import R2DComponent

class R2DDamageInput(DamageInput):
    """
    Class that sets the initial damage of components from an R2D output file.
    """

    DAMAGE_STATE_ID_POSITION_IN_COMPONENT_NAME = 2

    def __init__(self, parameters, system):
        self.parameters = parameters
        self.system = system

    def set_initial_damage(self) -> None:
        """
        Method sets the initial damage of components and third-party infrastructure simulators.
        """        
        self.set_damage_in_the_distribution_model()
        self.set_initial_component_damage_level()

    def set_initial_component_damage_level(self) -> None:
        """
        | Method sets the initial damage of components. 
        | Component damage state is defined when components are constructed, since components in different damage states have different component templates in the component library when using R2D outputs.
        | Initial damage level of 1 is set for all components that are damaged (i.e., damage state above 0) or are infrastructure interfaces, since those components have predefined supply/demand dynamics triggered once the initial damage is set. 
        """
        for component in self.system.components:
            if self.component_is_damaged(component) or self.component_is_interface(component):
                component.set_initial_damage_level(1.0)

    def set_damage_in_the_distribution_model(self) -> None:
        """
        | Method that provides initial damage information to third-party infrastructure simulators through the API.
        | **TODO**: Generalize this method to other infrastructure systems. At the moment, it is specific to the water system defined in REWET.
        """
        for resource_name in self.parameters.get("DistributionModelDamage", []):
            distribution_model = self.system.resources[resource_name]['DistributionModel'] 
            r2d_state = distribution_model.r2d_dict
            r2d_damage = self.configure_damage_file(r2d_state)  
            state_with_damage = distribution_model.flow_simulator.update_state_with_damages(r2d_damage, damage_time=0, state=r2d_state)
            self.set_water_system_component_damage_information(state_with_damage)

    def configure_damage_file(self, r2d_dict) -> dict:
        """
        Method that configures the damage file to only take components which are considered in pyrecodes model. Some components might be in the R2D damage file but not considered in the pyrecodes model.
        """
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
        """
        | Method that checks if the component is damaged.
        | Note that the R2D Damage Input only assigns damage to R2D components.
        """        
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