"""Methods for performance simulations of transportation networks."""  # noqa: INP001

# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 The Regents of the University of California
#
# This file is part of SimCenter Backend Applications.
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
# BRAILS. If not, see <http://www.opensource.org/licenses/>.
#
# Contributors:
# Barbaros Cetiner
# Tianyu Han
#
# Last updated:
# 08-14-2024

from __future__ import annotations  # noqa: I001

import gc
import os
import json
import logging
import sys
import time
import copy
import importlib
import math
from collections import defaultdict
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Set, Tuple, Dict, Literal, Union, Optional
from shapely.geometry import LineString, Polygon, Point, mapping
from shapely.ops import split
from sklearn.metrics.pairwise import cosine_similarity

import geopandas as gpd
import numpy as np
import pandana.network as pdna
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cdist
from shapely.wkt import loads
import warnings
# from brails.utils.geoTools import haversine_dist
# from brails.workflow.TransportationElementHandler import (
#     ROADLANES_MAP,
#     ROADSPEED_MAP,
#     calculate_road_capacity,
# )

## The below functions are mannually copied from brails to avoid importing brails

ROADLANES_MAP = {'S1100': 4, "S1200": 2, "S1400": 1, "S1500": 1, "S1630": 1,
                 "S1640": 1, "S1710": 1, "S1720": 1, "S1730": 1, "S1740": 1,
                 "S1750": 1, "S1780": 1, "S1810": 1, "S1820": 1, "S1830": 1}

ROADSPEED_MAP = {'S1100': 70, "S1200": 55, "S1400": 25, "S1500": 25,
                 "S1630": 25, "S1640": 25, "S1710": 25, "S1720": 25,
                 "S1730": 25, "S1740": 10, "S1750": 10, "S1780": 10,
                 "S1810": 10, "S1820": 10, "S1830": 10}

METER_PER_SECOND_TO_MILES_PER_HOUR = 2.23694
def calculate_road_capacity(nlanes: int,
                            traffic_volume_per_lane: int = 1800
                            ) -> int:
    """
    Calculate road capacity from number of lanes & traffic volume/lane.

    Parameters__
    nlanes (int): The number of lanes on the road.
    traffic_volume_per_lane (int, optional): The traffic volume
        capacity per lane. Default is 1800 vehicles.

    Returns__
    int: The total road capacity, which is the product of the number
        of lanes and the traffic volume per lane.
    """
    return nlanes * traffic_volume_per_lane

class TransportationPerformance(ABC):  # noqa: B024
    """
    An abstract base class for simulating transportation networks.

    This class provides an interface for implementing methods that process
    transportation data (such as system state and origin-destination files) and
    compute network performance metrics.

    Subclasses must define how to process these data inputs and update system
    performance in concrete terms.

    Attributes__
        assets (list): A list of asset types (e.g., 'Bridge', 'Roadway',
                      'Tunnel') to be analyzed in the transportation network.
        csv_filenames (list): A list of filenames (e.g., 'edges.csv', '
                              nodes.csv', 'closed_edges.csv') that are required
                              for network simulations.
        capacity_map (dict): A mapping that relates damage states to capacity
                             ratios. For example, damage states of 0-2 may
                             represent full capacity (1), while higher damage
                             states reduce capacity (e.g., 0.5 or 0).
        no_identifier (dict): A mapping of asset types to their unique
                              identifiers (e.g., 'StructureNumber' for Bridges,
                              'TigerOID' for Roadways). These are used to track
                              and manage assets within the system.

    Methods__
        system_state(detfile: str, csv_file_dir: str) -> None:
            Abstract method to process a given det (damage state) file and
            update the system state with capacity ratios. Also checks for
            missing or necessary CSV files for network simulation.

        update_od_file(old_nodes: str, old_det: str, new_nodes: str, new_det:
                       str, od: str, origin_ids: list) -> pd.DataFrame:
            Abstract method to update the origin-destination (OD) file based
            on population changes between time steps. The method tracks
            population growth in nodes and generates new trips in the OD file
            accordingly.

        system_performance(detfile: str, csv_file_dir: str) -> None:
            Abstract method to compute or update the performance of the
            transportation system based on current state and available data.

    Notes__
        This is an abstract class. To use it, create a subclass that implements
        the abstract methods for specific behavior related to transportation
        network performance analysis.
    """

    def __init__(
        self,
        assets: Union[list[str], None] = None,  # noqa: UP007
        capacity_map: Union[dict[int, float], None] = None,  # noqa: UP007
        csv_files: Union[dict[str, str], None] = None,  # noqa: UP007
        no_identifier: Union[dict[str, str], None] = None,  # noqa: UP007
        network_inventory: Union[dict[str, str], None] = None,  # noqa: UP007
        two_way_edges=False,  # noqa: FBT002
        od_file=None,
        hour_list=[],  # noqa: B006
        tmp_dir=None,
    ):  # noqa: B006, RUF100, UP007
        """
        Initialize the TransportationPerformance class with essential data.

        Args__
            assets (list): A list of asset types such as 'Bridge', 'Roadway',
                           'Tunnel'.
            capacity_map (dict): A mapping of damage states to capacity ratios.
            csv_files (dict): A dictionary of CSV filenames for network data,
                              including 'network_edges', 'network_nodes',
                              'edge_closures', and 'od_pairs'.
            no_identifier (dict): A mapping of asset types to their unique
                                  identifiers.
            network_inventory (dict): A dictionary of "edges" and "nodes" file.
        """
        if assets is None:
            assets = ['Bridge', 'Roadway', 'Tunnel']
        if capacity_map is None:
            # capacity_map = {0: 1, 1: 1, 2: 1, 3: 0.5, 4: 0}
            capacity_map = {0: 1, 1: 1, 2: 1, 3: 0, 4: 0}
        if csv_files is None:
            csv_files = {
                'network_edges': 'edges.csv',
                'network_nodes': 'nodes.csv',
                'edge_closures': 'closed_edges.csv',
                'od_pairs': 'od.csv',
            }
        if no_identifier is None:
            no_identifier = {
                'Bridge': 'StructureNumber',
                'Roadway': 'TigerOID',
                'Tunnel': 'TunnelNumber',
            }

        self.assets = assets
        self.csv_files = csv_files
        self.capacity_map = capacity_map
        self.no_identifier = no_identifier
        self.attribute_maps = {
            'lanes': ROADLANES_MAP,
            'speed': ROADSPEED_MAP,
            'capcity': calculate_road_capacity,
        }
        self.network_inventory = network_inventory
        self.two_way_edges = two_way_edges
        self.od_file = od_file
        self.hour_list = hour_list
        self.tmp_dir = tmp_dir

    # @abstractmethod
    def system_state(
        self, initial_state: str, csv_file_dir: str
    ) -> dict:  # updated_state
        """
        Process given det and damage results file to get updated system state.

        This function reads a JSON file containing undamaged network attributes
        and JSON file containing damage states and updates the state of the
        network (i.e., determines edges experiencing capacity reductions)
        using  capacity ratios defined for each damage state. It also checks
        for the existence of required CSV files, created the if missing, and
        generates a file listing closed edges.

        Args__
            detfile (str): Path to the JSON file containing the asset data.
            csv_file_dir (str): Directory containing the CSV files needed for
                                    running network simulations.

        Returns__
            The function does not return any value. It creates updated det file
            and CSV file necessary to run network simulations

        Raises__
            FileNotFoundError: If the `detfile` or any required CSV files are
                               not found.
            json.JSONDecodeError: If the `detfile` cannot be parsed as JSON.
            KeyError: If expected keys are missing in the JSON data.
            ValueError: If there are issues with data conversions, e.g., JSON
                        to integer.

        Examples__
            >>> system_state('damage_states.json', '/path/to/csv/files')
            Missing files: nodes.csv
            All required files are present.
            # This will process 'damage_states.json', update it, and use CSV
              files in '/path/to/csv/files'

            >>> system_state('damage_states.json', '/path/to/nonexistent/dir')
            Missing files: edges.csv, nodes.csv
            # This will attempt to process 'damage_states.json' and handle
              missing files in a non-existent directory
        """

        def files_exist(directory, filenames):
            # Convert directory path to a Path object
            dir_path = Path(directory)

            # Get a set of files in the directory
            files_in_directory = {f.name for f in dir_path.iterdir() if f.is_file()}

            # Check if each file exists in the directory
            missing_files = [
                filename
                for filename in filenames
                if filename not in files_in_directory
            ]

            if missing_files:
                print(f"Missing files: {', '.join(missing_files)}")  # noqa: T201
                out = False
            else:
                print('All required files are present.')  # noqa: T201
                out = True

            return out

        # Create link closures for network simulations:
        fexists = files_exist(csv_file_dir, [self.csv_files['network_edges']])

        if fexists:
            pass
            # graph_edge_file = os.path.join(csv_file_dir, self.csv_files['network_edges'])
            # graph_edge_df = pd.read_csv(graph_edge_file)
        else:
            self.get_graph_network(csv_file_dir)

        # Read damage states for det file and determine element capacity ratios
        # 1 denotes fully open and 0 denotes fully closed:
        capacity_dict = {}
        closed_edges = []
        with Path.open(Path(initial_state), encoding='utf-8') as file:
            temp = json.load(file)
            data = temp['TransportationNetwork']
            for asset_type in self.assets:
                datadict = data[asset_type]
                for aim_id in datadict:
                    item_id = datadict[aim_id]['GeneralInformation'][
                        self.no_identifier[asset_type]
                    ]
                    damage_state = int(
                        datadict[aim_id]['R2Dres'][
                            'R2Dres_MostLikelyCriticalDamageState'
                        ]
                    )
                    capacity_ratio = self.capacity_map[damage_state]
                    capacity_dict[item_id] = capacity_ratio
                    datadict[aim_id]['GeneralInformation']['Open'] = capacity_ratio
                    if capacity_ratio == 0:
                        if asset_type == 'Roadway':
                            closed_edges.append(int(aim_id))
                        elif asset_type == 'Bridge' or asset_type == 'Tunnel':  # noqa: PLR1714
                            carried_edges = datadict[aim_id]['GeneralInformation'][
                                'RoadID'
                            ]
                            carried_edges = [int(x) for x in carried_edges]
                            closed_edges += carried_edges

        # Update det file with closure information:
        temp = os.path.basename(initial_state).split('.')  # noqa: PTH119
        detfile_updated = temp[0] + '_updated.' + temp[1]
        detfile_updated = os.path.join(csv_file_dir, detfile_updated)  # noqa: PTH118

        with Path.open(Path(detfile_updated), 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)

        # Write closed edges:
        edge_closure_file = os.path.join(  # noqa: PTH118
            csv_file_dir, self.csv_files['edge_closures']
        )
        with open(edge_closure_file, 'w', encoding='utf-8') as file:  # noqa: PTH123
            # Write each item on a new line
            file.write('uniqueid\n')
            for item in closed_edges:
                file.write(str(item) + '\n')

        return

    def update_edge_capacity(self, damage_rlz_file, damage_det_file):  # noqa: D102
        with Path(damage_rlz_file).open() as file:
            damage_rlz = json.load(file)
        with Path(damage_det_file).open() as file:
            damage_det = json.load(file)
        transportation_damage = damage_rlz['TransportationNetwork']
        edges = pd.read_csv(self.csv_files['network_edges'])
        edges = edges.set_index('id')
        orig_capacity = edges['capacity'].to_dict()
        orig_maxspeed = edges['maxspeed'].to_dict()
        new_capacity = edges['capacity'].apply(lambda x: [x]).to_dict()
        new_maxspeed = edges['maxspeed'].apply(lambda x: [x]).to_dict()
        closed_links_roads_id = []
        for asset_type in self.assets:
            for asset_id, asset_id_dict in transportation_damage[asset_type].items():
                critical_ds = int(max(list(asset_id_dict['Damage'].values())))
                capacity_ratio = self.capacity_map[asset_type][str(critical_ds)]
                if capacity_ratio == 0:
                    closed_links_roads_id.append(asset_id)
                if asset_type == 'Roadway':
                    road_ids = [int(asset_id)]
                else:
                    road_id_str = damage_det['TransportationNetwork'][asset_type][
                        asset_id
                    ]['GeneralInformation']['RoadID']
                    road_ids = [int(x) for x in road_id_str.split(',')]
                for road_id in road_ids:
                    new_capacity[road_id].append(
                        orig_capacity[road_id] * capacity_ratio
                    )
                    new_maxspeed[road_id].append(
                        orig_maxspeed[road_id] * capacity_ratio
                    )
        for key, value in new_capacity.items():
            new_capacity[key] = min(value)
        for key, value in new_maxspeed.items():
            new_maxspeed[key] = min(value)
        new_capacity_df = pd.DataFrame.from_dict(
            new_capacity, orient='index', columns=['capacity']
        )
        new_maxspeed_df = pd.DataFrame.from_dict(
            new_maxspeed, orient='index', columns=['maxspeed']
        )
        edges = edges.merge(new_capacity_df, left_index=True, right_index=True)
        edges = edges.merge(new_maxspeed_df, left_index=True, right_index=True)
        edges = edges.drop(columns=['capacity_x', 'maxspeed_x'])
        edges = edges.rename(
            columns={'capacity_y': 'capacity', 'maxspeed_y': 'maxspeed'}
        )
        closed_links = edges[edges.index.isin(closed_links_roads_id)]
        edges['capacity'] = edges['capacity'].apply(lambda x: 1 if x == 0 else x)
        edges['maxspeed'] = edges['maxspeed'].apply(lambda x: 0.001 if x == 0 else x)
        damged_edges_file = Path.cwd() / 'damaged_edges.csv'
        closed_links_file = Path.cwd() / 'closed_edges.csv'
        edges = edges.reset_index().rename(columns={'index': 'id'})
        closed_links = closed_links.reset_index().rename(columns={'index': 'id'})
        edges.to_csv(damged_edges_file, index=False)
        closed_links.to_csv(closed_links_file, index=False)
        return damged_edges_file, closed_links_file

    def get_graph_network(self, csv_file_dir) -> None:  # noqa: D102
        # Get edges and nodes from the network inventory
        edges_file = self.network_inventory['edges']
        nodes_file = self.network_inventory['nodes']
        edges_gpd = gpd.read_file(edges_file)
        nodes_gpd = gpd.read_file(nodes_file)
        # Format edges and nodes for Pandana
        ## Edges
        edges_gpd['id'] = edges_gpd['id'].astype(int)
        edges_gpd = edges_gpd.rename(
            columns={
                'id': 'uniqueid',
                'StartNode': 'start_nid',
                'EndNode': 'end_nid',
                'RoadType': 'type',
                'NumOfLanes': 'lanes',
                'MaxMPH': 'maxspeed',
            }
        )
        edges_gpd['capacity'] = edges_gpd['lanes'].map(calculate_road_capacity)
        edges_gpd = edges_gpd.to_crs('EPSG:6500')
        edges_gpd['length'] = edges_gpd['geometry'].apply(lambda x: x.length)
        edges_gpd = edges_gpd.to_crs('EPSG:4326')
        edges_fils = os.path.join(csv_file_dir, self.csv_files['network_edges'])  # noqa: PTH118
        edges_gpd.to_csv(edges_fils, index=False)
        ## Nodes
        nodes_gpd = nodes_gpd.rename(columns={'nodeID': 'node_id'})
        nodes_gpd['lon'] = nodes_gpd['geometry'].apply(lambda x: x.x)
        nodes_gpd['lat'] = nodes_gpd['geometry'].apply(lambda x: x.y)
        nodes_file = os.path.join(csv_file_dir, self.csv_files['network_nodes'])  # noqa: PTH118
        nodes_gpd.to_csv(nodes_file, index=False)

    def substep_assignment(  # noqa: PLR0913
        self,
        nodes_df=None,
        weighted_edges_df=None,
        od_ss=None,
        quarter_demand=None,
        assigned_demand=None,
        quarter_counts=4,
        trip_info=None,
        agent_time_limit=0,
        sample_interval=1,
        agents_path=None,
        hour=None,
        quarter=None,
        ss_id=None,
        alpha_f=0.3,
        beta_f=3,
        two_way_edges=False,  # noqa: FBT002
    ):
        """
        Perform substep assignment for transportation network simulation.

        Args:
            nodes_df (pd.DataFrame): DataFrame containing node information.
            weighted_edges_df (pd.DataFrame): DataFrame containing edge information with weights.
            od_ss (pd.DataFrame): DataFrame containing origin-destination pairs for the substep.
            quarter_demand (int): Total demand for the quarter.
            assigned_demand (int): Demand assigned in the current substep.
            quarter_counts (int): Number of quarters in the simulation.
            trip_info (dict): Dictionary containing trip information.
            agent_time_limit (int): Time limit for agents.
            sample_interval (int): Sampling interval.
            agents_path (str): Path to agent data.
            hour (int): Current hour of the simulation.
            quarter (int): Current quarter of the simulation.
            ss_id (int): Substep ID.
            alpha_f (float): Alpha factor for travel time calculation.
            beta_f (float): Beta factor for travel time calculation.
            two_way_edges (bool): Flag indicating if edges are two-way.

        Returns
        -------
            tuple: Updated edges DataFrame, residual OD list, trip information, and agent paths.
        """
        # open_edges_df = weighted_edges_df.loc[weighted_edges_df['fft'] < 36000]
        open_edges_df = weighted_edges_df

        net = pdna.Network(
            nodes_df['x'],
            nodes_df['y'],
            open_edges_df['start_nid'],
            open_edges_df['end_nid'],
            open_edges_df[['weight']],
            twoway=two_way_edges,
        )

        # print('network')  # noqa: RUF100, T201
        net.set(pd.Series(net.node_ids))
        # print('net')  # noqa: RUF100, T201

        nodes_origin = od_ss['origin_nid'].to_numpy()
        nodes_destin = od_ss['destin_nid'].to_numpy()
        nodes_current = od_ss['current_nid'].to_numpy()
        agent_ids = od_ss['agent_id'].to_numpy()
        agent_current_links = od_ss['current_link'].to_numpy()
        agent_current_link_times = od_ss['current_link_time'].to_numpy()
        paths = net.shortest_paths(nodes_current, nodes_destin)

        # check agent time limit
        path_lengths = net.shortest_path_lengths(nodes_current, nodes_destin)
        remove_agent_list = []
        if agent_time_limit is None:
            pass
        else:
            for agent_idx, agent_id in enumerate(agent_ids):
                planned_trip_length = path_lengths[agent_idx]
                # agent_time_limit[agent_id]
                trip_length_limit = agent_time_limit
                if planned_trip_length > trip_length_limit + 0:
                    remove_agent_list.append(agent_id)

        edge_travel_time_dict = weighted_edges_df['t_avg'].T.to_dict()
        edge_current_vehicles = weighted_edges_df['veh_current'].T.to_dict()
        edge_quarter_vol = weighted_edges_df['vol_true'].T.to_dict()
        # edge_length_dict = weighted_edges_df['length'].T.to_dict()
        od_residual_ss_list = []
        # all_paths = []
        path_i = 0
        for path in paths:
            trip_origin = nodes_origin[path_i]
            trip_destin = nodes_destin[path_i]
            agent_id = agent_ids[path_i]
            # remove some agent (path too long)
            if agent_id in remove_agent_list:
                path_i += 1
                # no need to update trip info
                continue
            remaining_time = (
                3600 / quarter_counts + agent_current_link_times[path_i]
            )
            used_time = 0
            for edge_s, edge_e in zip(path, path[1:]):
                edge_str = f'{edge_s}-{edge_e}'
                edge_travel_time = edge_travel_time_dict[edge_str]
                if (remaining_time > edge_travel_time) and (
                    edge_travel_time < 36000  # noqa: PLR2004
                ):
                    # all_paths.append(edge_str)
                    # p_dist += edge_travel_time
                    remaining_time -= edge_travel_time
                    used_time += edge_travel_time
                    edge_quarter_vol[edge_str] += 1 * sample_interval
                    trip_stop = edge_e
                    if edge_str == agent_current_links[path_i]:
                        edge_current_vehicles[edge_str] -= 1 * sample_interval
                else:
                    if edge_str != agent_current_links[path_i]:
                        edge_current_vehicles[edge_str] += 1 * sample_interval
                    new_current_link = edge_str
                    new_current_link_time = remaining_time
                    trip_stop = edge_s
                    od_residual_ss_list.append(
                        [
                            agent_id,
                            trip_origin,
                            trip_destin,
                            trip_stop,
                            new_current_link,
                            new_current_link_time,
                        ]
                    )
                    break
            trip_info[(agent_id, trip_origin, trip_destin)][0] += (
                3600 / quarter_counts
            )
            trip_info[(agent_id, trip_origin, trip_destin)][1] += used_time
            trip_info[(agent_id, trip_origin, trip_destin)][2] = trip_stop
            trip_info[(agent_id, trip_origin, trip_destin)][3] = hour
            trip_info[(agent_id, trip_origin, trip_destin)][4] = quarter
            trip_info[(agent_id, trip_origin, trip_destin)][5] = ss_id
            path_i += 1

        new_edges_df = weighted_edges_df[
            [
                'uniqueid',
                'u',
                'v',
                'start_nid',
                'end_nid',
                'fft',
                'capacity',
                'normal_fft',
                'normal_capacity',
                'length',
                'vol_true',
                'vol_tot',
                'veh_current',
                'geometry',
            ]
        ].copy()
        # new_edges_df = new_edges_df.join(edge_volume, how='left')
        # new_edges_df['vol_ss'] = new_edges_df['vol_ss'].fillna(0)
        # new_edges_df['vol_true'] += new_edges_df['vol_ss']
        new_edges_df['vol_true'] = new_edges_df.index.map(edge_quarter_vol)
        new_edges_df['veh_current'] = new_edges_df.index.map(
            edge_current_vehicles
        )
        # new_edges_df['vol_tot'] += new_edges_df['vol_ss']
        new_edges_df['flow'] = (
            new_edges_df['vol_true'] * quarter_demand / assigned_demand
        ) * quarter_counts
        new_edges_df['t_avg'] = new_edges_df['fft'] * (
            1
            + alpha_f
            * (new_edges_df['flow'] / new_edges_df['capacity']) ** beta_f
        )
        new_edges_df['t_avg'] = np.where(
            new_edges_df['t_avg'] > 36000, 36000, new_edges_df['t_avg']  # noqa: PLR2004
        )
        new_edges_df['t_avg'] = new_edges_df['t_avg'].round(2)
        return new_edges_df, od_residual_ss_list, trip_info, agents_path
    def write_edge_vol(
        self,
        edges_df=None,
        simulation_outputs=None,
        quarter=None,
        hour=None,
        scen_nm=None,
    ):
        """
        Write edge volume data to a CSV file.

            Args:
                edges_df (pd.DataFrame): DataFrame containing edge information.
                simulation_outputs (str): Directory to save the output files.
                quarter (int): Current quarter of the simulation.
                hour (int): Current hour of the simulation.
                scen_nm (str): Scenario name for the simulation.

        Returns
        -------
                None
        """
        if 'flow' in edges_df.columns:
            if edges_df.shape[0] < 10:  # noqa: PLR2004
                edges_df[
                    [
                        'uniqueid',
                        'start_nid',
                        'end_nid',
                        'capacity',
                        'veh_current',
                        'vol_true',
                        'vol_tot',
                        'flow',
                        't_avg',
                        'geometry',
                    ]
                ].to_csv(
                    f'{simulation_outputs}/edge_vol/edge_vol_hr{hour}_'
                    f'qt{quarter}_{scen_nm}.csv',
                    index=False,
                )
            else:
                edges_df.loc[
                    edges_df['vol_true'] > 0,
                    [
                        'uniqueid',
                        'start_nid',
                        'end_nid',
                        'capacity',
                        'veh_current',
                        'vol_true',
                        'vol_tot',
                        'flow',
                        't_avg',
                        'geometry',
                    ],
                ].to_csv(
                    f'{simulation_outputs}/edge_vol/edge_vol_hr{hour}_'
                    f'qt{quarter}_{scen_nm}.csv',
                    index=False,
                )
    def write_final_vol(
        self,
        edges_df=None,
        simulation_outputs=None,
        quarter=None,
        hour=None,
        scen_nm=None,
    ):
        """
        Write the final volume data to a CSV file.

            Args:
                edges_df (pd.DataFrame): DataFrame containing edge information.
                simulation_outputs (str): Directory to save the output files.
                quarter (int): Current quarter of the simulation.
                hour (int): Current hour of the simulation.
                scen_nm (str): Scenario name for the simulation.

        Returns
        -------
                None
        """
        edges_df.loc[
            edges_df['vol_tot'] > 0,
            ['uniqueid', 'start_nid', 'end_nid', 'vol_tot', 'geometry'],
        ].to_csv(
            simulation_outputs / 'edge_vol' / f'final_edge_vol_hr{hour}_qt'
            f'{quarter}_{scen_nm}.csv',
            index=False,
        )
    def assignment(  # noqa: C901, PLR0913
        self,
        quarter_counts=6,
        substep_counts=15,
        substep_size=30000,
        edges_df=None,
        nodes_df=None,
        od_all=None,
        simulation_outputs=None,
        scen_nm=None,
        hour_list=None,
        quarter_list=None,
        cost_factor=None,  # noqa: ARG002
        closure_hours=None,
        closed_links=None,
        agent_time_limit=None,
        sample_interval=1,
        agents_path=None,
        alpha_f=0.3,
        beta_f=4,
        two_way_edges=False,  # noqa: FBT002
        save_edge_vol=True,  # noqa: FBT002
    ):
        """
        Perform traffic assignment for the transportation network simulation.

        Args:
            quarter_counts (int): Number of quarters in the simulation.
            substep_counts (int): Number of substeps in the simulation.
            substep_size (int): Size of each substep.
            edges_df (pd.DataFrame): DataFrame containing edge information.
            nodes_df (pd.DataFrame): DataFrame containing node information.
            od_all (pd.DataFrame): DataFrame containing origin-destination pairs.
            simulation_outputs (str): Directory to save the output files.
            scen_nm (str): Scenario name for the simulation.
            hour_list (list): List of hours in the simulation.
            quarter_list (list): List of quarters in the simulation.
            cost_factor (float): Cost factor for travel time calculation.
            closure_hours (list): List of hours when closures occur.
            closed_links (pd.DataFrame): DataFrame containing closed links.
            agent_time_limit (int): Time limit for agents.
            sample_interval (int): Sampling interval.
            agents_path (str): Path to agent data.
            alpha_f (float): Alpha factor for travel time calculation.
            beta_f (float): Beta factor for travel time calculation.
            two_way_edges (bool): Flag indicating if edges are two-way.
            save_edge_vol (bool): Flag indicating if edge volume should be saved.

        Returns
        -------
            pd.DataFrame: DataFrame containing trip information.
        """
        if closure_hours is None:
            closure_hours = []

        # Check if all od pairs has path. If not,
        orig = od_all['origin_nid'].to_numpy()
        dest = od_all['destin_nid'].to_numpy()
        open_edges_df = edges_df[
            ~edges_df['uniqueid'].isin(closed_links['uniqueid'].to_numpy())
        ]
        # Redirect the output from pdna to a tmp file and then delete the file
        # if self.tmp_dir is not None:
        #     output_file = Path(self.tmp_dir) / 'pandana_stdout.txt'
        #     original_stdout_fd = sys.stdout.fileno()
        #     with Path.open(output_file, 'w') as file:
        #         os.dup2(file.fileno(), original_stdout_fd)
        #         net = pdna.Network(
        #             nodes_df['x'],
        #             nodes_df['y'],
        #             open_edges_df['start_nid'],
        #             open_edges_df['end_nid'],
        #             open_edges_df[['fft']],
        #             twoway=two_way_edges,
        #         )
        #         # The file is automatically closed when exiting the with block
        #         # `sys.stdout` is automatically restored to its original state because
        #         # we duplicated the original descriptor to `stdout`.
        #     if getattr(self, 'save_pandana', True):
        #         Path.unlink(output_file)
        # else:
        #     net = pdna.Network(
        #             nodes_df['x'],
        #             nodes_df['y'],
        #             open_edges_df['start_nid'],
        #             open_edges_df['end_nid'],
        #             open_edges_df[['fft']],
        #             twoway=two_way_edges,
        #         )

        # Nikola: have issues with this way of redirecting output
        # different way of supressing the print statements
        net = pdna.Network(
                    nodes_df['x'],
                    nodes_df['y'],
                    open_edges_df['start_nid'],
                    open_edges_df['end_nid'],
                    open_edges_df[['fft']],
                    twoway=two_way_edges,
                )
        net.set(pd.Series(net.node_ids))
        paths = net.shortest_paths(orig, dest)
        no_path_ind = [i for i in range(len(paths)) if len(paths[i]) == 0]
        od_no_path = od_all.iloc[no_path_ind].copy()
        od_all = od_all.drop(od_no_path.index)

        od_all['current_nid'] = od_all['origin_nid']
        trip_info = {
            (od.agent_id, od.origin_nid, od.destin_nid): [
                0,
                0,
                od.origin_nid,
                0,
                od.hour,
                od.quarter,
                0,
                0,
            ]
            for od in od_all.itertuples()
        }

        # Quarters and substeps
        # probability of being in each division of hour
        if quarter_list is None:
            quarter_counts = 4
        else:
            quarter_counts = len(quarter_list)
        quarter_ps = [1 / quarter_counts for i in range(quarter_counts)]
        quarter_ids = list(range(quarter_counts))

        # initial setup
        od_residual_list = []
        # accumulator
        edges_df['vol_tot'] = 0
        edges_df['veh_current'] = 0

        # Loop through days and hours
        for _day in ['na']:
            for hour in hour_list:
                gc.collect()
                if hour in closure_hours:
                    # Note this is not used now as the closed links are dropped from
                    # the road network
                    for row in closed_links.itertuples():
                        edges_df.loc[
                            (edges_df['uniqueid'] == row.uniqueid), 'capacity'
                        ] = 1
                        edges_df.loc[
                            (edges_df['uniqueid'] == row.uniqueid), 'fft'
                        ] = 36000
                else:
                    edges_df['capacity'] = edges_df['normal_capacity']
                    edges_df['fft'] = edges_df['normal_fft']

                # Read OD
                od_hour = od_all[od_all['hour'] == hour].copy()
                if od_hour.shape[0] == 0:
                    od_hour = pd.DataFrame([], columns=od_all.columns)
                od_hour['current_link'] = None
                od_hour['current_link_time'] = 0

                # Divide into quarters
                if 'quarter' in od_all.columns:
                    pass
                else:
                    od_quarter_msk = np.random.choice(
                        quarter_ids, size=od_hour.shape[0], p=quarter_ps
                    )
                    od_hour['quarter'] = od_quarter_msk

                if quarter_list is None:
                    quarter_list = quarter_ids
                for quarter in quarter_list:
                    # New OD in assignment period
                    od_quarter = od_hour.loc[
                        od_hour['quarter'] == quarter,
                        [
                            'agent_id',
                            'origin_nid',
                            'destin_nid',
                            'current_nid',
                            'current_link',
                            'current_link_time',
                        ],
                    ]
                    # Add resudal OD
                    od_residual = pd.DataFrame(
                        od_residual_list,
                        columns=[
                            'agent_id',
                            'origin_nid',
                            'destin_nid',
                            'current_nid',
                            'current_link',
                            'current_link_time',
                        ],
                    )
                    od_residual['quarter'] = quarter
                    # Total OD in each assignment period is the combined
                    # of new and residual OD:
                    od_quarter = pd.concat(
                        [od_quarter, od_residual], sort=False, ignore_index=True
                    )
                    # Residual OD is no longer residual after it has been
                    # merged to the quarterly OD:
                    od_residual_list = []
                    od_quarter = od_quarter[
                        od_quarter['current_nid'] != od_quarter['destin_nid']
                    ]
                    # total demand for this quarter, including total and
                    # residual demand:
                    quarter_demand = od_quarter.shape[0]
                    # how many among the OD pairs to be assigned in this
                    # quarter are actually residual from previous quarters
                    residual_demand = od_residual.shape[0]
                    assigned_demand = 0

                    substep_counts = max(1, (quarter_demand // substep_size) + 1)
                    logging.info(
                        f'HR {hour} QT {quarter} has '
                        f'{quarter_demand}/{residual_demand} od'
                        f's/residuals {substep_counts} substeps'
                    )
                    substep_ps = [
                        1 / substep_counts for i in range(substep_counts)
                    ]
                    substep_ids = list(range(substep_counts))
                    od_substep_msk = np.random.choice(
                        substep_ids, size=quarter_demand, p=substep_ps
                    )
                    od_quarter['ss_id'] = od_substep_msk
                    # reset volume at each quarter
                    edges_df['vol_true'] = 0

                    for ss_id in substep_ids:
                        gc.collect()
                        time_ss_0 = time.time()
                        logging.info(
                            f'Hour: {hour}, Quarter: {quarter}, '
                            'SS ID: {ss_id}'
                        )
                        od_ss = od_quarter[od_quarter['ss_id'] == ss_id]
                        assigned_demand += od_ss.shape[0]
                        if assigned_demand == 0:
                            continue
                        # calculate weight
                        weighted_edges_df = edges_df.copy()
                        # weight by travel distance
                        # weighted_edges_df['weight'] = edges_df['length']
                        # weight by travel time
                        # weighted_edges_df['weight'] = edges_df['t_avg']
                        # weight by travel time
                        # weighted_edges_df['weight'] = (edges_df['t_avg']
                        # - edges_df['fft']) * 0.5 + edges_df['length']*0.1
                        # + cost_factor*edges_df['length']*0.1*(
                        # edges_df['is_highway'])
                        # 10 yen per 100 m --> 0.1 yen per m
                        weighted_edges_df['weight'] = edges_df['t_avg']
                        open_edges_df = weighted_edges_df[
                            ~weighted_edges_df['uniqueid'].isin(closed_links['uniqueid'].to_numpy())
                        ]
                        # weighted_edges_df['weight'] = np.where(
                        # weighted_edges_df['weight']<0.1, 0.1,
                        # weighted_edges_df['weight'])
                        # traffic assignment with truncated path
                        (
                            edges_df,
                            od_residual_ss_list,
                            trip_info,
                            agents_path,
                        ) = self.substep_assignment(
                            nodes_df=nodes_df,
                            weighted_edges_df=open_edges_df,
                            od_ss=od_ss,
                            quarter_demand=quarter_demand,
                            assigned_demand=assigned_demand,
                            quarter_counts=quarter_counts,
                            trip_info=trip_info,
                            agent_time_limit=agent_time_limit,
                            sample_interval=sample_interval,
                            agents_path=agents_path,
                            hour=hour,
                            quarter=quarter,
                            ss_id=ss_id,
                            alpha_f=alpha_f,
                            beta_f=beta_f,
                            two_way_edges=two_way_edges,
                        )
                        od_residual_list += od_residual_ss_list
                        # write_edge_vol(edges_df=edges_df,
                        #            simulation_outputs=simulation_outputs,
                        #               quarter=quarter,
                        #               hour=hour,
                        #         scen_nm='ss{}_{}'.format(ss_id, scen_nm))
                        logging.info(
                            f'HR {hour} QT {quarter} SS {ss_id}'
                            ' finished, max vol '
                            f'{np.max(edges_df["vol_true"])}, '
                            f'time {time.time() - time_ss_0}'
                        )

                    # write quarterly results
                    edges_df['vol_tot'] += edges_df['vol_true']
                    if save_edge_vol:  # hour >=16 or (hour==15 and quarter==3):
                        self.write_edge_vol(
                            edges_df=edges_df,
                            simulation_outputs=simulation_outputs,
                            quarter=quarter,
                            hour=hour,
                            scen_nm=scen_nm,
                        )

        trip_info_df = pd.DataFrame(
            [
                [
                    trip_key[0],
                    trip_key[1],
                    trip_key[2],
                    trip_value[0],
                    trip_value[1],
                    trip_value[2],
                    trip_value[3],
                    trip_value[4],
                    trip_value[5],
                ]
                for trip_key, trip_value in trip_info.items()
            ],
            columns=[
                'agent_id',
                'origin_nid',
                'destin_nid',
                'travel_time',
                'travel_time_used',
                'stop_nid',
                'stop_hour',
                'stop_quarter',
                'stop_ssid',
            ],
        )
        # If there are trips incompleted mark them as np.nan
        incomplete_trips_agent_id = [x[0] for x in od_residual_list]
        trip_info_df.loc[trip_info_df.agent_id.isin(incomplete_trips_agent_id),'travel_time_used'] = math.inf
        # Add the no path OD to the trip info
        trip_info_no_path = od_no_path.drop(
            columns=[
                col
                for col in od_no_path.columns
                if col not in ['agent_id', 'origin_nid', 'destin_nid']
            ]
        )
        trip_info_no_path['travel_time'] = 360000
        trip_info_no_path['travel_time_used'] = math.inf
        trip_info_no_path['stop_nid'] = np.nan
        trip_info_no_path['stop_hour'] = np.nan
        trip_info_no_path['stop_quarter'] = np.nan
        trip_info_no_path['stop_ssid'] = np.nan
        trip_info_df = pd.concat(
            [trip_info_df, trip_info_no_path], ignore_index=True
        )
        if save_edge_vol:
            trip_info_df.to_csv(
                simulation_outputs / 'trip_info' / f'trip_info_{scen_nm}.csv',
                index=False,
            )

            self.write_final_vol(
                    edges_df=edges_df,
                    simulation_outputs=simulation_outputs,
                    quarter=quarter,
                    hour=hour,
                    scen_nm=scen_nm,
                )
        return trip_info_df
    # @abstractmethod
    def system_performance(
        self, state  # noqa: ARG002
    ) -> None:  # Move the CSV creation here
        """
        Compute or update the performance of the transportation system.

            This method processes the current state of the transportation network,
            reads necessary CSV files, and performs traffic assignment to evaluate
            system performance.

            Args:
                state: The current state of the transportation network.

        Returns
        -------
                None
        """
        network_edges = self.csv_files['network_edges']
        network_nodes = self.csv_files['network_nodes']
        closed_edges_file = self.csv_files['edge_closures']
        demand_file = self.od_file
        simulation_outputs = self.simulation_outputs
        scen_nm = 'simulation_out'

        hour_list = self.hour_list
        if hour_list is None or len(hour_list) == 0:
            od_all = pd.read_csv(demand_file)
            hour_list = sorted(od_all['hour'].unique())
        quarter_list = [0, 1, 2, 3, 4, 5]
        closure_hours = hour_list

        edges_df = pd.read_csv(network_edges)
        # edges_df = edges_df[["uniqueid", "geometry", "osmid", "length", "type",
        #                      "lanes", "maxspeed", "fft", "capacity",
        #                      "start_nid", "end_nid"]]
        edges_df = edges_df[
            [
                'uniqueid',
                'id',
                'geometry',
                'length',
                'lanes',
                'maxspeed',
                'capacity',
                'normal_capacity',
                'normal_maxspeed',
                'start_nid',
                'end_nid',
            ]
        ]
        edges_df = gpd.GeoDataFrame(
            edges_df, crs='epsg:4326', geometry=edges_df['geometry'].map(loads)
        )
        # pay attention to the unit conversion, length is in meters, maxspeed is mph
        # fft is in seconds
        edges_df['fft'] = edges_df['length'] / edges_df['maxspeed'] * METER_PER_SECOND_TO_MILES_PER_HOUR
        edges_df['normal_fft'] = (
            edges_df['length'] / edges_df['normal_maxspeed'] * METER_PER_SECOND_TO_MILES_PER_HOUR
        )
        edges_df = edges_df.sort_values(by='fft', ascending=False).drop_duplicates(
            subset=['start_nid', 'end_nid'], keep='first'
        )
        edges_df['edge_str'] = (
            edges_df['start_nid'].astype('str')
            + '-'
            + edges_df['end_nid'].astype('str')
        )
        edges_df['t_avg'] = edges_df['fft']
        edges_df['u'] = edges_df['start_nid']
        edges_df['v'] = edges_df['end_nid']
        edges_df = edges_df.set_index('edge_str')
        # closure locations
        if closed_edges_file is not None:
            closed_links = pd.read_csv(closed_edges_file)
            for row in closed_links.itertuples():
                edges_df.loc[(edges_df['uniqueid'] == row.uniqueid), 'capacity'] = 1
                edges_df.loc[(edges_df['uniqueid'] == row.uniqueid), 'fft'] = 36000
        else:
            closed_links = pd.DataFrame([], columns=['uniqueid'])
        # output closed file for visualization
        # edges_df.loc[edges_df['fft'] == 36000, ['uniqueid',
        #                                         'start_nid',
        #                                         'end_nid',
        #                                         'capacity',
        #                                         'fft',
        #                                         'geometry']].to_csv(
        #                                             simulation_outputs +
        #                                             '/closed_links_'
        #                                             f'{scen_nm}.csv')

        # nodes processing
        nodes_df = pd.read_csv(network_nodes)

        nodes_df['x'] = nodes_df['lon']
        nodes_df['y'] = nodes_df['lat']
        nodes_df = nodes_df.set_index('node_id')

        # demand processing
        t_od_0 = time.time()
        od_all = pd.read_csv(demand_file)
        t_od_1 = time.time()
        logging.info('%d sec to read %d OD pairs', t_od_1 - t_od_0, od_all.shape[0])
        # run residual_demand_assignment
        self.assignment(
            edges_df=edges_df,
            nodes_df=nodes_df,
            od_all=od_all,
            simulation_outputs=simulation_outputs,
            scen_nm=scen_nm,
            hour_list=hour_list,
            quarter_list=quarter_list,
            closure_hours=closure_hours,
            closed_links=closed_links,
            two_way_edges=self.two_way_edges,
        )

    # @abstractmethod
    def update_od_file(
        self,
        old_nodes: str,
        old_det: str,
        new_nodes: str,
        new_det: str,
        od: str,
        origin_ids: list[int],
    ) -> pd.DataFrame:
        """
        Update origin-destination (OD) file from changes in population data.

        This function updates an OD file by calculating the population changes
        at each node between two time steps and generates trips originating
        from specified origins and ending at nodes where the population has
        increased. The updated OD data is saved to a new file.

        Args__
            old_nodes (str): Path to the CSV file containing the node
                             information at the previous time step.
            old_det (str): Path to the JSON file containing the building
                            information at the previous time step.
            new_nodes (str): Path to the CSV file containing the node
                             information at the current time step.
            new_det (str): Path to the JSON file containing the building
                            information at the current time step.
            od (str): Path to the existing OD file to be updated.
            origin_ids (List[int]): List of IDs representing possible origins
                                    for generating trips.

        Returns__
            pd.DataFrame: The updated OD DataFrame with new trips based on
                            population changes.

        Raises__
            FileNotFoundError: If any of the provided file paths are incorrect
                                or the files do not exist.
            json.JSONDecodeError: If the JSON files cannot be read or parsed
                                    correctly.
            KeyError: If expected keys are missing in the JSON data.
            ValueError: If there are issues with data conversions or
                        calculations.

        Examples__
            >>> update_od_file(
                    'old_nodes.csv',
                    'old_building_data.json',
                    'new_nodes.csv',
                    'new_building_data.json',
                    'existing_od.csv',
                    [1, 2, 3, 4]
                )
            The function will process the provided files, calculate population
            changes, and update the OD file with new trips. The result will be
            saved to 'updated_od.csv'.

        Notes__
            - Ensure that the columns `lat`, `lon`, and `node_id` are present
                in the nodes CSV files.
            - The `det` files should contain the `Buildings` and
                `GeneralInformation` sections with appropriate keys.
            - The OD file should have the columns `agent_id`, `origin_nid`,
                `destin_nid`, `hour`, and `quarter`.
        """

        # Extract the building information from the det file and convert it to
        # a pandas dataframe
        def extract_building_from_det(det):
            # Open the det file
            with Path.open(det, encoding='utf-8') as file:
                # Return the JSON object as a dictionary
                json_data = json.load(file)

            # Extract the required information and convert it to a pandas
            # dataframe
            extracted_data = []

            for aim_id, info in json_data['Buildings']['Building'].items():
                general_info = info.get('GeneralInformation', {})
                extracted_data.append(
                    {
                        'AIM_id': aim_id,
                        'Latitude': general_info.get('Latitude'),
                        'Longitude': general_info.get('Longitude'),
                        'Population': general_info.get('Population'),
                    }
                )

            return pd.DataFrame(extracted_data)

        # Aggregate the population in buildings to the closest road network
        # node
        def closest_neighbour(building_df, nodes_df):
            # Find the nearest road network node to each building
            nodes_xy = np.array(
                [nodes_df['lat'].to_numpy(), nodes_df['lon'].to_numpy()]
            ).transpose()
            building_df['closest_node'] = building_df.apply(
                lambda x: cdist(
                    [(x['Latitude'], x['Longitude'])], nodes_xy
                ).argmin(),
                axis=1,
            )

            # Merge the road network and building dataframes
            merged_df = nodes_df.merge(
                building_df, left_on='node_id', right_on='closest_node', how='left'
            )
            merged_df = merged_df.drop(
                columns=['AIM_id', 'Latitude', 'Longitude', 'closest_node']
            )
            merged_df = merged_df.fillna(0)

            # Aggregate population of  neareast buildings to the road network
            # node
            updated_nodes_df = (
                merged_df.groupby('node_id')
                .agg(
                    {
                        'lon': 'first',
                        'lat': 'first',
                        'geometry': 'first',
                        'Population': 'sum',
                    }
                )
                .reset_index()
            )

            return updated_nodes_df  # noqa: RET504

        # Function to add the population information to the nodes file
        def update_nodes_file(nodes, det):
            # Read the nodes file
            nodes_df = pd.read_csv(nodes)
            # Extract the building information from the det file and convert it
            # to a pandas dataframe
            building_df = extract_building_from_det(det)
            # Aggregate the population in buildings to the closest road network
            # node
            updated_nodes_df = closest_neighbour(building_df, nodes_df)

            return updated_nodes_df  # noqa: RET504

        # Read the od file
        od_df = pd.read_csv(od)
        # Add the population information to nodes dataframes at the last and
        # current time steps
        old_nodes_df = update_nodes_file(old_nodes, old_det)
        new_nodes_df = update_nodes_file(new_nodes, new_det)
        # Calculate the population changes at each node (assuming that
        # population will only increase at each node)
        population_change_df = old_nodes_df.copy()
        population_change_df['Population Change'] = (
            new_nodes_df['Population'] - old_nodes_df['Population']
        )
        population_change_df['Population Change'].astype(int)
        # Randomly generate the trips that start at one of the connections
        # between Alameda Island and Oakland, and end at the nodes where
        # population increases and append them to the od file
        # Generate OD data for each node with increased population and append
        # it to the od file
        for _, row in population_change_df.iterrows():
            # Only process rows with positive population difference
            if row['Population_Difference'] > 0:
                for _ in range(row['Population_Difference']):
                    # Generate random origin_nid
                    origin_nid = np.random.choice(origin_ids)
                    # Set the destin_nid to the node_id of the increased
                    # population
                    destin_nid = row['node_id']
                    # Generate random hour and quarter
                    hour = np.random.randint(5, 24)
                    quarter = np.random.randint(0, 5)
                    # Append to od dataframe
                    od_df = od_df.append(
                        {
                            'agent_id': 0,
                            'origin_nid': origin_nid,
                            'destin_nid': destin_nid,
                            'hour': hour,
                            'quarter': quarter,
                        },
                        ignore_index=True,
                    )
        od_df.to_csv('updated_od.csv')
        return od_df


class pyrecodes_residual_demand(TransportationPerformance):
    """
    A class to simulate transportation networks in pyrecodes.

    This class extends the TransportationPerformance abstract base class and
    implements methods to simulate and analyze the performance of transportation
    networks at pyrecodes recovery time steps.
    """

    def __init__(
        self,
        edges_file,
        nodes_file,
        od_pre_file,
        hour_list,
        results_dir,
        capacity_ruleset_script,
        demand_ruleset_script,
        two_way_edges=False,  # noqa: FBT002
    ):
        # Default not save pandana output
        self.tmp_dir = Path.cwd()
        self.save_pandana = False
        # Prepare edges and nodes files
        edges_gdf = gpd.read_file(edges_file)
        if 'length' not in edges_gdf.columns:
            edges_gdf = edges_gdf.to_crs(epsg=6500)
            edges_gdf['length'] = edges_gdf['geometry'].apply(lambda x: x.length)
            edges_gdf = edges_gdf.to_crs(epsg=4326)
        if two_way_edges:
            edges_gdf_copy = edges_gdf.copy()
            edges_gdf_copy['StartNode'] = edges_gdf['EndNode']
            edges_gdf_copy['EndNode'] = edges_gdf['StartNode']
            edges_gdf = pd.concat([edges_gdf, edges_gdf_copy], ignore_index=True)
        edges_gdf = edges_gdf.reset_index()
        edges_gdf = edges_gdf.rename(
            columns={
                'index': 'uniqueid',
                'StartNode': 'start_nid',
                'EndNode': 'end_nid',
                'NumOfLanes': 'lanes',
                'MaxMPH': 'maxspeed',
            }
        )
        # Assume that the capacity for each lane is 1800
        edges_gdf['capacity'] = edges_gdf['lanes'] * 1800
        edges_gdf['normal_capacity'] = edges_gdf['capacity']
        edges_gdf['normal_maxspeed'] = edges_gdf['maxspeed']
        edges_gdf['start_nid'] = edges_gdf['start_nid'].astype(int)
        edges_gdf['end_nid'] = edges_gdf['end_nid'].astype(int)

        nodes_gdf = gpd.read_file(nodes_file)
        nodes_gdf = nodes_gdf.rename(columns={'nodeID': 'node_id'})
        nodes_gdf['y'] = nodes_gdf['geometry'].apply(lambda x: x.y)
        nodes_gdf['x'] = nodes_gdf['geometry'].apply(lambda x: x.x)

        edges_gdf['fft'] = edges_gdf['length'] / edges_gdf['maxspeed'] * METER_PER_SECOND_TO_MILES_PER_HOUR
        edges_gdf['normal_fft'] = (
            edges_gdf['length'] / edges_gdf['normal_maxspeed'] * METER_PER_SECOND_TO_MILES_PER_HOUR
        )
        edges_gdf['t_avg'] = edges_gdf['fft']
        edges_gdf['u'] = edges_gdf['start_nid']
        edges_gdf['v'] = edges_gdf['end_nid']

        # delete geometry columns to save memory however, traffic assignment need to be updated accordingly
        # edges_gdf = edges_gdf.drop(columns=['geometry'])
        # nodes_gdf = nodes_gdf.drop(columns=['geometry'])

        # This edges_df is the initial undamaged network
        self.edges_df = edges_gdf
        self.nodes_df = nodes_gdf

        self.od_pre_file = od_pre_file
        self.initial_r2d_dict = None
        self.hour_list = hour_list
        self.results_dir = results_dir
        self.two_way_edges = two_way_edges

        # import update_edges from capacity_ruleset_script
        module_name = Path(capacity_ruleset_script).stem
        spec = importlib.util.spec_from_file_location(module_name, capacity_ruleset_script)
        capacity_ruleset = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = capacity_ruleset
        spec.loader.exec_module(capacity_ruleset)
        if not hasattr(capacity_ruleset, 'update_edges'):
            msg = f"Function 'update_edges' should exist in {capacity_ruleset_script}."
            raise Exception(msg)  # noqa: TRY002
        self.capacity_ruleset = capacity_ruleset

        # import update_od from demand_ruleset_script
        module_name = Path(demand_ruleset_script).stem
        spec = importlib.util.spec_from_file_location(module_name, demand_ruleset_script)
        demand_ruleset = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = demand_ruleset
        spec.loader.exec_module(demand_ruleset)
        if not hasattr(demand_ruleset, 'update_od'):
            msg = f"Function 'update_od' should exist in {capacity_ruleset_script}."
            raise Exception(msg)  # noqa: TRY002
        self.demand_ruleset = demand_ruleset

        self.simulate_time = 0



    def simulate(
        self,
        r2d_dict
    ):
        """
        Simulate the transportation network performance.

        Args:
            r2d_dict (dict): Dictionary containing the status of all asset at a certain time step.

        Returns
        -------
            pd.DataFrame: DataFrame containing trip information.
        """
        if self.initial_r2d_dict is None:
            od_matrix = pd.read_csv(self.od_pre_file)
            self.initial_od = copy.deepcopy(od_matrix)
            self.initial_r2d_dict = copy.deepcopy(r2d_dict)
        else:
            od_matrix = self.demand_ruleset.update_od(self.initial_od,
                                                      self.nodes_df,
                                                      self.initial_r2d_dict,
                                                      r2d_dict)

        edges_df = self.edges_df.copy()
        edges_df = edges_df.set_index('id')
        edges_df, closed_links = self.capacity_ruleset.update_edges(edges_df, r2d_dict)

        edges_df['fft'] = edges_df['length'] / edges_df['maxspeed'] * METER_PER_SECOND_TO_MILES_PER_HOUR # Nikola: Labeled the number.
        edges_df['normal_fft'] = (
            edges_df['length'] / edges_df['normal_maxspeed'] * METER_PER_SECOND_TO_MILES_PER_HOUR
        )
        edges_df['t_avg'] = edges_df['fft']

        edges_df = edges_df.sort_values(by='fft', ascending=False).drop_duplicates(
            subset=['start_nid', 'end_nid'], keep='first'
        )

        edges_df['edge_str'] = (
            edges_df['start_nid'].astype('str')
            + '-'
            + edges_df['end_nid'].astype('str')
        )
        edges_df = edges_df.reset_index().set_index('edge_str')


        self.simulate_time += 1
        trip_info_df = self.assignment(
            edges_df = edges_df,
            nodes_df=self.nodes_df,
            od_all=od_matrix,
            simulation_outputs=self.results_dir,
            hour_list=self.hour_list,
            quarter_list=[0, 1, 2, 3, 4, 5],
            closure_hours=self.hour_list,
            closed_links=closed_links,
            two_way_edges=False, # The edges has been duplicated to consider two way edges, so no need to have two way edges when constructing pandana net
            save_edge_vol = False
        )
        return trip_info_df  # noqa: RET504


    # def get_graph_network(self,
    #                       det_file_path: str,
    #                       output_files: Optional[List[str]] = None,
    #                       save_additional_attributes:
    #                           Literal['', 'residual_demand'] = ''
    #                       ) -> Tuple[Dict, Dict]:
    #     """
    #     Create a graph network from inventory data .

    #     This function processes inventory files containing road and structural
    #     data, constructs a graph network with nodes and edges, and optionally
    #     saves additional attributes such as residual demand. The node and edge
    #     features are saved to specified output files.

    #     Args__
    #         det_file_path (str): The path to the deterministic result JSON
    #         output_files (Optional[List[str]]): A list of file paths where the
    #             node and edge features will be saved. The first file in the
    #             list is used for edges and the second for nodes.
    #         save_additional_attributes (Literal['', 'residual_demand']):
    #             A flag indicating whether to save additional attributes.
    #             The only supported additional attribute is 'residual_demand'.

    #     Returns__
    #         Tuple[Dict, Dict]: A tuple containing two dictionaries:
    #             - The first dictionary contains the edge features.
    #             - The second dictionary contains the node features.

    #     Example__
    #         >>> det_file_path = 'path/to/Results_det.json'
    #         >>> output_files = ['edges.csv', 'nodes.csv']
    #         >>> save_additional_attributes = 'residual_demand'
    #         >>> edges, nodes = get_graph_network(det_file_path,
    #                                              output_files,
    #                                              save_additional_attributes)
    #         >>> print(edges)
    #         >>> print(nodes)
    #     """
    #     # if output_files is None:
    #     #     self.graph_network['output_files'] = ['edges.csv', 'nodes.csv']

    #     def create_circle_from_lat_lon(lat, lon, radius_ft, num_points=100):
    #         """
    #         Create a circle polygon from latitude and longitude.

    #         Args__
    #             lat (float): Latitude of the center.
    #             lon (float): Longitude of the center.
    #             radius_ft (float): Radius of the circle in feet.
    #             num_points (int): Number of points to approximate the circle.

    #         Returns__
    #             Polygon: A Shapely polygon representing the circle.
    #         """
    #         # Earth's radius in kilometers
    #         R_EARTH_FT = 20925721.784777

    #         # Convert radius from kilometers to radians
    #         radius_rad = radius_ft / R_EARTH_FT

    #         # Convert latitude and longitude to radians
    #         lat_rad = np.radians(lat)
    #         lon_rad = np.radians(lon)

    #         # Generate points around the circle
    #         angle = np.linspace(0, 2 * np.pi, num_points)
    #         lat_points = lat_rad + radius_rad * np.cos(angle)
    #         lon_points = lon_rad + radius_rad * np.sin(angle)

    #         # Convert radians back to degrees
    #         lat_points_deg = np.degrees(lat_points)
    #         lon_points_deg = np.degrees(lon_points)

    #         # Create a polygon from the points
    #         points = list(zip(lon_points_deg, lat_points_deg))
    #         return Polygon(points)

    #     def parse_element_geometries_from_geojson(
    #             det_file: str,
    #             save_additional_attributes: str
    #     ) -> Tuple[List[Dict], Tuple[List[LineString], List[Dict]]]:
    #         """
    #         Parse geometries from R2D deterministic result json.

    #         This function reads json files specified in `output_files`. It
    #         extracts and parses `LineString` geometries from files that contain
    #         "road" in their name. For other files, it accumulates point
    #         features.

    #         Args__
    #             det_file (str): Path to the R2D deterministic result Json.

    #         Returns__
    #             tuple: A tuple containing two elements:
    #                 - ptdata (list of dict): List of point features parsed from
    #                     GeoJSON files for bridges and tunnels
    #                 - road_data (tuple): A tuple containing:
    #                     - road_polys (list of LineString): List of `LineString`
    #                         objects created from the road geometries in GeoJSON
    #                         files that contain "road" in their name.
    #                     - road_features (list of dict): List of road features
    #                         as dictionaries from GeoJSON files that contain
    #                         "roads" in their name.

    #         Raises__
    #             FileNotFoundError: If any of the specified files in
    #                 `output_files` do not exist.
    #             json.JSONDecodeError: If a file cannot be parsed as valid JSON.
    #         """
    #         ptdata = {}
    #         with open(det_file, "r", encoding="utf-8") as file:
    #             # Read the JSON file:
    #             temp = json.load(file)
    #             if 'TransportationNetwork' not in temp:
    #                 raise KeyError(
    #                     'The deterministic result JSON file does not contain TransportationNetwork')
    #             temp = temp['TransportationNetwork']
    #             # If the file contains road information:
    #             if 'Roadway' in temp:
    #                 # Extract road features:
    #                 road_features = temp['Roadway']
    #                 # Read road polygons, add asset type information to
    #                 # road features and, if required, parse existing road
    #                 # attributes to infer information required for network
    #                 # analysis:
    #                 road_polys = {}
    #                 for AIM_ID, item in road_features.items():
    #                     road_polys.update({AIM_ID: loads(item["GeneralInformation"]["geometry"])})
    #                     # road_features[ind]['properties']['asset_type'] = \
    #                     #     'road'
    #                     if save_additional_attributes:
    #                         # Access properties for element at index ind:
    #                         properties = item['GeneralInformation']
    #                         # Get MTFCC value:
    #                         mtfcc = properties['MTFCC']
    #                         # Update road features for the indexed element
    #                         # with number of lanes, maximum speed, and
    #                         # road capacity:
    #                         properties.update({
    #                             'lanes':
    #                                 self.attribute_maps['lanes'][mtfcc],
    #                             'maxspeed':
    #                                 self.attribute_maps['speed'][mtfcc],
    #                             'capacity':
    #                                 self.attribute_maps['capacity'][
    #                                     properties['lanes']]
    #                         })
    #             if 'Bridge' in temp:
    #                 ptdata['Bridge'] = temp['Bridge']
    #                 # for feature in temp["features"]:
    #                 #     feature['properties']['asset_type'] = asset_type
    #                 # ptdata += temp["features"]
    #             if 'Tunnel' in temp:
    #                 ptdata['Tunnel'] = temp['Tunnel']

    #         return ptdata, (road_polys, road_features)

    #     def find_intersections(lines: List[LineString]) -> Set[Point]:
    #         """
    #         Find intersection points between pairs of LineString geometries.

    #         This function takes a list of `LineString` objects and identifies
    #         points where any two lines intersect. The intersections are
    #         returned as a set of `Point` objects.

    #         Args__
    #             lines (List[LineString]): A list of `LineString` objects. The
    #             function computes intersections between each pair of
    #             `LineString` objects in this list.

    #         Returns__
    #             Set[Point]: A set of `Point` objects representing the
    #             intersection points between the `LineString` objects. If
    #             multiple intersections occur at the same location, it will
    #             only be included once in the set.

    #         Example__
    #             >>> from shapely.geometry import LineString
    #             >>> line1 = LineString([(0, 0), (1, 1)])
    #             >>> line2 = LineString([(0, 1), (1, 0)])
    #             >>> find_intersections([line1, line2])
    #             {<shapely.geometry.point.Point object at 0x...>}

    #         Notes__
    #             - The function assumes that all input geometries are valid
    #             `LineString`
    #                 objects.
    #             - The resulting set may be empty if no intersections are found.

    #         Raises__
    #             TypeError: If any element in `lines` is not a `LineString`
    #             object.
    #         """
    #         intersections = set()
    #         for i, line1 in enumerate(lines):
    #             for line2 in lines[i + 1:]:
    #                 if line1.intersects(line2):
    #                     inter_points = line1.intersection(line2)
    #                     if inter_points.geom_type == "Point":
    #                         intersections.add(inter_points)
    #                     elif inter_points.geom_type == "MultiPoint":
    #                         intersections.update(inter_points.geoms)
    #         return intersections

    #     def cut_lines_at_intersections(lines: List[LineString],
    #                                    line_features: List[Dict],
    #                                    intersections: List[Point]
    #                                    ) -> List[LineString]:
    #         """
    #         Cut LineStrings at intersection points & return resulting segments.

    #         This function takes a list of `LineString` objects and a list of
    #         `Point` objects representing intersection points. For each
    #         `LineString`, it splits the line at each intersection point. The
    #         resulting segments are collected and returned.

    #         Args__
    #             lines (List[LineString]): A list of `LineString` objects to be
    #                 cut at the intersection points.
    #             line_features (List[Dict]): List of features for the
    #                 `LineString` objects in lines.
    #             intersections (List[Point]): A list of `Point` objects where
    #                 the lines are intersected and split.

    #         Returns__
    #             List[LineString]: A list of `LineString` objects resulting from
    #                               cutting the original lines at the
    #                               intersection points.

    #         Notes__
    #             - The `split` function from `shapely.ops` is used to perform
    #                 the cutting of lines at intersection points.
    #             - The function handles cases where splitting results in a
    #                 `GeometryCollection` by extracting only `LineString`
    #                 geometries.

    #         Example__
    #             >>> from shapely.geometry import LineString, Point
    #             >>> from shapely.ops import split
    #             >>> lines = [
    #             ...     LineString([(0, 0), (2, 2)]),
    #             ...     LineString([(2, 0), (0, 2)])
    #             ... ]
    #             >>> intersections = [
    #             ...     Point(1, 1)
    #             ... ]
    #             >>> cut_lines_at_intersections(lines, intersections)
    #             [<shapely.geometry.linestring.LineString object at 0x...>,
    #              <shapely.geometry.linestring.LineString object at 0x...>]
    #         """
    #         new_lines = []
    #         new_line_features = []

    #         for ind_line, line in enumerate(lines):
    #             segments = [line]  # Start with the original line
    #             for point in intersections:
    #                 new_segments = []
    #                 features = []
    #                 for segment in segments:
    #                     if segment.intersects(point):
    #                         split_result = split(segment, point)
    #                         if split_result.geom_type == "GeometryCollection":
    #                             new_segments.extend(
    #                                 geom
    #                                 for geom in split_result.geoms
    #                                 if geom.geom_type == "LineString"
    #                             )
    #                             features.extend([copy.deepcopy(
    #                                 line_features[ind_line])
    #                                 for _ in range(
    #                                 len(
    #                                     split_result.geoms
    #                                 ))])
    #                         elif split_result.geom_type == "LineString":
    #                             segments.append(split_result)
    #                             features.append(line_features[ind_line])
    #                     else:
    #                         new_segments.append(segment)
    #                         features.append(line_features[ind_line])
    #                 segments = new_segments

    #             # Add remaining segments that were not intersected by any
    #             # points:
    #             new_lines.extend(segments)
    #             new_line_features.extend(features)

    #         return (new_lines, new_line_features)

    #     def save_cut_lines_and_intersections(lines: List[LineString],
    #                                          points: List[Point]) -> None:
    #         """
    #         Save LineString and Point objects to separate GeoJSON files.

    #         This function converts lists of `LineString` and `Point` objects to
    #         GeoJSON format and saves them to separate files. The `LineString`
    #         objects are saved to "lines.geojson", and the `Point` objects are
    #         saved to "points.geojson".

    #         Args__
    #             lines (List[LineString]): A list of `LineString` objects to be
    #                                             saved in GeoJSON format.
    #             intersections (List[Point]): A list of `Point` objects to be
    #                                             saved in GeoJSON format.

    #         Returns__
    #             None: This function does not return any value. It writes
    #                     GeoJSON data to files.

    #         Notes__
    #             - The function uses the `mapping` function from
    #                 `shapely.geometry` to convert geometries to GeoJSON format.
    #             - Two separate GeoJSON files are created: one for lines and one
    #                 for points.
    #             - The output files are named "lines.geojson" and
    #                 "points.geojson" respectively.

    #         Example__
    #             >>> from shapely.geometry import LineString, Point
    #             >>> lines = [
    #             ...     LineString([(0, 0), (1, 1)]),
    #             ...     LineString([(1, 1), (2, 2)])
    #             ... ]
    #             >>> points = [
    #             ...     Point(0.5, 0.5),
    #             ...     Point(1.5, 1.5)
    #             ... ]
    #             >>> save_cut_lines_and_intersections(lines, points)
    #             # This will create "lines.geojson" and "points.geojson" files
    #                 with the corresponding GeoJSON data.
    #         """
    #         # Convert LineString objects to GeoJSON format
    #         features = []
    #         for line in lines:
    #             features.append(
    #                 {"type": "Feature", "geometry": mapping(
    #                     line), "properties": {}}
    #             )

    #         # Create a GeoJSON FeatureCollection
    #         geojson = {"type": "FeatureCollection", "features": features}

    #         # Save the GeoJSON to a file
    #         with open("lines.geojson", "w", encoding="utf-8") as file:
    #             json.dump(geojson, file, indent=2)

    #         # Convert Point objects to GeoJSON format
    #         features = []
    #         for point in points:
    #             features.append(
    #                 {"type": "Feature", "geometry": mapping(
    #                     point), "properties": {}}
    #             )

    #         # Create a GeoJSON FeatureCollection
    #         geojson = {"type": "FeatureCollection", "features": features}

    #         # Save the GeoJSON to a file
    #         with open("points.geojson", "w", encoding="utf-8") as file:
    #             json.dump(geojson, file, indent=2)

    #     def find_repeated_line_pairs(lines: List[LineString]) -> Set[Tuple]:
    #         """
    #         Find and groups indices of repeated LineString objects from a list.

    #         This function processes a list of `LineString` objects to identify
    #         and group all unique index pairs where LineString objects are
    #         repeated. The function converts each `LineString` to its
    #         Well-Known Text (WKT) representation to identify duplicates.

    #         Args__
    #             lines (List[LineString]): A list of `LineString` objects to be
    #                 analyzed for duplicates.

    #         Returns__
    #             Set[Tuple]: A set of tuples, where each tuple contains indices
    #                 for LineString objects that are repeated.

    #         Raises__
    #             TypeError: If any element in the `lines` list is not an
    #                 instance of `LineString`.

    #         Example__
    #             >>> from shapely.geometry import LineString
    #             >>> lines = [
    #             ...     LineString([(0, 0), (1, 1)]),
    #             ...     LineString([(0, 0), (1, 1)]),
    #             ...     LineString([(1, 1), (2, 2)]),
    #             ...     LineString([(0, 0), (1, 1)]),
    #             ...     LineString([(1, 1), (2, 2)])
    #             ... ]
    #             >>> find_repeated_line_pairs(lines)
    #             [{0, 1, 3}, {2, 4}]
    #         """
    #         line_indices = defaultdict(list)

    #         for id, line in lines.items():
    #             if not isinstance(line, LineString):
    #                 raise TypeError(
    #                     'All elements in the input list must be LineString'
    #                     ' objects.')

    #             # Convert LineString to its WKT representation to use as a
    #             # unique identifier:
    #             line_wkt = line.wkt
    #             line_indices[line_wkt].append(id)

    #         repeated_pairs = set()
    #         for indices in line_indices.values():
    #             if len(indices) > 1:
    #                 # Create pairs of all indices for the repeated LineString
    #                 for i, _ in enumerate(indices):
    #                     for j in range(i + 1, len(indices)):
    #                         repeated_pairs.add((indices[i], indices[j]))

    #         repeated_pairs = list(repeated_pairs)
    #         ind_matched = []
    #         repeated_polys = []
    #         for index_p1, pair1 in enumerate(repeated_pairs):
    #             pt1 = set(pair1)
    #             for index_p2, pair2 in enumerate(repeated_pairs[index_p1+1:]):
    #                 if (index_p1 + index_p2 + 1) not in ind_matched:
    #                     pt2 = set(pair2)
    #                     if bool(pt1 & pt2):
    #                         pt1 |= pt2
    #                         ind_matched.append(index_p1 + index_p2 + 1)
    #             if pt1 not in repeated_polys and index_p1 not in ind_matched:
    #                 repeated_polys.append(pt1)

    #         return repeated_polys

    #     def match_edges_to_points(ptdata: List[Dict],
    #                               road_polys: List[LineString],
    #                               road_features: List[Dict]
    #                               ) -> List[List[int]]:
    #         """
    #         Match points to closest road polylines based on name similarity.

    #         This function takes a list of points and a list of road polylines.
    #         For each point, it searches for intersecting road polylines within
    #         a specified radius and calculates the similarity between the
    #         point's associated facility name and the road's name. It returns a
    #         list of lists where each sublist contains indices of the road
    #         polylines that best match the point based on the similarity score.

    #         Args__
    #             ptdata (List[Dict[str, Any]]): A list of dictionaries where
    #                 each dictionary represents a point with its geometry and
    #                 properties. The 'geometry' key should contain 'coordinates'
    #                 , and the 'properties' key should contain 'tunnel_name' or
    #                 'facility_carried'.
    #             road_polys (List[LineString]): A list of `LineString` objects
    #                 representing road polylines.

    #         Returns__
    #             List[List[int]]: A list of lists where each sublist contains
    #                 the indices of road polylines that have the highest textual
    #                 similarity to the point's facility name. If no similarity
    #                 is found, the sublist is empty.

    #         Notes__
    #             - The function uses a search radius of 100 feet to find
    #                 intersecting road polylines.
    #             - TF-IDF vectors are used to compute the textual similarity
    #                 between the facility names and road names.
    #             - Cosine similarity is used to determine the best matches.

    #         Example__
    #             >>> from shapely.geometry import Point, LineString
    #             >>> ptdata = [
    #             ...     {"geometry": {"coordinates": [1.0, 1.0]},
    #                      "properties": {"tunnel_name": "Tunnel A"}},
    #             ...     {"geometry": {"coordinates": [2.0, 2.0]},
    #                      "properties": {"facility_carried": "Road B"}}
    #             ... ]
    #             >>> road_polys = [
    #             ...     LineString([(0, 0), (2, 2)]),
    #             ...     LineString([(1, 1), (3, 3)])
    #             ... ]
    #             >>> match_edges_to_points(ptdata, road_polys)
    #             [[0], [1]]
    #         """
    #         edge_matches = []
    #         for ptdata_type, type_data in ptdata.items():
    #             for AIM_ID, point in type_data.items():
    #                 lon = point["GeneralInformation"]["location"]["longitude"]
    #                 lat = point["GeneralInformation"]["location"]["latitude"]
    #                 search_radius = create_circle_from_lat_lon(lat, lon, 100)
    #                 # Check for intersections:
    #                 intersecting_polylines = [
    #                     AIM_ID
    #                     for (AIM_ID, poly) in road_polys.items()
    #                     if poly.intersects(search_radius)
    #                 ]
    #                 properties = point["GeneralInformation"]
    #                 if ptdata_type == "Tunnel":
    #                     facility = properties.get("tunnel_name", "")
    #                 elif ptdata_type == "Bridge":
    #                     # facility = properties["facility_carried"]
    #                     facility = properties.get("facility_carried", "")
    #                 max_similarity = 0
    #                 similarities = {}
    #                 for AIM_ID in intersecting_polylines:
    #                     roadway = road_features[AIM_ID]["GeneralInformation"].get("NAME", None)
    #                     if roadway:
    #                         # Create TF-IDF vectors:
    #                         vectorizer = TfidfVectorizer()
    #                         tfidf_matrix = vectorizer.fit_transform(
    #                             [facility, roadway.lower()]
    #                         )

    #                         # Calculate cosine similarity:
    #                         similarity = cosine_similarity(
    #                             tfidf_matrix[0:1], tfidf_matrix[1:2]
    #                         )
    #                     else:
    #                         similarity = -1
    #                     similarities.update({AIM_ID:similarity})
    #                     if similarity > max_similarity:
    #                         max_similarity = similarity
    #                 if max_similarity == 0:
    #                     max_similarity = -1
    #                 indices_of_max = [
    #                     intersecting_polylines[index]
    #                     for index, value in (similarities).items()
    #                     if value == max_similarity
    #                 ]
    #                 edge_matches.append(indices_of_max)

    #         return edge_matches

    #     def merge_brtn_features(ptdata: List[Dict],
    #                             road_features_brtn: List[Dict],
    #                             edge_matches: List[List],
    #                             save_additional_attributes: str) -> List[Dict]:
    #         """
    #         Merge bridge/tunnel features to road features using edge matches.

    #         This function updates road features with additional attributes
    #         derived from bridge or tunnel point data. It uses edge matches to
    #         determine how to distribute lane and capacity information among
    #         road features.

    #         Args__
    #             ptdata (List[Dict]): A list of dictionaries where each
    #                 dictionary contains properties of bridge or tunnel
    #                 features. Each dictionary should have 'asset_type',
    #                 'traffic_lanes_on', 'structure_number',
    #                 'total_number_of_lanes', and 'tunnel_number' as keys.
    #             road_features_brtn (List[Dict]): A list of dictionaries
    #                 representing road features that will be updated. Each
    #                 dictionary should have a 'properties' key where attributes
    #                 are stored.
    #             edge_matches (List[List[int]]): A list of lists, where each
    #                 sublist contains indices that correspond to
    #                 `road_features_brtn` and represent which features should be
    #                 updated together.
    #             save_additional_attributes (str): A flag indicating whether to
    #                 save additional attributes like 'lanes' and 'capacity'. If
    #                 non-empty, additional attributes will be saved.

    #         Returns__
    #             List[Dict]: The updated list of road features with merged
    #             attributes.

    #         Example__
    #             >>> ptdata = [
    #             ...     {'properties': {'asset_type': 'bridge',
    #                                     'traffic_lanes_on': 4,
    #                                     'structure_number': '12345'}},
    #             ...     {'properties': {'asset_type': 'tunnel',
    #                                     'total_number_of_lanes': 6,
    #                                     'tunnel_number': '67890'}}
    #             ... ]
    #             # List of empty
    #             >>> road_features_brtn = [{} for _ in range(4)]
    #                 dictionaries for demonstration
    #             >>> edge_matches = [[0, 1], [2, 3]]
    #             >>> save_additional_attributes = 'yes'
    #             >>> updated_features = merge_brtn_features(
    #                 ptdata,
    #                 road_features_brtn,
    #                 edge_matches,
    #                 save_additional_attributes)
    #             >>> print(updated_features)
    #         """
    #         poly_index = 0
    #         for item_index, edge_indices in enumerate(edge_matches):
    #             nitems = len(edge_indices)
    #             features = ptdata[item_index]['properties']
    #             asset_type = features['asset_type']
    #             if asset_type == 'bridge':
    #                 total_nlanes = features['traffic_lanes_on']
    #                 struct_no = features['structure_number']
    #             else:
    #                 total_nlanes = features['total_number_of_lanes']
    #                 struct_no = features['tunnel_number']

    #             lanes_per_item = round(int(total_nlanes)/nitems)

    #             for index in range(poly_index, poly_index + nitems):
    #                 properties = road_features_brtn[index]['properties']
    #                 properties['asset_type'] = asset_type
    #                 properties['OID'] = struct_no
    #                 if save_additional_attributes:
    #                     properties['lanes'] = lanes_per_item
    #                     properties['capacity'] = calculate_road_capacity(
    #                         lanes_per_item)

    #             poly_index += nitems
    #         return road_features_brtn

    #     def get_nodes_edges(lines: List[LineString],
    #                         length_unit: Literal['ft', 'm'] = 'ft'
    #                         ) -> Tuple[Dict, Dict]:
    #         """
    #         Extract nodes and edges from a list of LineString objects.

    #         This function processes a list of `LineString` geometries to
    #         generate nodes and edges. Nodes are defined by their unique
    #         coordinates, and edges are represented by their start and end
    #         nodes, length, and geometry.

    #         Args__
    #             lines (List[LineString]): A list of `LineString` objects
    #                 representing road segments.
    #             length_unit (Literal['ft', 'm']): The unit of length for the
    #                 edge distances. Defaults to 'ft'. Acceptable values are
    #                 'ft' for feet and 'm' for meters.

    #         Returns__
    #             Tuple[Dict[int, Dict[str, float]], Dict[int, Dict[str, Any]]]:
    #                 - A dictionary where keys are node IDs and values are
    #                     dictionaries with node attributes:
    #                     - 'lon': Longitude of the node.
    #                     - 'lat': Latitude of the node.
    #                     - 'geometry': WKT representation of the node.
    #                 - A dictionary where keys are edge IDs and values are
    #                     dictionaries with edge attributes:
    #                     - 'start_nid': ID of the start node.
    #                     - 'end_nid': ID of the end node.
    #                     - 'length': Length of the edge in the specified unit.
    #                     - 'geometry': WKT representation of the edge.

    #         Raises__
    #             TypeError: If any element in the `lines` list is not an
    #                 instance of `LineString`.

    #         Example__
    #             >>> from shapely.geometry import LineString
    #             >>> lines = [
    #             ...     LineString([(0, 0), (1, 1)]),
    #             ...     LineString([(1, 1), (2, 2)])
    #             ... ]
    #             >>> nodes, edges = get_nodes_edges(lines, length_unit='m')
    #             >>> print(nodes)
    #             >>> print(edges)
    #         """
    #         node_list = []
    #         edges = {}
    #         node_counter = 0
    #         for line_counter, line in enumerate(lines):
    #             # Ensure the object is a LineString
    #             if not isinstance(line, LineString):
    #                 raise TypeError(
    #                     "All elements in the list must be LineString objects.")

    #             # Extract coordinates
    #             coords = list(line.coords)
    #             ncoord_pairs = len(coords)
    #             if ncoord_pairs > 0:
    #                 start_node_coord = coords[0]
    #                 end_node_coord = coords[-1]

    #                 if start_node_coord not in node_list:
    #                     node_list.append(start_node_coord)
    #                     start_nid = node_counter
    #                     node_counter += 1
    #                 else:
    #                     start_nid = node_list.index(start_node_coord)

    #                 if end_node_coord not in node_list:
    #                     node_list.append(end_node_coord)
    #                     end_nid = node_counter
    #                     node_counter += 1
    #                 else:
    #                     end_nid = node_list.index(end_node_coord)

    #                 length = 0
    #                 (lon, lat) = line.coords.xy
    #                 for pair_no in range(ncoord_pairs - 1):
    #                     length += haversine_dist([lat[pair_no], lon[pair_no]],
    #                                              [lat[pair_no+1],
    #                                               lon[pair_no+1]])
    #                 if length_unit == 'm':
    #                     length = 0.3048*length

    #                 edges[line_counter] = {'start_nid': start_nid,
    #                                        'end_nid': end_nid,
    #                                        'length': length,
    #                                        'geometry': line.wkt}

    #             nodes = {}
    #             for node_id, node_coords in enumerate(node_list):
    #                 nodes[node_id] = {'lon': node_coords[0],
    #                                   'lat': node_coords[1],
    #                                   'geometry': 'POINT ('
    #                                               f'{node_coords[0]:.7f} '
    #                                               f'{node_coords[1]:.7f})'}

    #         return (nodes, edges)

    #     def get_node_edge_features(updated_road_polys: List[LineString],
    #                                updated_road_features: List[Dict],
    #                                output_files: List[str]
    #                                ) -> Tuple[Dict, Dict]:
    #         """
    #         Extract/write node and edge features from updated road polygons.

    #         This function processes road polygon data to generate nodes and
    #         edges, then writes the extracted features to specified output
    #         files.

    #         Args__
    #             updated_road_polys (List[LineString]): A list of LineString
    #                 objects representing updated road polygons.
    #             updated_road_features (List[Dict]): A list of dictionaries
    #                 containing feature properties for each road segment.
    #             output_files (List[str]): A list of two file paths where the
    #                 first path is for edge data and the second for node data.

    #         Returns__
    #             Tuple[Dict, Dict]: A tuple containing two dictionaries:
    #                 - The first dictionary contains edge data.
    #                 - The second dictionary contains node data.

    #         Raises__
    #             TypeError: If any input is not of the expected type.

    #         Example__
    #             >>> from shapely.geometry import LineString
    #             >>> road_polys = [LineString([(0, 0), (1, 1)]),
    #                               LineString([(1, 1), (2, 2)])]
    #             >>> road_features = [{'properties': {'OID': 1,
    #                                                  'asset_type': 'road',
    #                                                  'lanes': 2,
    #                                                  'capacity': 2000,
    #                                                  'maxspeed': 30}}]
    #             >>> output_files = ['edges.csv', 'nodes.csv']
    #             >>> get_node_edge_features(road_polys,
    #                                        road_features,
    #                                        output_files)
    #         """
    #         (nodes, edges) = get_nodes_edges(
    #             updated_road_polys, length_unit='m')

    #         with open(output_files[1], 'w', encoding="utf-8") as nodes_file:
    #             nodes_file.write('node_id, lon, lat, geometry\n')
    #             for key in nodes:
    #                 nodes_file.write(f'{key}, {nodes[key]["lon"]}, '
    #                                  f'{nodes[key]["lat"]}, '
    #                                  f'{nodes[key]["geometry"]}\n')

    #         with open(output_files[0], 'w', encoding="utf-8") as edge_file:
    #             edge_file.write('uniqueid, start_nid, end_nid, osmid, length, '
    #                             'type, lanes, maxspeed, capacity, fft, '
    #                             'geometry\n')

    #             for key in edges:
    #                 features = updated_road_features[key]['properties']
    #                 edges[key]['osmid'] = features['OID']
    #                 edges[key]['type'] = features['asset_type']
    #                 edges[key]['lanes'] = features['lanes']
    #                 edges[key]['capacity'] = features['capacity']
    #                 maxspeed = features['maxspeed']
    #                 edges[key]['maxspeed'] = maxspeed
    #                 free_flow_time = edges[key]['length'] / \
    #                     (maxspeed*1609.34/3600)
    #                 edges[key]['fft'] = free_flow_time
    #                 edge_file.write(f'{key}, {edges[key]["start_nid"]}, '
    #                                 f'{edges[key]["end_nid"]}, '
    #                                 f'{edges[key]["osmid"]}, '
    #                                 f'{edges[key]["length"]}, '
    #                                 f'{edges[key]["type"]}, '
    #                                 f'{edges[key]["lanes"]}, {maxspeed}, '
    #                                 f'{edges[key]["capacity"]}, '
    #                                 f'{free_flow_time}, '
    #                                 f'{edges[key]["geometry"]}\n')

    #         return (edges, nodes)

    #     print('Getting graph network for elements in '
    #           f'{det_file_path}...')

    #     # Read inventory data:
    #     ptdata, (road_polys, road_features) = \
    #         parse_element_geometries_from_geojson(det_file_path,
    #                                               save_additional_attributes=save_additional_attributes)

    #     # Find edges that match bridges and tunnels:
    #     edge_matches = match_edges_to_points(ptdata, road_polys, road_features)

    #     # Get the indices for bridges and tunnels:
    #     brtn_poly_idx = [item for sublist in edge_matches for item in sublist]

    #     # Detect repeated edges and save their indices:
    #     repeated_edges = find_repeated_line_pairs(road_polys)

    #     edges_remove = []
    #     for edge_set in repeated_edges:
    #         bridge_poly = set(brtn_poly_idx)
    #         if edge_set & bridge_poly:
    #             remove = list(edge_set - bridge_poly)
    #         else:
    #             temp = list(edge_set)
    #             remove = temp[1:].copy()
    #         edges_remove.extend(remove)

    #     # Save polygons that are not bridge or tunnel edges or marked for
    #     # removal in road polygons:
    #     road_polys_local = [poly for (ind, poly) in road_polys.items() if
    #                         ind not in brtn_poly_idx + edges_remove]
    #     road_features_local = [feature for (ind, feature) in
    #                            road_features.items()
    #                            if ind not in brtn_poly_idx + edges_remove]

    #     # Save polygons that are not bridge or tunnel edges:
    #     road_polys_brtn = [poly for (ind, poly) in enumerate(road_polys)
    #                        if ind in brtn_poly_idx]
    #     road_features_brtn = [feature for (ind, feature)
    #                           in enumerate(road_features)
    #                           if ind in brtn_poly_idx]
    #     road_features_brtn = merge_brtn_features(ptdata,
    #                                              road_features_brtn,
    #                                              edge_matches,
    #                                              save_additional_attributes)

    #     # Compute the intersections of road polygons:
    #     intersections = find_intersections(road_polys_local)

    #     # Cut road polygons at intersection points:
    #     cut_lines, cut_features = cut_lines_at_intersections(
    #         road_polys_local,
    #         road_features_local,
    #         intersections)
    #     # Come back and update cut_lines_at_intersections to not intersect
    #     # lines within a certain diameter of a bridge point

    #     # Combine all polygons and their features:
    #     updated_road_polys = cut_lines + road_polys_brtn
    #     updated_road_features = cut_features + road_features_brtn

    #     # Save created polygons (for debugging only)
    #     # save_cut_lines_and_intersections(updated_road_polys, intersections)

    #     # Get nodes and edges of the final set of road polygons:
    #     (edges, nodes) = get_node_edge_features(updated_road_polys,
    #                                             updated_road_features,
    #                                             output_files)
    #     self.graph_network['edges'] = edges
    #     self.graph_network['nodes'] = nodes

    #     print('Edges and nodes of the graph network are saved in '
    #           f'{", ".join(output_files)}')
