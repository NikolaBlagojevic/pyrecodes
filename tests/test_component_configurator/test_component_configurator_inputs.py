MAIN_FILE = './tests/test_inputs/test_inputs_Alameda_Main.json'
SYSTEM_LEVEL_DATA_DICT = {'START_TIME_STEP': 0,
                            'MAX_TIME_STEP': 100,
                            'REPAIR_CREW_DEMAND_PER_SQFT': {"DS1": 2000, "DS2": 2000, "DS3": 1000, "DS4": 1000}, 
                            'REPAIR_CREW_DEMAND_PER_MILE_ROADWAY': 0.5,
                            'REPAIR_CREW_DEMAND_PER_MILE_PIPE': 2,
                            'REPAIR_CREW_DEMAND_PER_MILE_BRIDGE': 4,
                            'REPAIR_CREW_DEMAND_PER_MILE_TUNNEL': 4,
                            'MAX_REPAIR_CREW_DEMAND_PER_BUILDING': 100,
                            'HOUSING_RESOURCES': ['Shelter', 'FunctionalHousing'],
                            "DEMAND_PER_PERSON": {"ElectricPower": 0.02, "PotableWater": 150, "CellularCommunication": 0.033}}
RECOVERY_TIME_STEPPING_RULE = [{"start": 0, "end": 30, "step": 1}, 
                                {"start": 30, "end": 80, "step": 5}, 
                                {"start": 80, "end": 1000, "step": 10}]
LOCALITY_STRING = ['Locality 10']
COMPONENT_DICT_REPAIR_COST_TESTS = {
    "RecoveryModel": {
        "FileName": "component_level_recovery_activities_model",
        "ClassName": "ComponentLevelRecoveryActivitiesModel",
        "Parameters": {
            "Financing": {
                "Duration": {
                    "Lognormal": {
                        "Median": 1,
                        "Dispersion": 0.0
                    }
                },
                "Demand": [
                    {
                        "Resource": "Money",
                        "Amount": 0.1
                    }
                ],
                "PrecedingActivities": []
            }
        }
    }
}

DAMAGE_STATE = 3

R2D_COMPONENT_DATA = {
    "Information": {
        "GeneralInformation": {
          "AIM_id": "1",
          "location": {
            "latitude": 37.7709536,
            "longitude": -122.2939517
          },
          "Latitude": 37.7709536,
          "Longitude": -122.2939517,
          "NumberOfStories": 3,
          "YearBuilt": 1953,
          "OccupancyClass": "IND2",
          "StructureType": "W1",
          "PlanArea": 18615.30048,
          "ReplacementCost": 38781.876,
          "Population": 15,
          "SoilType": "B",
          "type": "Building",
          "Footprint": "{\"type\":\"Feature\",\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[-122.293878,37.771004],[-122.293973,37.771029],[-122.294025,37.770903],[-122.293931,37.770878],[-122.293878,37.771004]]]},\"properties\":{}}",
          "units": {
            "force": "kips",
            "length": "inch",
            "time": "sec"
          },
          "DesignLevel": "MC",
          "PopulationRatio": 1
        },
        "R2Dres": {
          "R2Dres_MostLikelyCriticalDamageState": 2.0,
          "R2Dres_mean_RepairCost_loss_ratio": 4.35,
          "R2Dres_std_RepairCost_loss_ratio": 6.093754046877703,
          "R2Dres_mean_RepairTime_day": 14.8,
          "R2Dres_std_RepairTime_day": 19.252705437591537
        },
        "Demand": {
          "Units": {
            "ONE-0-1": "unitless",
            "PGA-1-1": "inchps2",
            "PGD-1-1": "inch",
            "PGD-1-3": "inch",
            "SA_0.3-1-1": "inchps2",
            "SA_1.0-1-1": "inchps2"
          }
        },
        "Loss": {
          "Units": {
            "Cost-LF.IND2-LF.W1.MC": "loss_ratio",
            "Cost-replacement-collapse": "loss_ratio",
            "Time-LF.IND2-LF.W1.MC": "day",
            "Time-replacement-collapse": "loss_ratio"
          }
        }
      },
    "Loss": {
          "Repair": {
            "Cost": {
              "LF.IND2-LF.W1.MC": 0.1,
              "replacement-collapse": 0.0
            },
            "Time": {
              "LF.IND2-LF.W1.MC": 30.0,
              "replacement-collapse": 0.0
            }
          }
        },
    "AssetType": "Building",
    "AssetSubtype": "Building",
}

R2D_COMPONENT_DAMAGE_DATA = {
        "GeneralInformation": {},
        "Demand": {
          "PGA-1-1": 161.13669891805034,
          "PGD-1-1": 24.43581949904346,
          "PGD-1-3": 2.4970896672864584,
          "PGV-1-1": 21.599359126716383,
          "SA_0.3-1-1": 397.23199929450095,
          "SA_1-1-1": 170.48955058365408
        },
        "Damage": {
          "GF.H.S-1": 0,
          "GF.V.S-1": 1,
          "LF.W1.MC-1": 2,
          "collapse-0": 0
        },
        "Loss": {
          "Repair": {
            "Cost": {
              "LF.IND2-LF.W1.MC": 0.1,
              "replacement-collapse": 0.0
            },
            "Time": {
              "LF.IND2-LF.W1.MC": 30.0,
              "replacement-collapse": 0.0
            }}
        }
    }

R2D_ROADWAY_DATA = {
        "GeneralInformation": {
          "AIM_id": "3015",
          "location": {
            "latitude": 37.77628184347495,
            "longitude": -122.28533659228832
          },
          "geometry": "LINESTRING (-122.28588099975882 37.77632400012012, -122.28574500021472 37.776316000146586, -122.28534000015874 37.776295000123184, -122.28532400026525 37.776295000123184, -122.28520600026445 37.77628499997468, -122.28508900008858 37.776264999673586, -122.28479807687329 37.77619721186654)",
          "TigerOID": "1102325761249",
          "RoadType": "residential",
          "NumOfLanes": 1,
          "MaxMPH": 25,
          "StartNode": 217,
          "EndNode": 3369,
          "ExplodeID": 0,
          "SegID": 0,
          "type": "Roadway",
          "assetSubtype": "Roadway",
          "SoilType": "A",
          "units": {
            "force": "kips",
            "length": "inch",
            "time": "sec"
          },
          "RoadHazusClass": "HRD2"
        },
        "R2Dres": {
          "R2Dres_MostLikelyCriticalDamageState": 0.0,
          "R2Dres_mean_RepairCost_loss_ratio": 0.32299999999999995,
          "R2Dres_std_RepairCost_loss_ratio": 0.3925068358151437,
          "R2Dres_mean_RepairTime_day": 15.26,
          "R2Dres_std_RepairTime_day": 26.84396363874724
        },
        "Demand": {
          "Units": {
            "ONE-0-1": "unitless",
            "PGA-1-1": "inchps2",
            "PGD-1-1": "inch",
            "PGD-1-3": "inch",
            "SA_0.3-1-1": "inchps2",
            "SA_1.0-1-1": "inchps2"
          }
        },
        "Loss": {
          "Units": {
            "Cost-HRD-HRD.GF.2": "loss_ratio",
            "Cost-replacement-collapse": "loss_ratio",
            "Time-HRD-HRD.GF.2": "day",
            "Time-replacement-collapse": "loss_ratio"
          }
        }
      }

R2D_PIPE_DATA = {
        "GeneralInformation": {
          "AIM_id": "1",
          "location": {
            "latitude": 37.7785,
            "longitude": -122.28950000000002
          },
          "geometry": "LINESTRING (-122.29 37.778, -122.289 37.779)",
          "Diam": 0.5,
          "InpID": "2ND",
          "Kb": 0,
          "Kc": 100,
          "Km": 0,
          "Kw": 0,
          "Len": 366.087755,
          "R": 0,
          "Rc": 0,
          "Status": "OPEN",
          "endNode": "node_835",
          "startNode": "node_1247",
          "type": "Pipe",
          "units": {
            "force": "kips",
            "length": "inch",
            "time": "sec"
          },
          "material flexibility": "D",
          "material": "BS"
        },
        "R2Dres": {
          "R2Dres_MostLikelyCriticalDamageState": 0.0
        },
        "Demand": {
          "Units": {
            "ONE-0-1": "unitless",
            "PGA-1-1": "inch",
            "PGA-2-1": "inch",
            "PGD-1-1": "inch",
            "PGD-1-3": "inchps2",
            "PGD-2-1": "inch",
            "PGD-2-3": "inchps2",
            "SA_0.3-1-1": "inchps2",
            "SA_0.3-2-1": "inchps2",
            "SA_1.0-1-1": "inchps2",
            "SA_1.0-2-1": "inchps2"
          }
        }
      }

INTERFACE_PARAMETERS_IN_SYSTEM_CONFIGURATION = {
        "Resource": "SupplyInterfaceResource1",
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
            "Resource": "DemandInterfaceResource1",
            "Amount": 5
        }
    }

INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY = {
    'ComponentClass': 'InfrastructureInterface',
    'RecoveryModel': {
        "FileName": "infrastructure_interface_recovery_model",
        "ClassName": "InfrastructureInterfaceRecoveryModel",
        "Parameters": {},
    },
    'Supply': { 
        'SupplyInterfaceResource1': {
            'Amount': 0,
            'FunctionalityToAmountRelation': 'Linear'
        }
    },
    'OperationDemand': {
        'DemandInterfaceResource1': {
            'Amount': 0,
            'FunctionalityToAmountRelation': 'Constant'
        }
    }
}