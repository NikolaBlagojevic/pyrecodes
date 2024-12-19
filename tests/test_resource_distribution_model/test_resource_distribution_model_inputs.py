
MAIN_FILE_REWET = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main.json'
RESOURCE_NAME_REWET = 'PotableWater'
RESOURCE_PARAMETERS_REWET = {
    "INPFile": "./tests/test_inputs/test_ThreeLocalities_water_distribution_network/ThreeLocalitiesWaterNetwork.inp",
    "Results_folder": "./tests/test_inputs/test_ThreeLocalities_water_distribution_network/rewet_results",
    "Temp_folder": "./tests/test_inputs/test_ThreeLocalities_water_distribution_network/rewet_temp"
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
                    "SoilType": "B",
                    "type": "Building",
                    "Footprint": "{\"type\":\"Feature\",\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[-122.293878,37.771004],[-122.293973,37.771029],[-122.294025,37.770903],[-122.293931,37.770878],[-122.293878,37.771004]]]},\"properties\":{}}",
                    "units": {
                        "force": "kips",
                        "length": "inch",
                        "time": "sec"
                    },
                    "DesignLevel": "MC",
                    "Population_Ratio": 1.0,
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