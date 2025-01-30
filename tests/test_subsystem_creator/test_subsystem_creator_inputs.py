MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'
MAIN_FILE_REWET = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main.json'
MAIN_FILE_ALAMEDA = './tests/test_inputs/test_inputs_Alameda_Main.json'

LOCALITY_CENTROID = {'LocalityName': 'Locality 1', 'Coordinates': [0, 0]}
LOCALITY_1_BOUNDING_BOX = {'LocalityName': 'Locality 1', "Coordinates": {
                "BoundingBox": [[0.5, 1.5], [0.5, 0.5], [1.5, 0.5], [1.5, 1.5]]
            }}
LOCALITY_2_BOUNDING_BOX = {'LocalityName': 'Locality 1', "Coordinates": {
                "BoundingBox": [[-0.5, 0.5], [-0.5, -0.5], [0.5, -0.5], [0.5, 0.5]]
            }}
LOCALITY_ALAMEDA_GEOJSON = {
    "LocalityName": "Alameda 964",
    "GeoJSON": {
                    "Filename": "./tests/test_inputs/Alameda_TravelAnalysisZone_964.geojson"
                }
}

PARAMETERS_BTS = {
                            "ComponentsInLocality": {
                                "BaseTransceiverStation_2": 1
                        }
                    }

PARAMETERS_ERC = {
                    "ComponentName": [
                                "EmergencyResponseCenter"
                            ],
                            "RecoveryTimeStepping": [
                                {
                                    "start": 0,
                                    "end": 50,
                                    "step": 1
                                },
                                {
                                    "start": 50,
                                    "end": 1000,
                                    "step": 5
                                }
                            ]
                    }

PARAMETERS_ERC_2 = {
                    "ComponentName": [
                                "EmergencyResponseCenter", "EmergencyResponseCenter"
                            ],
                            "RecoveryTimeStepping": [
                                {
                                    "start": 0,
                                    "end": 50,
                                    "step": 1
                                },
                                {
                                    "start": 50,
                                    "end": 1000,
                                    "step": 5
                                }
                            ]
                    }

PARAMETERS_LINKS = {
        "ComponentsBetweenLocalities": {
                                "Locality 1": ["SuperLink"],
                                "Locality 2": ["SuperLink"]
                            }      
}

PARAMETERS_BUILDING = {
        "ComponentsInLocality": {
                "BuildingStockUnit": 1
                        }
                    }

PARAMETERS_DIFFERENT_COMPONENTS = {
        "ComponentsInLocality": {
                "BuildingStockUnit": 1,
                "BaseTransceiverStation_2": 1,
                "ElectricPowerPlant": 1
                        }
                    }

PARAMETERS_INFRASTRUCTURE_INTERFACE = {
    "ComponentName": ["ElectricPowerSupplySystem"],
    "Resource": "ElectricPower",
    "Amount": [100, 200],
    "RestoredIn": [
        {
            "Lognormal": {
                "Median": 20,
                "Dispersion": 0
            }
        },
        {
            "Deterministic": {
                "Value": 50
            }
        }
    ],
    "Demand": {
        "Resource": "CellularCommunication",
        "Amount": 5
    }
}

CONSTANTS = {
    'START_TIME_STEP': 0,
    'MAX_TIME_STEP': 500,
    'DISASTER_TIME_STEP': 1,
    "REPAIR_CREW_DEMAND_PER_SQFT": {
            "DS1": 5400,
            "DS2": 5400,
            "DS3": 2700,
            "DS4": 2700
        },
    "MAX_REPAIR_CREW_DEMAND_PER_BUILDING": 50,
}

PARAMETERS_R2D_WATER_SYSTEM = {
                            "Resource": ["PotableWater"],
                            "R2DJSONFile_Info": "./tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_det.json",
                            "SubsystemNameInR2DJSON": "WaterDistributionNetwork",
                            "AssetTypes": ["Pipe"]
                            }

PARAMETERS_R2D_BUILDINGS = {
                            "Resource": ["Housing"],
                            "R2DJSONFile_Info": "./tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_det.json",
                            "SubsystemNameInR2DJSON": "Buildings",
                            "AssetTypes": ["Building"]
                            }

PARAMETERS_R2D_ALAMEDA = {
    "Resource": [
                "Shelter",
                "FunctionalHousing"
            ],
            "R2DJSONFile_Info":"./tests/test_inputs/test_inputs_Alameda_Results_det.json",
            "SubsystemNameInR2DJSON": "Buildings",
            "AssetTypes": [
                "Building"
            ],
            "MaxNumComponents": 10,
            "RecoveryTimeStepping": [
                {
                    "start": 0,
                    "end": 80,
                    "step": 1
                },
                {
                    "start": 80,
                    "end": 1000,
                    "step": 10
                }
            ]
}

DAMAGE_INPUT_R2D = {
        "ClassName": "R2DDamageInput",
        "FileName": "r2d_damage_input",
        "Parameters": {"DamageFile": "./tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_0.json",
        "DistributionModelDamage": [
            "PotableWater"
        ]
        }
    }

DAMAGE_INPUT_ALAMEDA = {
        "FileName": "r2d_damage_input",
        "ClassName": "R2DDamageInput",
        "Parameters": {
            "DamageFile": "./tests/test_inputs/test_inputs_Alameda_Results_0.json",
            "DistributionModelDamage": [
                "PotableWater"
            ]
        }
    }