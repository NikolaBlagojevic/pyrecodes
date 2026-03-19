from pyrecodes.geovisualizer.r2d_geovisualizer import R2DGeoVisualizer
from pyrecodes.constants import HOUSEHOLD_OCCUPANCY_COLORS

class HouseholdGeoVisualizer(R2DGeoVisualizer):

    def get_household_populated_colors(self, time_step: int):
        """
        Returns a list of colors for household population visualization.
        """
        state_colors = []
        for row_id, component_row in self.buildings_geodataframe.iterrows():
            component = self.components[component_row['ID']]
            if hasattr(component, 'occupied_or_vacant') and component.occupied_or_vacant[0] == 'Occupied':
                occupancy_status = component.occupied_or_vacant[time_step]
                state_colors.append(HOUSEHOLD_OCCUPANCY_COLORS[occupancy_status])
            else:
                state_colors.append('white')
        return state_colors

    def create_household_state_figure(self, time_step: int, save=False, dpi=300):
        state_colors = self.get_household_populated_colors(time_step)
        self.create_current_state_figure('Households at home', state_colors, HOUSEHOLD_OCCUPANCY_COLORS, save=save, dpi=dpi)
