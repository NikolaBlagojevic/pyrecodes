# Copyright (c) 2024 The Regents of the University of California  # noqa: INP001
# Copyright (c) 2024 Leland Stanford Junior University
#
# This file is part of whale.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# You should have received a copy of the BSD 3-Clause License along with
# whale. If not, see <http://www.opensource.org/licenses/>.
#
# Contributors:
# Sina Naeimi

"""Provide Interface between REWET and PYReCoDes."""

import sys
import copy
import json
import random
from pathlib import Path

import pandas as pd
import rewet
import wntrfr
from rewet.api import API
from sklearn.cluster import KMeans

# Nikola: moved these constant into the class constructor
# TEMP_DIR = './'
# RESULT_DIR = './rewet_result'
# INPUT_FILE_DIR = './'


class REWETPyReCoDes:
    """Provide the wrapper for REWET API."""

    # Sina: Deleted this
    # Nikola
    # TEMP_DIR = './'
    # RESULT_DIR = './rewet_result'
    # INPUT_FILE_DIR = './'

    def __init__(self, state: dict, resource_name: str, inp_file_path: str, result_dir='./rewet_result', temp_dir='./'):
        self.wn = None
        self._clean_wn = None
        self.asset_information = {}
        self.building_coordinates = []
        self.demand_node_to_building = {}
        self.buildings = {}
        self.nodes = {}
        self.pipe_damage = None
        self.node_damage = None
        self.pump_damage = None
        self.tank_damage = None
        self.rewet = None
        self.damage_file_list = {}
        self.damage_state = {}
        self.hydraulic_time_step = 3600
        self.inp_file_path = inp_file_path
        self.result_dir = result_dir
        self.temp_dir = temp_dir

        # Nikola: added this attribute - needed to get demand from the state dict
        self.resource_name = resource_name

        # Sina
        # Nikola
        # self.set_path(result_dir, 'RESULT_DIR')
        # self.set_path(temp_dir, 'TEMP_DIR')

        # Nikola: moved methods from system state which are not related to setting damage to __init__
        self.read_inp_file(self.inp_file_path)
        self.set_asset_data(state)
        self.couple_buildings_to_demand_nodes(state)

        rewet_log_path = Path(self.result_dir) / "rewet_log.txt"
        if rewet_log_path.exists():
            rewet_log_path.unlink()
    # Sina
    # Nikola
    # def set_path(self, path, var_name):
        # setattr(self, var_name, path)

    def system_state(self, state, damage, damage_time=0):
        """
        Set the WDN system for PyReCoDes Interface.

        Parameters
        ----------
        state : dict
            The State of system which is defined in the R2DTool's system_det
            style.
        damage : dict
            The damage state in 2DTool's system_i style.
        Damage_time : int
            When initil damages happen in seconds.

        Returns
        -------
        None.

        """
        # read the inp file
        self.read_inp_file(self.inp_file_path)

        self.set_asset_data(state)

        # sets the damage state based on the initial damage (from pelicun)
        self.update_state_with_damages(damage, damage_time, state)

        # couple building to the demand nodes
        self.couple_buildings_to_demand_nodes(state)

    def system_performance(self, state, current_time, next_time):
        """
        Assess the system functionality.

        Parameters
        ----------
        state : dict.
            The _det file content.
        current_time : int
            Current time in seconds.
        next_time : int
            Next time in seconds.

        Returns
        -------
        building_satisfaction : dict
            The ratio of satiesfied water for each building.

        """

        self.wn = copy.deepcopy(self._clean_wn)
        # sets the damage state based on the current (change of the network)
        # and saves the current time
        self.save_damage(state, current_time)

        # prepare rewet inputs
        self.make_rewet_inputs(current_time, next_time)

        system_std_out = sys.stdout
        rewet_log_path = Path(self.result_dir) / "rewet_log.txt"

        with rewet_log_path.open('at') as log_file:
            sys.stdout = log_file
            # load REWET API interface
            self.rewet = API(self.input_file_path)

            # sets the new demand absed on the new percentage
            self.set_new_demand(state)

            # apply_damages
            # self.apply_damage()

            # run WDN performance evaluation
            self.run_performance(current_time, next_time)

            # Save REWET Result
            self.rewet.save_result()

            # Get result
            building_satisfaction = self.get_building_data_satisfaction(method='mean')
            self.building_satisfaction = building_satisfaction

        sys.stdout = system_std_out

        return building_satisfaction

    def read_inp_file(self, inp_file):
        """
        Read the inp file.

        Parameters
        ----------
        inp_file : str
            The path to the inp file.

        Returns
        -------
        None.

        """
        self.inp_file_path = Path(inp_file)
        self.inp_file_path = self.inp_file_path.resolve()

        if not self.inp_file_path.exists():
            raise ValueError(f'There inp file does not exists: {inp_file}')  # noqa: EM102, TRY003

        self.inp_file_path = str(self.inp_file_path)

        # Read the inp file and create the WDN object file
        self.wn = wntrfr.network.model.WaterNetworkModel(self.inp_file_path)
        self._clean_wn = copy.deepcopy(self.wn)

        for node_name, node in self.wn.junctions():
            node_demand_base_value = node.demand_timeseries_list[0].base_value
            if node_demand_base_value > 0:
                if node_name not in self.nodes:
                    self.nodes[node_name] = {}

                # Nikola: Can we get the demand straight from the buildings in the state dict, not from the inp file?
                self.nodes[node_name]['initial_demand'] = node_demand_base_value

                self.nodes[node_name]['coordinates'] = node.coordinates

    def set_asset_data(self, state):
        """
        Set the asset information from state file.

        Parameters
        ----------
        state : dict
            _det file.

        Raises
        ------
        ValueError
            Unexpecyed values exists in state file.

        Returns
        -------
        None.

        """
        # Sina: self.asset_information['WaterDistributionNetwork'] = state['WaterDistributionNetwork']

        for asset_type, asset_type_data in state.items():
            if asset_type not in self.asset_information:
                # check if asset_type exists in self.asset_information
                self.asset_information[asset_type] = {}
            for sub_asset_type, sub_asset_type_data in asset_type_data.items():
                # check if sub_asset_type exists in
                # self.asset_information[asset_type]
                if sub_asset_type not in self.asset_information[asset_type]:
                    self.asset_information[asset_type][sub_asset_type] = {}

                for element_key, element_data in sub_asset_type_data.items():
                    asset_id = element_data['GeneralInformation']['AIM_id']
                    if asset_id != element_key:
                        raise ValueError(  # noqa: TRY003
                            'The rationality behidd the workdflow'  # noqa: EM101
                            'is that oth aim-id and keys be the'
                            'same'
                        )

                    self.asset_information[asset_type][sub_asset_type][asset_id] = (
                        element_data['GeneralInformation']
                    )

        building_state = state['Buildings']['Building']

        for building_id, each_building in building_state.items():
            population = each_building['GeneralInformation']['Population']
            # Nikola: I added water demand here, so we can get it from the state dict and update node demand directly
            water_demand = self.get_building_demand(each_building)
            population_ratio = each_building.get('population_ratio', None)

            if population_ratio is not None:
                ratio = population_ratio
            else:
                ratio = 1
                building_state[building_id]['GeneralInformation']['PopulationRatio'] = 1

            cur_building = {}
            cur_building['initial_population_ratio'] = ratio
            cur_building['population_ratio'] = ratio
            cur_building['initial_population'] = population
            cur_building['population'] = population
            cur_building['initial_demand'] = water_demand

            self.buildings[building_id] = cur_building

    def get_building_demand(self, building):
        return building['GeneralInformation']['OperationDemand'].get(self.resource_name, 0) + building['GeneralInformation']['RecoveryDemand'].get(self.resource_name, 0)

    def update_state_with_damages(self, damage, damage_time, state):  # noqa: ARG002
        """
        Update the state dic with damages.

        Parameters
        ----------
        damage : dict
            _i file in dict form..
        damage_time : int
            Damaeg time.
        state : dict
            _det file.

        Raises
        ------
        ValueError
            Unexpected damage state in damage data.

        Returns
        -------
        None.

        """
        damage = damage['WaterDistributionNetwork']
        pipe_damage = damage.get('Pipe', [])

        for asset_id, damage_location in pipe_damage.items():
            damage_location_info = damage_location['Damage']

            aggregate_keys = [
                key for key in damage_location_info if 'aggregate-' in key
            ]

            segment_list = [(int(key_name.strip("aggregate-")), key_name)  for key_name in aggregate_keys]

            segment_list.sort()

            # aggregate_results = [damage_location_info[key] for key in aggregate_keys]

            segment_sizes = len(segment_list)
            segment_step = 1 / segment_sizes

            cur_pipe_damage_location_list = []
            cur_pipe_damage_location_type = []
            c = 0
            for segment_c in segment_list:
                seg_key = segment_c[1]
                damage_val = damage_location_info[seg_key]
                if damage_val > 0:
                    if damage_val == 1:
                        damage_type = 'leak'
                    elif damage_val == 2:  # noqa: PLR2004
                        damage_type = 'break'
                    else:
                        raise ValueError('The damage type must be either 1 or 2')  # noqa: EM101, TRY003
                else:
                    continue

                cur_loc = c * segment_step + segment_step / 2
                cur_pipe_damage_location_list.append(cur_loc)
                cur_pipe_damage_location_type.append(damage_type)
                c += 1

            wdn_state = state['WaterDistributionNetwork']
            pipe_state = wdn_state.get('Pipe')

            # Sina's response: it's a unexpect-behavior test to make sure that the file is
            # the way it is expected. It doesn't matter if it is created before
            # or not.

            # Nikola: "Damage" key is provided as default for the state dict from pyrecodes, but has empty lists for Location and Type keys so basically no Damage.
            # This throws ValueError here so I comment it out for now. Let's see how to handle this.
            # Not sure why it's important if damage already exists, we can overwrite it.
            # if 'Damage' in pipe_state[asset_id]:
            #     raise ValueError(f'Damage is already exist for Pipe ' f'{asset_id}')  # noqa: EM102, TRY003

            pipe_state[asset_id]['Damage'] = dict()  # noqa: C408
            pipe_state[asset_id]['Damage']['Location'] = (
                cur_pipe_damage_location_list
            )

            pipe_state[asset_id]['Damage']['Type'] = cur_pipe_damage_location_type

        # Nikola: I need the pipe damage state so I can update it during recovery
        # Functionality of a pipe should not be described by the damage but by an attribute in the general information of the pipe.
        # This is a workaround until that is implemented.
        # In addition this method only works for pipes, not for other water system components.
        return pipe_state

    def set_rewet_damage_from_state(self, state, damage_time):
        """
        Set REWET damafe data from state at each time step.

        Parameters
        ----------
        state : dict
            _det file in dict format.
        damage_time : int
            Current damage time.

        Raises
        ------
        ValueError
            Unexpected or abnormal data in state.

        Returns
        -------
        None.

        """
        state = state['WaterDistributionNetwork']
        pipe_damage = state.get('Pipe', [])

        damage_list = []
        for asset_id, pipe_info in pipe_damage.items():
            damage_location_info = pipe_info['Damage']
            damage_location_list = damage_location_info['Location']
            damage_type_list = damage_location_info['Type']

            if len(damage_location_list) != len(damage_type_list):
                raise ValueError('The size of types and locationis not the same.')  # noqa: EM101, TRY003

            segment_sizes = len(damage_location_list)

            pipe_id = self.asset_information['WaterDistributionNetwork']['Pipe'][
                asset_id
            ]['InpID']

            for c in range(segment_sizes):
                cur_loc = damage_location_list[c]
                damage_type = damage_type_list[c]

                damage_list.append(
                    {
                        'pipe_id': pipe_id,
                        'damage_loc': cur_loc,
                        'type': damage_type,
                        'Material': 'CI',
                    }
                )

        damage_list.reverse()
        self.pipe_damage = pd.Series(
            data=damage_list,
            index=[damage_time for val in damage_list],
            dtype='O',
        )

        self.node_damage = pd.Series(dtype='O')

        self.pump_damage = pd.Series(dtype='O')

        self.tank_damage = pd.Series(dtype='O')

        if damage_time in self.damage_state:
            raise ValueError(f'Time {damage_time} still exists in damage state.')  # noqa: EM102, TRY003

    def couple_buildings_to_demand_nodes(self, state):  # noqa: C901
        """
        Couple building to the demand nodes based on their coordinates.

        Parameters
        ----------
        state :dict
            State file content.

        Returns
        -------
        None.

        """
        building_state = state['Buildings']['Building']

        building_id_list = []
        for building_id, each_building in building_state.items():
            location = each_building['GeneralInformation']['location']
            coordinate = (location['latitude'], location['longitude'])
            building_id_list.append(building_id)

            self.building_coordinates.append(coordinate)

        demand_node_coordinate_list = [
            val['coordinates'] for key, val in self.nodes.items()
        ]

        demand_node_name_list = [key for key, val in self.nodes.items()]

        kmeans = KMeans(
            n_clusters=len(demand_node_coordinate_list),
            init=demand_node_coordinate_list,
            n_init=1,
            random_state=0,
        )

        kmeans.fit(self.building_coordinates)

        labels = kmeans.labels_
        labels = labels.tolist()

        for group_i in range(len(demand_node_coordinate_list)):
            node_name = demand_node_name_list[group_i]
            for building_l in range(len(labels)):
                cur_node_l = labels[building_l]
                if group_i == cur_node_l:
                    if node_name not in self.demand_node_to_building:
                        self.demand_node_to_building[node_name] = []

                    building_id = building_id_list[building_l]
                    self.demand_node_to_building[node_name].append(building_id)

        for node_name in self.demand_node_to_building:
            building_name_list = self.demand_node_to_building[node_name]
            population_list = [
                self.buildings[bldg_id]['initial_population']
                for bldg_id in building_name_list
            ]

            total_initial_population = sum(population_list)

            cur_node = self.nodes[node_name]
            # Nikola: I introduce here a new method to calculate water demand based on the 
            initial_node_demand = self.get_node_demand(building_name_list)
            # initial_node_demand = cur_node['initial_demand']

            if initial_node_demand == 0 and total_initial_population > 0:
                Warning(  # noqa: PLW0133
                    f"Initial demand for node {node_name} is 0."
                    f" Thus, the demand ratio in buildidng(s)"
                    f" {repr(building_name_list).strip('[').strip(']')}"
                    f" is naturally ineffective and their demand"
                    f" is not met."
                )

            if total_initial_population == 0:
                Warning(  # noqa: PLW0133
                    f"The population assigned to {node_name} is 0."
                    f" Thus, the demand ratio in buildidng(s)"
                    f" {repr(building_name_list).strip('[').strip(']')}"
                    f" is ignored."
                )

            # We assume that population in the State does not change in the
            # course of recovery. Thus, the population is initial population.
            #  For more clarity, we name the variable "initial_population".
            # It does not mean that there will be ffdifferent population in
            # the course of recovery
            self.nodes[node_name]['initial_population'] = total_initial_population

            self.nodes[node_name]['initial_node_demand'] = initial_node_demand

            # Nikola - why do we need this? It seems like a reverse calculation of the above code.
            # for bldg_id in building_name_list:
            #     pop = self.buildings[bldg_id]['initial_population']

            #     if total_initial_population != 0:
            #         cur_bldg_initial_demand = (
            #             pop / total_initial_population * initial_node_demand
            #         )
            #     else:
            #         cur_bldg_initial_demand = None

            #     self.buildings[bldg_id]['initial_demand'] = cur_bldg_initial_demand

    # Nikola: new method to get the demand of a node based on the buildings connected to it
    def get_node_demand(self, building_name_list):
        """
        Calculate the water demand of a node based on the buildings connected to it.

        Parameters
        ----------
        building_name_list : list
            List of building names connected to the node.

        Returns
        -------
        float
            The total water demand of the node.

        """
        demand = 0
        for building_name in building_name_list:
            demand += self.buildings[building_name]['initial_demand']
        return demand
    
    def save_damage(self, state, current_time):
        """
        Convert and save the dmaages that are set before.

        Parameters
        ----------
        damage : dict
            damage dict.
        current_time : int
            Current time.

        Returns
        -------
        None.

        """
        pipe_damage_file_name = 'temp_pipe_damage_file.pkl'
        node_damage_file_name = 'node_pipe_damage_file.pkl'
        tank_damage_file_name = 'tank_pipe_damage_file.pkl'
        pump_damage_file_name = 'pump_pipe_damage_file.pkl'

        pipe_path = Path(self.temp_dir) / pipe_damage_file_name
        node_path = Path(self.temp_dir) / node_damage_file_name
        tank_path = Path(self.temp_dir) / tank_damage_file_name
        pump_path = Path(self.temp_dir) / pump_damage_file_name
        list_path = Path(self.temp_dir) / 'list.xlsx'

        pipe_path = str(pipe_path)
        node_path = str(node_path)
        tank_path = str(tank_path)
        pump_path = str(pump_path)

        # self.damage_state[current_time] = damage
        self.set_rewet_damage_from_state(state, current_time)

        if current_time in self.damage_state:
            raise ValueError(  # noqa: TRY003
                f'The time {current_time} is already in ' f' damage state.'  # noqa: EM102
            )

        self.damage_state[current_time] = {
            'Pipe': self.pipe_damage,
            'Node': self.node_damage,
            'Pump': self.pump_damage,
            'Tank': self.tank_damage,
        }

        self.pipe_damage.to_pickle(pipe_path)
        self.node_damage.to_pickle(node_path)
        self.pump_damage.to_pickle(pump_path)
        self.tank_damage.to_pickle(tank_path)

        scn_postfix_list = random.choices(
            ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'L', 'M'], k=0
        )

        scn_postfix = ''
        for p in scn_postfix_list:
            scn_postfix += p

        self.damage_file_list['Scenario Name'] = 'SCN_' + scn_postfix
        self.damage_file_list['Pipe Damage'] = pipe_damage_file_name
        self.damage_file_list['Nodal Damage'] = node_damage_file_name
        self.damage_file_list['Pump Damage'] = tank_damage_file_name
        self.damage_file_list['Tank Damage'] = pump_damage_file_name
        self.damage_file_list['Probability'] = 1

        damage_file_list = pd.DataFrame.from_dict([self.damage_file_list])
        damage_file_list.to_excel(list_path)
        self.list_path = list_path

    def run_performance(self, current_time, next_time):
        """
        Run the performance model using a hydraic solver (REWET).

        Parameters
        ----------
        current_time : int
            Current time in day.
        next_time : int
            Mext time in day.

        Raises
        ------
        ValueError
            When the current or next time is given wrong.

        Returns
        -------
        building_demand : dict
            the result specifying the percentage of demand satisfied by each
            building.

        """
        if current_time > next_time:
            raise ValueError('Current tiime cannot be bigger than the next' 'time')  # noqa: EM101, TRY003
        if abs(next_time - current_time) % self.hydraulic_time_step != 0:
            raise ValueError(  # noqa: TRY003
                'next_time - current_time must be a factor of '  # noqa: EM101
                'the hydraulci time step.'
            )

        status = self.rewet.initiate(current_time=current_time, debug=True)
        if status != 0:
            raise ValueError(f'There is an error: {status}')  # noqa: EM102, TRY003

        self.rewet.apply_damage(current_time, 0.001)

        time_step = next_time - current_time
        status = self.rewet.run_hydraulic_simulation(time_step)
        if status != 0:
            raise ValueError(f'There is an error: {status}')  # noqa: EM102, TRY003

        return dict

    def make_rewet_inputs(self, current_time, next_time):
        """
        Create setting input for REWET.

        Parameters
        ----------
        current_time : int
            Current time in seconds.
        next_time : TYPE
            Next stop time in seconds.

        Raises
        ------
        ValueError
            Path are not available.

        Returns
        -------
        None.

        """
        settings = get_rewet_hydraulic_basic_setting()
        run_time = next_time - current_time
        list_file_path = Path(self.list_path)
        list_file_path = list_file_path.resolve()
        if not list_file_path.exists():
            raise ValueError(  # noqa: TRY003
                f'The list file does not exists: ' f'{list_file_path!s}'  # noqa: EM102
            )
        list_file_path = str(list_file_path)

        temp_dir = Path(self.temp_dir).resolve()
        if not temp_dir.exists():
            raise ValueError(f'The temp directory does not exists: ' f'{temp_dir!s}')  # noqa: EM102, TRY003
        temp_dir = str(temp_dir)

        settings['RUN_TIME'] = run_time
        settings['minimum_simulation_time'] = run_time
        settings['result_directory'] = self.result_dir
        settings['temp_directory'] = temp_dir
        settings['WN_INP'] = self.inp_file_path
        settings['pipe_damage_file_list'] = list_file_path
        settings['pipe_damage_file_directory'] = temp_dir
        settings['Restoration_on'] = False
        settings['Pipe_damage_input_method'] = 'pickle'

        input_file_path = Path(self.temp_dir) / 'rewet_input.json'
        input_file_path = input_file_path.resolve()
        with open(input_file_path, 'w') as f:  # noqa: PTH123
            json.dump(settings, f, indent=4)

        self.input_file_path = str(input_file_path)

    def get_building_data_satisfaction(self, method):
        """
        Get building water satiesfaction data.

        Parameters
        ----------
        method : str
            MEAB, MAX, or MIN.

        Raises
        ------
        ValueError
            Unrecognizable method is given.

        Returns
        -------
        building_demand_satisfaction_ratio : dict
            Building satiesfied ratio.

        """
        demand_sat = self.rewet.get_satisfied_demand_ratio()

        if method.upper() == 'MEAN':
            demand_sat = demand_sat.mean()
        elif method.upper() == 'MAX':
            demand_sat = demand_sat.max()
        elif method.upper() == 'MIN':
            demand_sat = demand_sat.min()
        else:
            raise ValueError(f'The method is not recognizable: {method}')  # noqa: EM102, TRY003

        building_demand_satisfaction_ratio = {}

        for node_name in self.demand_node_to_building:
            node_demand_ratio = demand_sat[node_name]
            building_names = self.demand_node_to_building[node_name]
            cur_satisified_demand_building = dict(
                zip(building_names, [node_demand_ratio] * len(building_names))
            )

            building_demand_satisfaction_ratio.update(cur_satisified_demand_building)

        return building_demand_satisfaction_ratio

    def set_new_demand(self, state):
        """
        Set new demand from state.

        Parameters
        ----------
        state : dict
            _det file in dict format.

        Returns
        -------
        None.

        """
        for node_name in self.demand_node_to_building:
            # cur_node = self.nodes[node_name]
            total_initial_population = self.nodes[node_name]['initial_population']

            if not total_initial_population > 0:
                continue

            building_name_list = self.demand_node_to_building[node_name]

            building = state['Buildings']['Building']

            node_new_demand = 0

            for bldg_id in building_name_list:
                # Nikola: We take the demand directly from the buidling general information, not based on population ratio.
                # cur_bldg_initial_demand = self.buildings[bldg_id]['initial_demand']

                # cur_bldg_deamnd_ratio = building[bldg_id]['GeneralInformation'][
                #     'PopulationRatio'
                # ]

                # cur_bldg_new_deamnd = cur_bldg_deamnd_ratio * cur_bldg_initial_demand
                cur_bldg_new_deamnd = self.get_building_demand(building[bldg_id])

                self.buildings[bldg_id]['current_demand'] = cur_bldg_new_deamnd

                node_new_demand += cur_bldg_new_deamnd

            self.nodes[node_name]['current_demand'] = node_new_demand
            node = self.wn.get_node(node_name)
            node.demand_timeseries_list[0].base_value = node_new_demand


def get_rewet_hydraulic_basic_setting():
    """
    Create basic settings for rewet's input.

    Returns
    -------
    settings_dict : dict
        REWET input.

    """
    settings = rewet.Input.Settings.Settings()
    settings_dict = settings.process.settings

    return settings_dict  # noqa: RET504