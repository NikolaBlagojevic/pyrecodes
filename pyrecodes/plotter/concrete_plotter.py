import matplotlib.pyplot as plt
import matplotlib as mpl
import json
from pyrecodes.component.component import Component
from pyrecodes.component.r2d_component import R2DComponent
from pyrecodes.system.system import System
from pyrecodes.resilience_calculator.recodes_calculator import ReCoDeSCalculator
from pyrecodes.constants import ALL_RECOVERY_ACTIVITIES_LABELS, LOR_ALPHA, GANTT_BAR_DISTANCE, GANTT_BAR_WIDTH, ALL_RECOVERY_ACTIVITIES_COLORS, HOUSEHOLD_GANTT_CHART_COLORS

class ConcretePlotter():
    """
    | Class that plots resilience assessment results in two formats:
    | 1. The supply, demand, and consumption dynamics during recovery for a list of resources.
    | 2. A Gantt chart that shows the recovery activities for each component in the system.
    """

    def setup_lor_plot_fig(self, x_axis_label: str, y_axis_label: str) -> plt.axis:
        plt.style.use('seaborn-v0_8-whitegrid')
        mpl.rcParams.update({
            'font.size': 12,
            'axes.labelsize': 14,
            'axes.titlesize': 16,
            'figure.figsize': (10, 6),
            'lines.linewidth': 2,
            'axes.edgecolor': 'black',
            'axes.linewidth': 1,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'legend.frameon': True,
            'legend.facecolor': 'white',
            'legend.framealpha': 0.9
        })

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
                             consumption_label='Consumption', unmet_demand_label='Unmet Demand') -> None:
        [supply, demand, consumption] = self.add_warmup(warmup, [supply, demand, consumption])
        axis_object.plot(time_steps, supply, label=supply_label)
        axis_object.plot(time_steps, demand, label=demand_label)
        axis_object.plot(time_steps, consumption, label=consumption_label)
        axis_object.fill_between(time_steps, demand, consumption,
                         label=unmet_demand_label, alpha=LOR_ALPHA)
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

    def setup_gantt_chart_fig(self, x_axis_label, num_components: int, mode: str) -> plt.axis:
        height_per_component = {'stack': 0.3, 'parallel': 0.5, 'separate': 1.0}
        plt.figure(figsize=(10, max(3, num_components * height_per_component[mode])))
        plt.xlabel(x_axis_label)
        axis_object = plt.gca()
        plt.grid(True)
        return axis_object

    def plot_gantt_chart(self, components: list[Component], x_axis_label='Time Step [day]', mode='stack') -> None:
        axis_object = self.setup_gantt_chart_fig(x_axis_label, len(components), mode)
        recovery_activities_legend = []
        plotted_components = []
        component_row = 0
        for component in components:
            active_recovery_activities = self.plot_component_gantt_bar(component_row, component, axis_object, mode)
            if len(active_recovery_activities) > 0:
                component_row += 1
                recovery_activities_legend += active_recovery_activities
                plotted_components.append(component)
        self.set_gantt_chart_legend(recovery_activities_legend, axis_object)
        axis_object.set_yticks([(i) * GANTT_BAR_DISTANCE for i in range(len(plotted_components))])
        axis_object.set_yticklabels([component.__str__() for component in plotted_components])
        plt.show()
    
    def set_gantt_chart_legend(self, recovery_activities_legend: list, axis_object: plt.axis, legend_colors: dict = None) -> None:
        legend_labels = []
        legend_handles = []
        colors = legend_colors if legend_colors is not None else ALL_RECOVERY_ACTIVITIES_COLORS
        for recovery_activity_name in set(recovery_activities_legend):
            label = ALL_RECOVERY_ACTIVITIES_LABELS.get(recovery_activity_name, recovery_activity_name)
            legend_labels.append(label)
            legend_handles.append(plt.Rectangle((0, 0), 1, 1, fc=colors[recovery_activity_name]))
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

    def assign_activity_lanes(self, component_recovery_progress: dict, mode: str) -> tuple[dict, int]:
        """Assign each activity to a vertical lane for rendering.

        'stack'    – all activities share one lane (original behaviour, overlapping activities overwrite each other)
        'separate' – each activity gets its own lane regardless of overlap
        'parallel' – greedy assignment: a new lane is only opened when activities actually overlap
        """
        if mode == 'stack':
            return {name: 0 for name in component_recovery_progress}, 1
        if mode == 'separate':
            return {name: idx for idx, name in enumerate(component_recovery_progress)}, len(component_recovery_progress)
        # mode == 'parallel': greedy interval-graph colouring
        lanes = []  # each entry is the end time of the last activity assigned to that lane
        activity_lanes = {}
        for activity_name, activity_progress in component_recovery_progress.items():
            start = activity_progress['Start']
            end = start + activity_progress['Duration']
            assigned = False
            for lane_idx, lane_end in enumerate(lanes):
                if start >= lane_end:
                    lanes[lane_idx] = end
                    activity_lanes[activity_name] = lane_idx
                    assigned = True
                    break
            if not assigned:
                activity_lanes[activity_name] = len(lanes)
                lanes.append(end)
        return activity_lanes, max(len(lanes), 1)

    def plot_component_gantt_bar(self, component_row: int, component: Component, axis_object: plt.axis, mode: str = 'stack') -> list:
        component_recovery_progress, active_recovery_activities = self.get_component_recovery_progress(component)
        if not active_recovery_activities:
            return active_recovery_activities
        activity_lanes, num_lanes = self.assign_activity_lanes(component_recovery_progress, mode)
        sub_bar_height = GANTT_BAR_WIDTH / num_lanes
        for recovery_activity_name, recovery_activity_progress in component_recovery_progress.items():
            Y_position = component_row * GANTT_BAR_DISTANCE - GANTT_BAR_WIDTH/2 + activity_lanes[recovery_activity_name] * sub_bar_height
            axis_object.broken_barh([(recovery_activity_progress['Start'], recovery_activity_progress['Duration'])], (Y_position, sub_bar_height),
                                        facecolors=ALL_RECOVERY_ACTIVITIES_COLORS[recovery_activity_name],
                                        edgecolor="none")
        return active_recovery_activities        
    
    def save_supply_demand_consumption(self, system, resource_names: list, resilience_calculator_id=0):
        for resource in resource_names:
            savename = f'{resource}_supply_demand_consumption_{resilience_calculator_id}.json'
            supply_demand_consumption = self.get_supply_demand_consumption(system, resource, resilience_calculator_id)
            with open(savename, mode="w") as file:
                json.dump(supply_demand_consumption, file) 

    def save_component_recovery_progress(self, components: list):
        component_recovery_progress = {}
        for component in components:
            if isinstance(component, R2DComponent):
                if component.asset_type not in component_recovery_progress:
                    component_recovery_progress[component.asset_type] = {}
                if component.asset_subtype not in component_recovery_progress[component.asset_type]:
                    component_recovery_progress[component.asset_type][component.asset_subtype] = {}
                component_recovery_progress[component.asset_type][component.asset_subtype][component.aim_id], _ = self.get_component_recovery_progress(component)
        savename = f'R2D_component_recovery_progress.json'
        with open(savename, mode="w") as file:
            json.dump(component_recovery_progress, file)

    def plot_household_movement(self, components: list, axis_object: plt.axis) -> None:
        all_households = self.collect_all_households(components)
        locations = []
        household_ids = []
        for household_count, household in enumerate(all_households):
            household_ids.append(household.id)
            locations += self.plot_single_household_movement(household, household_count, axis_object)
        self.set_gantt_chart_legend(locations, axis_object, HOUSEHOLD_GANTT_CHART_COLORS)
        axis_object.set_yticks([household_count for household_count in range(len(household_ids))])
        axis_object.set_yticklabels([household_id for household_id in household_ids])
        plt.show()

    def plot_single_household_movement(self, household, household_count: int, axis_object: plt.axis, bar_width=0.5) -> list:
        locations = []
        for time_step, location in enumerate(household.staying_at):
            axis_object.broken_barh([(time_step, 1)], (household_count-bar_width*0.5, bar_width),
                                    facecolors=HOUSEHOLD_GANTT_CHART_COLORS[location],
                                    edgecolor="none")
            locations.append(location)
        return locations

    def collect_all_households(self, components: list) -> list:
        all_households = []
        for component in components:
            all_households += getattr(component, "households", [])
        return all_households

    def get_household_location_counts(self, components: list) -> dict:
        all_households = self.collect_all_households(components)
        if not all_households:
            return {}
        time_length = len(all_households[0].staying_at)
        counts = {loc: [0] * time_length for loc in HOUSEHOLD_GANTT_CHART_COLORS}
        for household in all_households:
            for time_step, location in enumerate(household.staying_at):
                if location in counts:
                    counts[location][time_step] += 1
        return counts

    def plot_household_location_over_time(self, components: list, x_axis_label='Time step [day]') -> None:
        counts = self.get_household_location_counts(components)
        if not counts:
            return
        time_steps = list(range(len(counts['Home'])))
        axis_object = self.setup_lor_plot_fig(x_axis_label, 'Number of households in different locations')
        layers = [('Home', 'At Home'), ('Friend', 'With Friend'), ('OutOfTown', 'Out of Town')]
        cividis = mpl.colormaps['cividis']
        colors = [cividis(i / (len(layers) - 1)) for i in range(len(layers))]
        bottoms = [0] * len(time_steps)
        for (key, label), color in zip(layers, colors):
            tops = [b + v for b, v in zip(bottoms, counts[key])]
            axis_object.fill_between(time_steps, bottoms, tops, label=label, alpha=0.5, color=color)
            bottoms = tops
        self.reorder_legend(['Out of Town', 'With Friend', 'At Home'], loc='lower right')
        plt.show()

    def reorder_legend(self, order: list, ax=None, **legend_kwargs) -> None:
        if ax is None:
            ax = plt.gca()
        handles, labels = ax.get_legend_handles_labels()
        pairs = dict(zip(labels, handles))
        ordered = [(pairs[l], l) for l in order if l in pairs]
        if ordered:
            ordered_handles, ordered_labels = zip(*ordered)
            ax.legend(ordered_handles, ordered_labels, **legend_kwargs)
        
    def get_met_demand_over_time(self, components: list, resource_name: str) -> list:
        met_demand_tracker = getattr(components[0], 'met_demand_tracker', None)
        if met_demand_tracker is None:
            return []
        time_length = len(met_demand_tracker)
        totals = [0.0] * time_length
        for component in components:
            last_value = 0.0
            for time_step, met_demand in enumerate(getattr(component, 'met_demand_tracker', [])):
                if resource_name in met_demand:
                    last_value = met_demand[resource_name]['PercentOfMetDemand']
                totals[time_step] += last_value
        return totals

    def plot_met_demand_over_time(self, components: list, resource_name: str, x_axis_label='Time step [day]') -> None:
        totals = self.get_met_demand_over_time(components, resource_name)
        if not totals:
            return
        time_steps = list(range(len(totals)))
        axis_object = self.setup_lor_plot_fig(x_axis_label, f'{resource_name} met demand')
        axis_object.fill_between(time_steps, 0, totals, alpha=0.5, label='Met demand')
        axis_object.legend(loc='lower right')
        plt.show()
