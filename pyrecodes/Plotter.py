"""
Module used to plot the results of the resilience assessment.

More details coming soon.
"""

import matplotlib.pyplot as plt
from pyrecodes import Component

# CONSTANTS
GANTT_BAR_DISTANCE = 10
GANTT_BAR_WIDTH = 5
LOR_ALPHA = 0.2
ALL_RECOVERY_ACTIVITIES_COLORS = {'RapidInspection': 'lightblue',
                                    'Financing': 'orange',
                                    'ContractorMobilization': 'springgreen',
                                    'SitePreparation': 'purple',
                                    'CleanUp': 'yellow',
                                    'DetailedInspection': 'tomato',
                                    'ArchAndEngDesign': 'pink',
                                    'Permitting': 'darkblue',
                                    'Demolition': 'gray',
                                    'Repair': 'red',
                                    'Functional': 'green'}

class Plotter():

    def setup_lor_plot_fig(self, x_axis_label: str, y_axis_label: str) -> plt.axis:
        plt.figure()
        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.grid(True)
        return plt.gca()

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
    
    def add_warmup(self, warmup: int, lists_to_extend: list([list])) -> list([list]):
        extended_lists = []
        for list_to_extend in lists_to_extend:
            extended_lists.append([list_to_extend[0]] * warmup + list_to_extend)
        return extended_lists       

    def setup_gantt_chart_fig(self, x_axis_label: str, components: list) -> plt.axis:
        plt.figure()
        plt.xlabel(x_axis_label)
        axis_object = plt.gca()
        plt.grid(True)
        return axis_object

    def plot_gantt_chart(self, components: list([Component.Component]), axis_object: plt.axis) -> None:
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

    def plot_component_gantt_bar(self, component_row: int, component: Component.Component, axis_object: plt.axis) -> list:
        active_recovery_activities = []
        for recovery_activity_name, recovery_activity_object in component.recovery_model.recovery_activities.items():
            duration = len(recovery_activity_object.time_steps)
            if duration > 0:
                Y_position = component_row * GANTT_BAR_DISTANCE - GANTT_BAR_WIDTH/2
                active_recovery_activities.append(recovery_activity_name)
                start = recovery_activity_object.time_steps[0]
                axis_object.broken_barh([(start, duration)], (Y_position, GANTT_BAR_WIDTH),
                                        facecolors=ALL_RECOVERY_ACTIVITIES_COLORS[recovery_activity_name],
                                        edgecolor="none")
        return active_recovery_activities