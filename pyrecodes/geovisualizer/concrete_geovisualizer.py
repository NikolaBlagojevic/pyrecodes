from pyrecodes.component.component import Component
from pyrecodes.geovisualizer.component_state_colors import COMPONENT_STATE_COLORS
import time
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.cm as mcm
import imageio
import pandas as pd
import shapely
from pyrecodes.component.component import Component
from pyrecodes.plotter.concrete_plotter import ConcretePlotter
from pyrecodes.system.system import System
from pyrecodes.resilience_calculator.resilience_calculator import ResilienceCalculator


class ConcreteGeoVisualizer():
    """
    Class that visualizes recovery using geospatial data plots.
    """

    def __init__(self, components: list[Component]) -> None:
        self.set_components(components)
        self.set_component_state_dict()
        self.create_geodataframe()
        self.plotter = ConcretePlotter()

    def set_components(self, components: list[Component]) -> None:
        self.components = components  
    
    def set_component_state_dict(self) -> None:
        self.state_dict = {}
        states, colors = COMPONENT_STATE_COLORS.keys(), COMPONENT_STATE_COLORS.values()        
        for id, (state, color) in enumerate(zip(states, colors)):
            self.state_dict[state] = {'Color': color, 'ID': id} 
    
    def create_empty_dataframe(self) -> None:
        columns = ['ID', 'Footprint_WKT', 'State']
        return pd.DataFrame(columns=columns)
    
    def show_recovery_animation(self, max_time_step: int, pause=1):
        for time_step in range(max_time_step):
            self.create_current_state_figure(time_step)
            time.sleep(pause)
            plt.clf()
    
    def create_components_recovery_time_figure(self, recovery_time_resilience_calculator: ResilienceCalculator, 
                                               show=True, save=True, dpi=1000,
                                               savename='./components_recovery_time.png') -> None:
        components_color, cmap, norm = self.get_component_recovery_time_colors(recovery_time_resilience_calculator)
        fig, ax = plt.subplots(figsize=(8, 6))
        self.buildings_geodataframe.plot(color=components_color, ax=ax)
        ax.set_title(f'Components Recovery Time')
        ctx.add_basemap(ax, zoom="auto", crs=self.buildings_geodataframe.crs, source=ctx.providers.OpenStreetMap.Mapnik)
        ax.axis('tight')   
        ax.axis('off')   

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
        cbar.set_label('Recovery Time (days)') 

        if save:      
            plt.savefig(savename, dpi=dpi, bbox_inches='tight', transparent=True, pad_inches=0)  
        if show:
            plt.show()
    
    def get_component_recovery_time_colors(self, recovery_time_resilience_calculator) -> list[str]:
        components_recovery_time = list(recovery_time_resilience_calculator.component_recovery_times.values())   
        # remove infinite values and replace them with an integer max
        components_recovery_time = [recovery_time if recovery_time != float('inf') else -1 for recovery_time in components_recovery_time]
        max_recovery_time = max(components_recovery_time)
        components_recovery_time = [recovery_time if recovery_time != -1 else max_recovery_time for recovery_time in components_recovery_time]

        norm = mcolors.Normalize(vmin=min(components_recovery_time), vmax=max(components_recovery_time))
        cmap = mcm.get_cmap('OrRd')
        return [cmap(norm(recovery_time)) for recovery_time in components_recovery_time], cmap, norm
    
    def create_recovery_gif(self, time_steps: list[int], file_name='./2D_buildings_with_supply_demand_TIME_STEP.png', savename='./system_recovery.gif', fps=1) -> None:        
        frames = []
        for time_step in time_steps:           
            frame = imageio.v2.imread(file_name.replace('TIME_STEP', str(time_step)))
            frames.append(frame)
        imageio.mimwrite(savename, 
                frames,          
                fps = fps)         
    
    def create_current_state_buildings_and_supply_demand_figure(self, time_step: int, system: System, save=True, 
                                                                dpi=300, resources_to_plot=['Shelter', 'RepairCrew'],
                                                                units=['[beds/day]', '[crews/day]'],
                                                                show=False, supply_demand_resilience_calculator_id=0,
                                                                savename=f'2D_buildings_with_supply_demand_TIME_STEP.png') -> None:
        fig, ax_dict = plt.subplot_mosaic([['left', 'upper right'],
                               ['left', 'lower right']],
                              figsize=(24, 12), layout="constrained") 
           
        self.create_current_state_figure(time_step, ax=ax_dict['left'])
        x_axis_label = 'Time step [day]'
        for axis_name, resource_to_plot, unit in zip(['upper right', 'lower right'], resources_to_plot, units):
            y_axis_label = f'{resource_to_plot} {unit}'
            self.plotter.plot_single_resource(list(range(0, time_step+1)), system.resilience_calculators[supply_demand_resilience_calculator_id].system_supply[resource_to_plot][:time_step+1], 
                                        system.resilience_calculators[supply_demand_resilience_calculator_id].system_demand[resource_to_plot][:time_step+1], 
                                        system.resilience_calculators[supply_demand_resilience_calculator_id].system_consumption[resource_to_plot][:time_step+1], ax_dict[axis_name])
            ax_dict[axis_name].set_xlabel(x_axis_label)
            ax_dict[axis_name].set_ylabel(y_axis_label)
            ax_dict[axis_name].grid(True)      

        if show:
            plt.show()

        if save:
            plt.rcParams.update({'font.size': 18})   
            plt.savefig(savename.replace('TIME_STEP', str(time_step)), dpi=dpi, bbox_inches='tight', pad_inches=0)  
            plt.close()       
        
    
    def create_current_state_figure(self, time_step: int, ax=None, save=False, dpi=300):
        state_colors = self.update_buildings_dataframe_with_component_current_state(time_step)     
        if ax == None:   
            fig, ax = plt.subplots(figsize=(8, 6))
        self.buildings_geodataframe.plot(color=state_colors, ax=ax)
        self.create_component_state_legend(ax)
        ax.set_title(f'Time Step: {time_step}')
        minx, miny, maxx, maxy = self.buildings_geodataframe.total_bounds
        ax.set_xlim(minx*0.95, maxx*1.05)
        ax.set_ylim(miny*0.95, maxy*1.05)
        # Calculate width and height of the bounding box
        width = maxx - minx
        height = maxy - miny

        # Determine the larger of the two dimensions
        max_dim = max(width, height)

        # Adjust the bounds to make a square
        if width > height:
            # Expand height to match width
            mid_y = (miny + maxy) / 2
            miny = mid_y - max_dim / 2
            maxy = mid_y + max_dim / 2
        else:
            # Expand width to match height
            mid_x = (minx + maxx) / 2
            minx = mid_x - max_dim / 2
            maxx = mid_x + max_dim / 2

        # Set the new square extent
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)
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

    def create_geodataframe(self) -> None:
        """
        Creates a geodataframe with the buildings of the system. Implemented in subclasses.
        """
        self.buildings_geodataframe = self.create_empty_dataframe()

    def get_component_current_state(self, component: Component, time_step: int) -> int:        
        component_state = []
        for state in list(self.state_dict.keys())[1:]:
            if self.component_is_in_state(component, state, time_step):                
                component_state.append(state)   
        if self.component_is_waiting(component_state):            
            component_state.append('Waiting')  
        return component_state 

    def component_is_in_state(self, component: Component, state: str, time_step: int) -> bool:
        if state in component.recovery_model.recovery_activities and time_step in \
            component.recovery_model.recovery_activities[state].time_steps:
            return True
        elif state == 'Functional' and self.component_is_functional(component, time_step): 
            return True   
        else:
            return False 
    
    def component_is_functional(self, component: Component, time_step: int) -> bool:        
        return time_step in component.functional
    
    def component_is_waiting(self, component_state: list[int]):
        return len(component_state) == 0
    
    def create_component_state_legend(self, axis: plt.axis):
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
    
    def create_localities_figure(self, components_to_plot: list, number_of_localities: int, save=False, dpi=300):
        localities_colors = self.get_component_localities_color(components_to_plot, number_of_localities)     
        fig, ax = plt.subplots(figsize=(8, 6))        
        self.buildings_geodataframe.plot(color=localities_colors, ax=ax, legend=True)      
        ax.set_title('Component Localities')
        ctx.add_basemap(ax, zoom="auto", crs=self.buildings_geodataframe.crs, source=ctx.providers.OpenStreetMap.Mapnik)
        ax.axis('tight')   
        ax.axis('off')    
        if save:      
            plt.savefig(f'2D_buildings_Localities.png', dpi=dpi, bbox_inches='tight', transparent=True, pad_inches=0)  
    
    def get_component_localities_color(self, components_to_plot: list, number_of_localities: int) -> list[str]:
        component_localities_color = []
        cmap = mcm.get_cmap('seismic')
        for component in components_to_plot:
                component_localities_color.append(cmap(component.locality[0]/number_of_localities))
        return component_localities_color
    
    def plot_locality_polygons(self, ax, system_file: dict):
        for locality, locality_content in system_file["Content"].items():
            bounding_box = locality_content['Coordinates']['BoundingBox']
            # Create a method for creating polygons in system creator and use it here - DRY. Future work.
            locality_polygon = shapely.Polygon([(lat, long) for lat, long in 
                                zip(bounding_box['Latitude'], bounding_box['Longitude'])])
            x, y = locality_polygon.exterior.xy
            ax.plot(x, y)
