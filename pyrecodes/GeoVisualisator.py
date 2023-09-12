"""
Module used to visualize the system recovery process using geospatial tools.

More details coming soon.
"""

import time
import contextily as ctx
import geopandas
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.cm as mcm
import imageio
import pandas as pd
import shapely
from pyrecodes import Component
from pyrecodes import Plotter
from pyrecodes import System

COMPONENT_STATE_COLORS = {
    'Waiting': 'black',
    'RapidInspection': 'lightblue',
    'Financing': 'orange',
    'ContractorMobilization': 'springgreen',
    'SitePreparation': 'purple',
    'CleanUp': 'yellow',
    'DetailedInspection': 'tomato',
    'ArchAndEngDesign': 'pink',
    'Permitting': 'darkblue',
    'Demolition': 'gray',
    'Repair': 'red',
    'Functional': 'green'
}

class ConcreteGeoVisualisator():

    def __init__(self, components: list([Component.Component])) -> None:
        self.set_components(components)
        self.set_component_state_dict()
        self.create_buildings_geodataframe()
        self.plotter = Plotter.Plotter()

    def set_components(self, components: list([Component.Component])) -> None:
        self.components = components  
    
    def set_component_state_dict(self) -> None:
        self.state_dict = {}
        states, colors = COMPONENT_STATE_COLORS.keys(), COMPONENT_STATE_COLORS.values()        
        for id, (state, color) in enumerate(zip(states, colors)):
            self.state_dict[state] = {'Color': color, 'ID': id} 
    
    def create_empty_buildings_dataframe(self) -> None:
        columns = ['ID', 'Footprint_WKT', 'State']
        return pd.DataFrame(columns=columns)
    
    def show_recovery_animation(self, max_time_step: int, pause=1):
        for time_step in range(max_time_step):
            self.create_current_state_figure(time_step)
            time.sleep(pause)
            plt.clf()
        
    def create_recovery_gif(self, time_steps: list([int]), file_name='./2D_buildings_with_supply_demand_TIME_STEP.png', savename='./system_recovery.gif') -> None:        
        frames = []
        for time_step in time_steps:           
            frame = imageio.v2.imread(file_name.replace('TIME_STEP', str(time_step)))
            frames.append(frame)
        imageio.mimsave(savename, # output gif
                frames,          # array of input frames
                fps = 4)         # optional: frames per second
    
    def create_current_state_buildings_and_supply_demand_figure(self, time_step: int, system: System.System, save=True, 
                                                                dpi=300, resources_to_plot=['Shelter', 'RepairCrew'],
                                                                supply_demand_resilience_calculator_id=0,
                                                                savename=f'2D_buildings_with_supply_demand_TIME_STEP.png') -> None:
        fig, ax_dict = plt.subplot_mosaic([['left', 'upper right'],
                               ['left', 'lower right']],
                              figsize=(24, 12), layout="constrained") 
           
        self.create_current_state_figure(time_step, ax=ax_dict['left'])
        x_axis_label = 'Time step [day]'
        for axis_name, resource_to_plot in zip(['upper right', 'lower right'], resources_to_plot):
            y_axis_label = f'{resource_to_plot} Demand/Supply/Consumption'
            self.plotter.plot_single_resource(list(range(0, time_step+1)), system.resilience_calculators[supply_demand_resilience_calculator_id].system_supply[resource_to_plot][:time_step+1], 
                                        system.resilience_calculators[supply_demand_resilience_calculator_id].system_demand[resource_to_plot][:time_step+1], 
                                        system.resilience_calculators[supply_demand_resilience_calculator_id].system_consumption[resource_to_plot][:time_step+1], ax_dict[axis_name])
            ax_dict[axis_name].set_xlabel(x_axis_label)
            ax_dict[axis_name].set_ylabel(y_axis_label)
            ax_dict[axis_name].grid(True)      

        if save:
            plt.rcParams.update({'font.size': 18})   
            plt.savefig(savename.replace('TIME_STEP', str(time_step)), dpi=dpi, bbox_inches='tight', pad_inches=0)  
            plt.close()
    
    def create_current_state_figure(self, time_step: int, ax=None, save=False, dpi=300):
        state_colors = self.update_buildings_dataframe_with_component_current_state(time_step)     
        if ax == None:   
            fig, ax = plt.subplots(figsize=(8, 6))
        self.buildings_geodataframe.plot(color=state_colors, ax=ax)
        self.create_legend(ax)
        ax.set_title(f'Time Step: {time_step}')
        ctx.add_basemap(ax, zoom="auto", crs=self.buildings_geodataframe.crs, source=ctx.providers.OpenStreetMap.Mapnik)
        ax.axis('tight')   
        ax.axis('off')    
        if save:      
            plt.savefig(f'2D_buildings_{time_step}.png', dpi=dpi, bbox_inches='tight', transparent=True, pad_inches=0)  
    
    def create_current_state_shapefile(self, time_step: int, file_name='./Example 3/shapefiles/NorthEast_SF'):
        self.update_buildings_dataframe_with_component_current_state(time_step)
        self.buildings_geodataframe.to_file(f'{file_name}_Time_Step_{time_step}.shp', driver='ESRI Shapefile')

    def update_buildings_dataframe_with_component_current_state(self, time_step: int) -> list:
        state_colors = []
        for row_id, component_row in self.buildings_geodataframe.iterrows():
            component = self.components[component_row['ID']]
            component_current_state = self.get_component_current_state(component, time_step)
            state_colors.append(self.state_dict[component_current_state[0]]['Color'])
            self.buildings_geodataframe.at[row_id, 'State'] = component_current_state[0]
        return state_colors

    def create_buildings_geodataframe(self) -> None:
        """
        Creates a geodataframe with the buildings of the system. Implemented in subclasses.
        """
        self.buildings_geodataframe = self.create_empty_buildings_dataframe()

    def get_component_current_state(self, component: Component.Component, time_step: int) -> int:        
        component_state = []
        for state in list(self.state_dict.keys())[1:]:
            if self.component_is_in_state(component, state, time_step):                
                component_state.append(state)   
        if self.component_is_waiting(component_state):            
            component_state.append('Waiting')  
        return component_state 

    def component_is_in_state(self, component: Component.Component, state: str, time_step: int) -> bool:
        if state in component.recovery_model.recovery_activities and time_step in \
            component.recovery_model.recovery_activities[state].time_steps:
            return True
        elif state == 'Functional' and self.component_is_functional(component, time_step): 
            return True   
        else:
            return False 
    
    def component_is_functional(self, component: Component.Component, time_step: int) -> bool:        
        return time_step in component.functional
    
    def component_is_waiting(self, component_state: list([int])):
        return len(component_state) == 0
    
    def create_legend(self, axis: plt.axis):
        rectangles = []
        legend_names = []
        for state_name, state_info in self.state_dict.items():
            rectangles.append(mpatches.Rectangle((0, 0), 1, 1, fc=state_info['Color']))
            legend_names.append(state_name)
        axis.legend(rectangles, legend_names, loc='upper right', bbox_to_anchor=(1, 1), frameon=1, facecolor='white')
    
    def get_building_state_color_map(self) -> tuple:
        state_ids = [state['ID'] for state in self.state_dict.values()]   
        state_ids.append(max(state_ids)+1)
        state_colors = [state['Color'] for state in self.state_dict.values()]
        cmap = mcolors.ListedColormap(state_colors, state_ids)
        norm = mcolors.Normalize(vmin=min(state_ids), vmax=max(state_ids))
        return cmap, norm
    
    def create_localities_figure(self, components_to_plot: list, save=False, dpi=300):
        localities_colors = self.get_component_localities_color(components_to_plot)     
        fig, ax = plt.subplots(figsize=(8, 6))        
        self.buildings_geodataframe.plot(color=localities_colors, ax=ax)      
        ax.set_title('Component Localities')
        ctx.add_basemap(ax, zoom="auto", crs=self.buildings_geodataframe.crs, source=ctx.providers.OpenStreetMap.Mapnik)
        ax.axis('tight')   
        ax.axis('off')    
        if save:      
            plt.savefig(f'2D_buildings_Localities.png', dpi=dpi, bbox_inches='tight', transparent=True, pad_inches=0)  
    
    def get_component_localities_color(self, components_to_plot: list) -> list([str]):
        component_localities_color = []
        cmap = mcm.get_cmap('seismic')
        for component in components_to_plot:
                component_localities_color.append(cmap(component.locality[0]/5))
        return component_localities_color
    
    def plot_locality_polygons(self, ax, system_file: dict):
        for locality, locality_content in system_file["Content"].items():
            bounding_box = locality_content['Coordinates']['BoundingBox']
            # Create a method for creating polygons in system creator and use it here - DRY. Future work.
            locality_polygon = shapely.Polygon([(lat, long) for lat, long in 
                                zip(bounding_box['Latitude'], bounding_box['Longitude'])])
            x, y = locality_polygon.exterior.xy
            ax.plot(x, y)

class R2D_GeoVisualisator(ConcreteGeoVisualisator):

    def create_buildings_geodataframe(self) -> None:
        buildings_dataframe = self.create_empty_buildings_dataframe()
        for i, component in enumerate(self.components):
            if self.component_is_a_residential_building(component):
                building_polygon_WKT_format = self.get_building_polygon_in_WKT_format(component)                
                current_row = len(buildings_dataframe) + 1
                component_data_for_df = [i, building_polygon_WKT_format,
                                         'Functional']              
                buildings_dataframe.loc[current_row] = component_data_for_df

        geo_series = geopandas.GeoSeries.from_wkt(buildings_dataframe['Footprint_WKT'])
        geodataframe = geopandas.GeoDataFrame(buildings_dataframe, geometry=geo_series, crs="EPSG:4326")
        self.buildings_geodataframe = geodataframe.to_crs(epsg=3857)           

    def plot_component_localities(self):
        components_to_plot = []
        for component in self.components:
            if self.component_is_a_residential_building(component):
                components_to_plot.append(component)
        self.create_localities_figure(components_to_plot, save=True)

    @staticmethod
    def component_is_a_residential_building(component: Component.Component) -> bool:
        if 'ResidentialBuilding' in component.name:
            return True
        else:
            return False
    
    def get_building_polygon_in_WKT_format(self, component) -> str:
        if self.footprint_in_WKT_format(component.footprint):
            return component.footprint
        else:
            building_polygon_coordinates_as_list = [[str(coordinate_x) + ' ' + str(coordinate_y)][0] for
                                                    coordinate_x, coordinate_y in
                                                    component.footprint['geometry']['coordinates'][0]]
            building_polygons_as_one_string = ','.join(building_polygon_coordinates_as_list)
            building_polygon_WKT_format = 'POLYGON((' + building_polygons_as_one_string + '))'
            return building_polygon_WKT_format
    
    def footprint_in_WKT_format(self, footprint) -> bool:
        if 'POLYGON' in footprint:
            return True
        else:
            return False   
        