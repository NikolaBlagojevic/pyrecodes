from pyrecodes.subsystem_creator.subsystem_creator import SubsystemCreator
from pyrecodes.component.component import Component
from pyrecodes.utilities import read_json_file, create_locality_polygon, component_inside_bounding_box, create_component_geometry_as_point
from pyrecodes.component_configurator import r2d_component_configurator

class R2DSubsystemCreator(SubsystemCreator):
    """
    Create a System based on SimCenter R2D Tool's JSON output file.
    """

    def create_components_in_localities(self) -> list[Component]:
        return self.create_components()

    def set_component_configurator(self) -> None:
        for component_type in self.parameters['AssetTypes']:
            component_configurator_class = self.get_component_configurator(component_type)
            system_level_data = {key: self.constants.get(key, None) for key in component_configurator_class.SYSTEM_LEVEL_DATA}
            recovery_time_stepping = self.parameters.get('RecoveryTimeStepping', None)
            self.component_configurator[component_type] = component_configurator_class(system_level_data, recovery_time_stepping)

    def get_component_configurator(self, component_type: str):
        return getattr(r2d_component_configurator, f'R2D{component_type}Configurator')

    def create_components(self) -> list[Component]:
        info_json_file = read_json_file(self.parameters['R2DJSONFile_Info'])
        results_json_file = read_json_file(self.damage_input['Parameters']['DamageFile'])
        components = []
        subsystem_info = info_json_file[self.parameters['SubsystemNameInR2DJSON']]
        self.locality['ShapelyPolygon'] = create_locality_polygon(self.locality['Coordinates']['BoundingBox'])
        for asset_type in self.parameters['AssetTypes']:
            for component_id, component_info in subsystem_info[asset_type].items():
                component_location = self.get_component_geometry(component_info)
                if component_inside_bounding_box(component_location, self.locality['ShapelyPolygon']):
                    self._prepare_component_info(component_info)
                    damage_info = results_json_file[self.parameters['SubsystemNameInR2DJSON']][asset_type][component_id]
                    components += self.create_component(component_info, damage_info,
                                    self.parameters['SubsystemNameInR2DJSON'],
                                    asset_type)
                    self._after_component_created(components[-1])
                if len(components) >= self.parameters.get('MaxNumComponents', float('inf')):
                    break
        return components

    def _prepare_component_info(self, component_info: dict) -> None:
        """Hook called before creating each component. Override to modify component_info."""
        pass

    def _after_component_created(self, component: Component) -> None:
        """Hook called after each component is created. Override to collect component data."""
        pass

    def create_component(self, component_info: dict, damage_info: dict,
                         asset_type: str, asset_subtype: str) -> Component:
        """
        | Method to create a component.
        | It is assumed that the names of the components in the component library are in the format 'DS{damage_state}_{component_type}'
        | Component type is the same string as the asset subtype of the component in the R2D JSON file, e.g., 'Building', 'Bridge', etc.
        """
        component_type = asset_subtype
        component_damage_state = self.get_component_damage_state(damage_info, component_type)
        component_name = self.get_component_name(component_info, component_damage_state, component_type)
        component = self.get_component_object(component_name)
        component_data = {'Information': component_info, 'Loss': damage_info.get('Loss', {}), 'AssetType':asset_type,
                          'AssetSubtype': asset_subtype}
        component = self.component_configurator[component_type].set_parameters(component, [self.locality['LocalityName']], component_data, component_damage_state)
        return [component]

    def get_component_name(self, component_info: dict, component_damage_state: int, component_type: str) -> str:
        """Returns the component library name for the given component. Override to handle special component types."""
        if component_info['GeneralInformation'].get('OccupancyClass', '') == 'OutOfTown':
            return 'NeighboringTown'
        else:
            return f'DS{component_damage_state}_{component_type}'

    def get_component_geometry(self, component_info: dict) -> list:
        """
        | Method creates a shapely point representing component's geometry based on the information provided in the R2D location data.

        | TODO: Needs improvement for components whose geometry are lines (roads, pipes) and polygons. Future work.
        """
        return create_component_geometry_as_point([component_info['GeneralInformation']['location']['latitude'], component_info['GeneralInformation']['location']['longitude']])

    def get_component_damage_state(self, damage_info: dict, component_type: str) -> int:
        return self.component_configurator[component_type].get_damage_state(damage_info)


class R2DSubsystemCreatorWithHouseholds(R2DSubsystemCreator):
    """
    Extends R2DSubsystemCreator to support buildings with households.
    Tracks household counts and handles OutOfTown components.
    """

    def get_component_configurator(self, component_type: str):
        if component_type == 'Building':
            return getattr(r2d_component_configurator, 'R2DBuildingWithHouseholdsConfigurator')
        return super().get_component_configurator(component_type)

    def get_component_name(self, component_info: dict, component_damage_state: int, component_type: str) -> str:
        if component_info['GeneralInformation'].get('OccupancyClass', '') == 'OutOfTown':
            return 'NeighboringTown'
        return super().get_component_name(component_info, component_damage_state, component_type)

    def create_components(self) -> list[Component]:
        self.households = []
        return super().create_components()

    def _prepare_component_info(self, component_info: dict) -> None:
        if len(self.households) > self.parameters.get('MaxNumHouseholds', float('inf')):
            component_info['GeneralInformation']['Households'] = []

    def _after_component_created(self, component: Component) -> None:
        self.households += getattr(component, 'households', [])
