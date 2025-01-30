import pandas as pd
import geopandas as gpd
import warnings
import numpy as np

# Extract the building information from the det file and convert it to a pandas dataframe
def extract_building_from_det(det):
            # Extract the required information and convert it to a pandas dataframe
            extracted_data = []

            for aim_id, info in det['Buildings']['Building'].items():
                general_info = info.get('GeneralInformation', {})
                extracted_data.append({
                    'AIM_id': aim_id,
                    'Latitude': general_info.get('Latitude'),
                    'Longitude': general_info.get('Longitude'),
                    'Population': general_info.get('Population'),
                    'PopulationRatio': general_info.get('PopulationRatio')
                })
            extracted_df = pd.DataFrame(extracted_data)
            return gpd.GeoDataFrame(extracted_df, geometry=gpd.points_from_xy(extracted_df.Longitude, extracted_df.Latitude), crs='epsg:4326')
# Aggregate the population in buildings to the closest road network node
def closest_neighbour(building_df, nodes_df):
    # Nikola: I think there is an issue with this method. I have multiple nodes and one building in the system and the population of the one building (which is in one of the nodes) is assigned to all nodes. So the sum of the population in nodes is multiple times higher than the actual population in the system. I assume the population from one building should only be linked to one (closest) node, not to multiple nodes.
    # Find the nearest road network node to each building
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        merged_df = building_df.sjoin_nearest(nodes_df, how = 'left')
        # merged_df = nodes_df.sjoin_nearest(building_df, how = 'left')
    merged_df = merged_df.drop(columns=['AIM_id', 'Latitude', 'Longitude', 'index_right'])
    merged_df = merged_df.fillna(0)
    merged_df['Population'] = merged_df['Population'] * merged_df['PopulationRatio']

    # Aggregate the population of the neareast buildings to the road network node
    return merged_df.groupby('node_id').agg({'x': 'first', 'y': 'first', 'geometry': 'first', 'Population': 'sum'}).reset_index()
# Function to add the population information to the nodes file
def find_population(nodes, det):
    # Extract the building information from the det file and convert it to a pandas dataframe
    building_df = extract_building_from_det(det)
    # Aggregate the population in buildings to the closest road network node
    updated_nodes_df = closest_neighbour(building_df, nodes)

    return updated_nodes_df  # noqa: RET504


def update_od(initial_od, nodes_df, initial_r2d_dict, new_r2d_dict):
    trips_starting_at_nodes = initial_od.reset_index()[['origin_nid', 'index']].groupby(
        'origin_nid').agg(list).to_dict()['index']
    trips_ending_at_nodes = initial_od.reset_index()[['destin_nid', 'index']].groupby(
        'destin_nid').agg(list).to_dict()['index']
    # old population at each node
    old_population = find_population(nodes_df, initial_r2d_dict)
    # new population at each node
    new_population = find_population(nodes_df, new_r2d_dict)
    population_change = new_population['Population'] - old_population['Population']
    # population change percentage at each node
    trips_index_set = set()
    for i in old_population.index:
        node_id = old_population.loc[i, 'node_id']
        # The population did not change, the OD starting and ending at this node does not change
        if population_change[i] == 0:
            trips_index_set = trips_index_set.union(set(trips_starting_at_nodes.get(node_id, [])))
            trips_index_set = trips_index_set.union(set(trips_ending_at_nodes.get(node_id, [])))
        # If the population changed and if the original OD starting and ending at this node is zero,
        # Generate new OD starting and ending at this node. This is considered impossible in this
        # implementation as new population can only be generated at nodes with non-zero pre-event population
        elif old_population.loc[i, 'Population'] == 0:
            print(f'Warning: New population generated at node {node_id}, which had zero pre-event population')
        # If the population changed and if the original OD starting and ending at this node is not zero,
        # Modify the trips starting and ending at this node according to the population change percentage
        else:
            change_percentage = population_change[i] / old_population.loc[i, 'Population']
            origin_trips = trips_starting_at_nodes.get(node_id, [])
            origin_trips = np.random.choice(origin_trips, int(len(origin_trips) * (1+change_percentage)), replace=False)
            destin_trips = trips_ending_at_nodes.get(node_id, [])
            destin_trips = np.random.choice(destin_trips, int(len(destin_trips) * (1+change_percentage)), replace=False)
            trips_index_set = trips_index_set.union(set(origin_trips)).union(set(destin_trips))
    trips_index_set = sorted(trips_index_set)
    return initial_od.loc[trips_index_set, :]