
MAIN_FILE_REWET = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main.json'
MAIN_FILE_RESIDUAL_DEMAND = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main.json'
RESOURCE_NAME_REWET = 'PotableWater'
RESOURCE_NAME_RESIDUAL_DEMAND = 'TransportationService'
RESOURCE_PARAMETERS_REWET = {
    "INPFile": "./tests/test_inputs/test_ThreeLocalities_water_distribution_network/ThreeLocalitiesWaterNetwork.inp",
    "Results_folder": "./tests/test_inputs/test_ThreeLocalities_water_distribution_network/rewet_results",
    "Temp_folder": "./tests/test_inputs/test_ThreeLocalities_water_distribution_network/rewet_temp"
}
RESOURCE_PARAMETERS_RESIDUAL_DEMAND = {
    "Directory": "./tests/test_inputs/test_ThreeLocalities_transportation_network/",
    "EdgeFile": "./tests/test_inputs/test_ThreeLocalities_transportation_network/ProcessedRoadNetworkRoads.geojson",
    "NodeFile": "./tests/test_inputs/test_ThreeLocalities_transportation_network/ProcessedRoadNetworkNodes.geojson",
    "ODFilePre":"./tests/test_inputs/test_ThreeLocalities_transportation_network/OD_Matrix.csv",
    "TwoWayEdges":True,
    "HourList": [7, 8],
    "CapacityRuleset":"./tests/test_inputs/test_ThreeLocalities_transportation_network/transportation_capacity_ruleset.py",
    "DemandRuleset":"./tests/test_inputs/test_ThreeLocalities_transportation_network/transportation_demand_ruleset.py",
    "ResultsFolder": "./tests/test_inputs/test_ThreeLocalities_transportation_network/results",
    "TripCutoffThreshold": 3
}

INITIAL_R2D_DICT_REWET = {
    "Buildings": {
        "Building": {
            "1": {
                "GeneralInformation": {
                    "AIM_id": "1",
                    "location": {
                        "latitude": 2,
                        "longitude": 0
                    },
                    "Latitude": 2,
                    "Longitude": 0,
                    "NumberOfStories": 1,
                    "YearBuilt": 1953,
                    "OccupancyClass": "RES1",
                    "StructureType": "W1",
                    "PlanArea": 18615.30048,
                    "ReplacementCost": 38781.876,
                    "Population": 5,
                    "PopulationRatio": 1.0,
                    "SoilType": "B",
                    "type": "Building",
                    "Footprint": "{\"type\":\"Feature\",\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[-122.293878,37.771004],[-122.293973,37.771029],[-122.294025,37.770903],[-122.293931,37.770878],[-122.293878,37.771004]]]},\"properties\":{}}",
                    "units": {
                        "force": "kips",
                        "length": "inch",
                        "time": "sec"
                    },
                    "DesignLevel": "MC",
                    "PopulationRatio": 1.0,
                    "OperationDemand": {
                        "Communication": 1.0,
                        "ElectricPower": 1.0,
                        "PotableWater": 1.0
                    },
                    "RecoveryDemand": {}
                },
                "Damage": {}
            }
        }
    },
    "WaterDistributionNetwork": {
        "Pipe": {
            "1": {
                "GeneralInformation": {
                    "AIM_id": "1",
                    "location": {
                        "latitude": 1,
                        "longitude": 1
                    },
                    "geometry": "LINESTRING (1 1, 0 0)",
                    "Diam": 1.0,
                    "InpID": "1",
                    "Kb": 0,
                    "Kc": 100,
                    "Km": 0,
                    "Kw": 0,
                    "Len": 18559,
                    "R": 0,
                    "Rc": 0,
                    "Status": "OPEN",
                    "endNode": "3",
                    "startNode": "1",
                    "type": "Pipe",
                    "units": {
                        "force": "kips",
                        "length": "ft",
                        "time": "sec"
                    },
                    "material flexibility": "B",
                    "material": "CI",
                    "OperationDemand": {},
                    "RecoveryDemand": {}
                },
                "Damage": {
                    "Location": [],
                    "Type": []
                }
            },
            "2": {
                "GeneralInformation": {
                    "AIM_id": "2",
                    "location": {
                        "latitude": 0,
                        "longitude": 0
                    },
                    "geometry": "LINESTRING (0 0, 0 2)",
                    "Diam": 1.0,
                    "InpID": "2",
                    "Kb": 0,
                    "Kc": 100,
                    "Km": 0,
                    "Kw": 0,
                    "Len": 13123,
                    "R": 0,
                    "Rc": 0,
                    "Status": "OPEN",
                    "endNode": "4",
                    "startNode": "3",
                    "type": "Pipe",
                    "units": {
                        "force": "kips",
                        "length": "ft",
                        "time": "sec"
                    },
                    "material flexibility": "B",
                    "material": "CI",
                    "OperationDemand": {},
                    "RecoveryDemand": {}
                },
                "Damage": {
                    "Location": [],
                    "Type": []
                }
            },
            "3": {
                "GeneralInformation": {
                    "AIM_id": "3",
                    "location": {
                        "latitude": 2,
                        "longitude": 0
                    },
                    "geometry": "LINESTRING (0 2, 1 1)",
                    "Diam": 4.166667,
                    "InpID": "3",
                    "Kb": 0,
                    "Kc": 100,
                    "Km": 0,
                    "Kw": 0,
                    "Len": 9280,
                    "R": 0,
                    "Rc": 0,
                    "Status": "OPEN",
                    "endNode": "5",
                    "startNode": "1",
                    "type": "Pipe",
                    "units": {
                        "force": "kips",
                        "length": "ft",
                        "time": "sec"
                    },
                    "material flexibility": "B",
                    "material": "CI",
                    "OperationDemand": {},
                    "RecoveryDemand": {}
                },
                "Damage": {
                    "Location": [],
                    "Type": []
                }
            },
            "4": {
                "GeneralInformation": {
                    "AIM_id": "4",
                    "location": {
                        "latitude": 2,
                        "longitude": 0
                    },
                    "geometry": "LINESTRING (0 2, 1 1)",
                    "Diam": 4.166667,
                    "InpID": "4",
                    "Kb": 0,
                    "Kc": 100,
                    "Km": 0,
                    "Kw": 0,
                    "Len": 9280,
                    "R": 0,
                    "Rc": 0,
                    "Status": "OPEN",
                    "endNode": "4",
                    "startNode": "6",
                    "type": "Pipe",
                    "units": {
                        "force": "kips",
                        "length": "ft",
                        "time": "sec"
                    },
                    "material flexibility": "B",
                    "material": "CI",
                    "OperationDemand": {},
                    "RecoveryDemand": {}
                },
                "Damage": {
                    "Location": [],
                    "Type": []
                }
            }
        }
    }
}

INITIAL_R2D_DICT_RESIDUAL_DEMAND = {
    "Buildings": {
        "Building": {
            "1": {
                "GeneralInformation": {
                    "AIM_id": "1",
                    "location": {
                        "latitude": 0.2,
                        "longitude": 0
                    },
                    "Latitude": 0.2,
                    "Longitude": 0,
                    "NumberOfStories": 1,
                    "YearBuilt": 1953,
                    "OccupancyClass": "RES1",
                    "StructureType": "W1",
                    "PlanArea": 18615.30048,
                    "ReplacementCost": 38781.876,
                    "Population": 5,
                    "PopulationRatio": 1.0,
                    "SoilType": "B",
                    "type": "Building",
                    "Footprint": "{\"type\":\"Feature\",\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[-122.293878,37.771004],[-122.293973,37.771029],[-122.294025,37.770903],[-122.293931,37.770878],[-122.293878,37.771004]]]},\"properties\":{}}",
                    "units": {
                        "force": "kips",
                        "length": "inch",
                        "time": "sec"
                    },
                    "DesignLevel": "MC",
                    "PopulationRatio": 1.0,
                    "OperationDemand": {'Communication': 1.0, 'ElectricPower': 1.0, 'PotableWater': 1.0},
                    "RecoveryDemand": {}
                },
                "Damage": {}
            }
        }
    },
    "TransportationNetwork": {
        "Roadway": {
            "1": {
                "GeneralInformation": {
                    "AIM_id": "1",
                    "location": {
                        "latitude": 0,
                        "longitude": 0
                    },
                    "geometry": "LINESTRING (0 0, 0.1 0.1)",
                    "TigerOID": "11029704599947",
                    "RoadType": "residential",
                    "NumOfLanes": 1,
                    "MaxMPH": 25,
                    "MTFCC": "S1400",
                    "NAME": "Santa Clara Ave",
                    "StartNode": 243,
                    "EndNode": 757,
                    "ExplodeID": 23,
                    "SegID": 0,
                    "type": "Roadway",
                    "assetSubtype": "Roadway",
                    "SoilType": "A",
                    "units": {
                        "force": "kips",
                        "length": "inch",
                        "time": "sec"
                    },
                    "RoadHazusClass": "HRD2",
                    "OperationDemand": {},
                    "RecoveryDemand": {},
                    "FunctionalityLevel": 1.0
                },
                "Damage": {}     
            },
            "2": {
                "GeneralInformation": {
                    "AIM_id": "2",
                    "location": {
                        "latitude": 0.1,
                        "longitude": 0.1
                    },
                    "geometry": "LINESTRING (0.1 0.1, 0.2 0)",
                    "TigerOID": "11029704599947",
                    "RoadType": "residential",
                    "NumOfLanes": 1,
                    "MaxMPH": 25,
                    "MTFCC": "S1400",
                    "NAME": "Santa Clara Ave",
                    "StartNode": 243,
                    "EndNode": 757,
                    "ExplodeID": 23,
                    "SegID": 0,
                    "type": "Roadway",
                    "assetSubtype": "Roadway",
                    "SoilType": "A",
                    "units": {
                        "force": "kips",
                        "length": "inch",
                        "time": "sec"
                    },
                    "RoadHazusClass": "HRD2",
                    "OperationDemand": {},
                    "RecoveryDemand": {},
                    "FunctionalityLevel": 1.0
                },
                "Damage": {}
            },
            "3": {
                "GeneralInformation": {
                    "AIM_id": "3",
                    "location": {
                        "latitude": 0.2,
                        "longitude": 0
                    },
                    "geometry": "LINESTRING (0.2 0, 0 0)",
                    "TigerOID": "11029704599947",
                    "RoadType": "residential",
                    "NumOfLanes": 1,
                    "MaxMPH": 25,
                    "MTFCC": "S1400",
                    "NAME": "Santa Clara Ave",
                    "StartNode": 243,
                    "EndNode": 757,
                    "ExplodeID": 23,
                    "SegID": 0,
                    "type": "Roadway",
                    "assetSubtype": "Roadway",
                    "SoilType": "A",
                    "units": {
                        "force": "kips",
                        "length": "inch",
                        "time": "sec"
                    },
                    "RoadHazusClass": "HRD2",
                    "OperationDemand": {},
                    "RecoveryDemand": {},
                    "FunctionalityLevel": 1.0
                },
                "Damage": {}
            }          
        }
    }
}