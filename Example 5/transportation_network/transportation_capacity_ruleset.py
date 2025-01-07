import pandas as pd


def update_edges(edges, r2d_dict):
    capacity_map = {'Bridge':{0: 1.0, 1: 1.0, 2:0.75, 3:0.5, 4:0.0},
                    'Tunnel':{0: 1.0, 1: 1.0, 2:0.75, 3:0.5, 4:0.0},
                    'Roadway':{0: 1.0, 1: 1.0, 2:0.75, 3:0.5, 4:0.0}}
    free_flow_speed_map = {'Bridge':{0: 1.0, 1: 0.75, 2:0.5, 3:0.5, 4:0.0},
                           'Tunnel':{0: 1.0, 1: 0.75, 2:0.5, 3:0.5, 4:0.0},
                           'Roadway':{0: 1.0, 1: 0.75, 2:0.5, 3:0.5, 4:0.0}}
    transportation_damage = r2d_dict['TransportationNetwork']
    orig_capacity = edges['capacity'].to_dict()
    orig_maxspeed = edges['maxspeed'].to_dict()
    new_capacity = edges['capacity'].apply(lambda x: [x]).to_dict()
    new_maxspeed = edges['maxspeed'].apply(lambda x: [x]).to_dict()
    for asset_type in transportation_damage:
        for asset_id, asset_id_dict in transportation_damage[asset_type].items():
            # Nikola: Let's use component's functionality level which is also stored in the general information, instead of the initial damage state (which depends on the fragility curves)
            # User can define how damage states affect the functionality level, and then capacity and fre flow speed ratio, in the component library. It does not have to be done here.
            # initial_ds = int(asset_id_dict['GeneralInformation']['initial_damage_state'])
            # capacity_ratio = capacity_map[asset_type][initial_ds]
            # free_flow_speed_ratio = free_flow_speed_map[asset_type][initial_ds]
            capacity_ratio = asset_id_dict['GeneralInformation']['FunctionalityLevel']
            free_flow_speed_ratio = asset_id_dict['GeneralInformation']['FunctionalityLevel']
            if asset_type == 'Roadway':
                road_ids = [asset_id]
            else:
                road_id_str = r2d_dict['TransportationNetwork'][asset_type][
                    asset_id
                ]['GeneralInformation']['RoadID']
                road_ids = list(road_id_str.split(','))
            for road_id in road_ids:
                new_capacity[road_id].append(
                    orig_capacity[road_id] * capacity_ratio
                )
                new_maxspeed[road_id].append(
                    orig_maxspeed[road_id] * free_flow_speed_ratio
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
    edges['capacity'] = edges['capacity'].apply(lambda x: 1 if x == 0 else x)
    edges['maxspeed'] = edges['maxspeed'].apply(lambda x: 0.001 if x == 0 else x)
    return edges
