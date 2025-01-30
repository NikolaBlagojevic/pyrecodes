import matplotlib.pyplot as plt
import json
from pyrecodes.component.component import Component
from pyrecodes.system.system import System
from pyrecodes.resilience_calculator.recodes_calculator import ReCoDeSCalculator
from pyrecodes.constants import LOR_ALPHA, GANTT_BAR_DISTANCE, GANTT_BAR_WIDTH, ALL_RECOVERY_ACTIVITIES_COLORS

class ConcretePlotter():
    """
    | Class that plots resilience assessment results in two formats:
    | 1. The supply, demand, and consumption dynamics during recovery for a list of resources.
    | 2. A Gantt chart that shows the recovery activities for each component in the system.
    """

    def setup_lor_plot_fig(self, x_axis_label: str, y_axis_label: str) -> plt.axis:
        plt.figure()
        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.grid(True)
        return plt.gca()
    
    def get_supply_demand_consumption(self, system: System, resource_name: str, resilience_calculator_id=0) -> list[list]:
        """
        | Method returns a list of lists containing the supply, demand, and consumption dynamics during recovery for a list of resources.

        | Default values are set for the resilience calculator id. It is assumed that the first resilience calculator in system.resilience_calculators list is a recodes calculator with scope='All'. The user can specify a different resilience calculator id as long as it is a recodes calculator.
        """
        if isinstance(system.resilience_calculators[resilience_calculator_id], ReCoDeSCalculator):
            supply_demand_consumption = {'TimeStep': [], 'Supply': [], 'Demand': [], 'Consumption': []}
            supply_demand_consumption['TimeStep'] = list(range(system.START_TIME_STEP, system.time_step+1))
            supply_demand_consumption['Supply'] = system.resilience_calculators[resilience_calculator_id].system_supply[resource_name]
            supply_demand_consumption['Demand'] = system.resilience_calculators[resilience_calculator_id].system_demand[resource_name]
            supply_demand_consumption['Consumption'] = system.resilience_calculators[resilience_calculator_id].system_consumption[resource_name]
            return supply_demand_consumption
        else:
            raise ValueError('To get supply/demand/consumption, the resilience calculator must be a ReCoDeS calculator.')
        
    def plot_supply_demand_dynamics(self, system: System, resources: list[str], units: list[str], resilience_calculator_id=0, x_axis_label='Time step [day]'):
        """
        | Method plots regional supply, demand, and consumption dynamics during recovery for a list of resources.

        | Default values are set for:
        | - the resilience calculator id. It is assumed that the first resilience calculator in system.resilience_calculators list is a recodes calculator with scope='All'. The user can specify a different resilience calculator id as long as it is a recodes calculator.
        | - the x-axis label. It is assumed that the x-axis label is 'Time step [day]'.
        """
        for resource_name, unit in zip(resources, units):
            y_axis_label= f'{resource_name} {unit}'
            axis_object = self.setup_lor_plot_fig(x_axis_label, y_axis_label)
            # supply/demand/consumption information is in the ReCoDeS resilience calculator object, which is stored in the system object: system.resilience_calculators[0]
            supply_demand_consumption = self.get_supply_demand_consumption(system, resource_name, resilience_calculator_id)
            self.plot_single_resource(supply_demand_consumption['TimeStep'], supply_demand_consumption['Supply'],
                                                supply_demand_consumption['Demand'],
                                                supply_demand_consumption['Consumption'], axis_object)


    def plot_single_resource(self, time_steps: list, supply: list, demand: list, consumption: list,
                             axis_object: plt.axis, warmup=0, show=False, supply_label='Supply', demand_label='Demand',
                             consumption_label='Consumption') -> None:
        [supply, demand, consumption] = self.add_warmup(warmup, [supply, demand, consumption])
        axis_object.plot(time_steps, supply, label=supply_label)
        axis_object.plot(time_steps, demand, label=demand_label)
        axis_object.plot(time_steps, consumption, label=consumption_label)
        axis_object.fill_between(time_steps, demand, consumption,
                         label='LoR', alpha=LOR_ALPHA)
        axis_object.legend(loc='lower right')
        if show:
            plt.show()

    def save_current_figure(self, savename='Figure.png', dpi=300) -> None:        
        plt.gca()
        plt.savefig(savename, dpi=dpi)
    
    def add_warmup(self, warmup: int, lists_to_extend: list[list]) -> list[list]:
        extended_lists = []
        for list_to_extend in lists_to_extend:
            extended_lists.append([list_to_extend[0]] * warmup + list_to_extend)
        return extended_lists       

    def setup_gantt_chart_fig(self, x_axis_label) -> plt.axis:
        plt.figure()
        plt.xlabel(x_axis_label)
        axis_object = plt.gca()
        plt.grid(True)
        return axis_object

    def plot_gantt_chart(self, components: list[Component], x_axis_label='Time Step [day]') -> None:
        axis_object = self.setup_gantt_chart_fig(x_axis_label)
        recovery_activities_legend = []
        plotted_components = []
        component_row = 0
        for component in components:
            active_recovery_activities = self.plot_component_gantt_bar(component_row, component, axis_object)
            if len(active_recovery_activities) > 0:
                component_row += 1
                recovery_activities_legend += active_recovery_activities
                plotted_components.append(component)        
        self.set_gantt_chart_legend(recovery_activities_legend, axis_object)
        axis_object.set_yticks([(i) * GANTT_BAR_DISTANCE for i in range(len(plotted_components))])   
        axis_object.set_yticklabels([component.__str__() for component in plotted_components])
        plt.show()
    
    def set_gantt_chart_legend(self, recovery_activities_legend: list, axis_object: plt.axis) -> None:
        legend_labels = []
        legend_handles = []
        for recovery_activity_name in set(recovery_activities_legend):
            legend_labels.append(recovery_activity_name)
            legend_handles.append(plt.Rectangle((0, 0), 1, 1, fc=ALL_RECOVERY_ACTIVITIES_COLORS[recovery_activity_name]))
        axis_object.legend(legend_handles, legend_labels, loc='upper left', bbox_to_anchor=(1.02, 1.0))

    def get_component_recovery_progress(self, component: Component) -> dict:
        component_recovery_progress = {}
        active_recovery_activities = []
        for recovery_activity_name, recovery_activity_object in component.recovery_model.recovery_activities.items():
            duration = len(recovery_activity_object.time_steps)
            if duration > 0:                
                active_recovery_activities.append(recovery_activity_name)
                start = recovery_activity_object.time_steps[0]
                component_recovery_progress[recovery_activity_name] = {'Start': start, 'Duration': duration}
        return component_recovery_progress, active_recovery_activities

    def plot_component_gantt_bar(self, component_row: int, component: Component, axis_object: plt.axis) -> list:        
        component_recovery_progress, active_recovery_activities = self.get_component_recovery_progress(component)
        for recovery_activity_name, recovery_activity_progress in component_recovery_progress.items():
            Y_position = component_row * GANTT_BAR_DISTANCE - GANTT_BAR_WIDTH/2
            axis_object.broken_barh([(recovery_activity_progress['Start'], recovery_activity_progress['Duration'])], (Y_position, GANTT_BAR_WIDTH),
                                        facecolors=ALL_RECOVERY_ACTIVITIES_COLORS[recovery_activity_name],
                                        edgecolor="none")        
        return active_recovery_activities        
    
    def save_supply_demand_consumption(self, system, resource_names: list, resilience_calculator_id=0):
        for resource in resource_names:
            savename = f'{resource}_supply_demand_consumption.json'
            supply_demand_consumption = self.get_supply_demand_consumption(system, resource, resilience_calculator_id)
            with open(savename, mode="w") as file:
                json.dump(supply_demand_consumption, file) 

    def save_component_recovery_progress(self, components: list):
        for component in components:
            savename = f'{component.name}_Locality_{component.locality[0]}_ID_{getattr(component, "aim_id", "None")}_recovery_progress.json'
            component_recovery_progress, _ = self.get_component_recovery_progress(component)
            with open(savename, mode="w") as file:
                json.dump(component_recovery_progress, file)

            
        