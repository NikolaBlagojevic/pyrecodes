COMPONENT_NAME = 'TestComponent'
COMPONENT_PARAMETERS = {
        "ComponentClass": {"Filename": "building_with_emergency_calls", "ClassName": "BuildingWithEmergencyCalls"},
        "RecoveryModel": {
            "FileName": "component_level_recovery_activities_model",
            "ClassName": "ComponentLevelRecoveryActivitiesModel",
            "Parameters": {
                "Repair": {
                    "Duration": {
                        "Deterministic": {
                            "Value": 100
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "RecoveryResource1",
                            "Amount": 0.1
                        }],
                    }
                },
            "DamageFunctionalityRelation": {
                "Type": "ReverseLinear"
            }
        },
        "Supply": {
            "SupplyResource1": {
                "Amount": 10,
                "FunctionalityToAmountRelation": "Constant",
                "UnmetDemandToAmountRelation": "Binary"
            },
            "SupplyResource2": {
                "Amount": 100,
                "FunctionalityToAmountRelation": "Linear",
                "UnmetDemandToAmountRelation": "Constant"
            }
        },
        "OperationDemand": {
            "DemandResource1": {
                "Amount": 1,
                "FunctionalityToAmountRelation": "Constant"
            },
            "DemandResource2": {
                "Amount": 5,
                "FunctionalityToAmountRelation": "Binary"
            }
        }
    }

RECOVERY_TIME_STEPS_DENSE = list(range(500))
RECOVERY_TIME_STEPS_SPARSE = list(range(0, 500, 5))

SUPPLY_DICT_SIMPLE = {
        "TestInterface": {
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
    }

SUPPLY_DICT_COMPLICATED = {
    "TestInterface": {
                        "Resource": "SupplyInterfaceResource1",
                        "Amount": [100, 50, 0, 200, 500, 600],
                        "RestoredIn": [
                            {
                                "Deterministic": {
                                    "Value": 0
                                }
                            },
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
                            },
                            {
                                "Deterministic": {
                                    "Value": 80
                                }
                            },
                            {
                                "Deterministic": {
                                    "Value": 150
                                }
                            },
                            {
                                "Deterministic": {
                                    "Value": 200
                                }
                            }
                        ],
                        "Demand": {
                            "Resource": "DemandInterfaceResource1",
                            "Amount": 5
                        }
                    }
}

INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY = {
    'ComponentClass': 'InfrastructureInterface',
    'RecoveryModel': {
        "FileName": "infrastructure_interface_recovery_model",
        "ClassName": "InfrastructureInterfaceRecoveryModel",
        "Parameters": { },
    },
    "Supply": {
                "SupplyInterfaceResource1": {
                    "InitialAmount": 0,
                    "FunctionalityToAmountRelation": "Constant",
                    "UnmetDemandToAmountRelation": "Binary"
                }
            },
            "OperationDemand": {
                "DemandInterfaceResource1": {
                    "Amount": 5,
                    "FunctionalityToAmountRelation": "Constant"
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

BUILDING_WITH_HOUSEHOLDS_COMPONENT_LIBRARY_PARAMETERS = {
        "ComponentClass": {"FileName": "r2d_building_with_households", "ClassName": "R2DBuildingWithHouseholds"},
        "HouseholdClass": {"FileName": "household_gpt", "ClassName": "HouseholdGPT"},
        "RecoveryModel": {
            "FileName": "component_level_recovery_activities_model",
            "ClassName": "ComponentLevelRecoveryActivitiesModel",
            "Parameters": {
                "RapidInspection": {
                    "Duration": {
                        "Lognormal": {
                            "Median": 1,
                            "Dispersion": 0.0
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "FirstResponderEngineer",
                            "Amount": 0.1
                        }
                    ],
                    "PrecedingActivities": []
                },
                "DetailedInspection": {
                    "Duration": {
                        "Lognormal": {
                            "Median": 1,
                            "Dispersion": 0.0
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "SeniorEngineer",
                            "Amount": 2
                        }
                    ],
                    "PrecedingActivities": [
                        "RapidInspection"
                    ]
                },
                "CleanUp": {
                    "Duration": {
                        "Lognormal": {
                            "Median": 1,
                            "Dispersion": 0.0
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "CleanUpCrew",
                            "Amount": 1
                        }
                    ],
                    "PrecedingActivities": [
                        "RapidInspection"
                    ]
                },
                "SitePreparation": {
                    "Duration": {
                        "Lognormal": {
                            "Median": 1,
                            "Dispersion": 0.0
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "SitePreparationCrew",
                            "Amount": 1
                        }
                    ],
                    "PrecedingActivities": [
                        "RapidInspection"
                    ]
                },
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
                            "Amount": 0.4
                        }
                    ],
                    "PrecedingActivities": [
                        "RapidInspection",
                        "DetailedInspection"
                    ]
                },
                "ArchAndEngDesign": {
                    "Duration": {
                        "Lognormal": {
                            "Median": 1,
                            "Dispersion": 0.0
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "EngineeringDesignTeam",
                            "Amount": 1
                        }
                    ],
                    "PrecedingActivities": [
                        "RapidInspection",
                        "DetailedInspection"
                    ]
                },
                "ContractorMobilization": {
                    "Duration": {
                        "Lognormal": {
                            "Median": 1,
                            "Dispersion": 0.0
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "Contractor",
                            "Amount": 1
                        }
                    ],
                    "PrecedingActivities": [
                        "RapidInspection",
                        "DetailedInspection",
                        "ArchAndEngDesign"
                    ]
                },
                "Permitting": {
                    "Duration": {
                        "Lognormal": {
                            "Median": 1,
                            "Dispersion": 0.0
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "PlanCheckEngineeringTeam",
                            "Amount": 1
                        }
                    ],
                    "PrecedingActivities": [
                        "RapidInspection",
                        "DetailedInspection",
                        "ArchAndEngDesign"
                    ]
                },
                "Repair": {
                    "Duration": {
                        "Lognormal": {
                            "Median": 1,
                            "Dispersion": 0.0
                        }
                    },
                    "Demand": [
                        {
                            "Resource": "RepairCrew_Buildings",
                            "Amount": 0
                        }
                    ],
                    "PrecedingActivities": [
                        "RapidInspection",
                        "DetailedInspection",
                        "CleanUp",
                        "SitePreparation",
                        "Financing",
                        "ArchAndEngDesign",
                        "ContractorMobilization",
                        "Permitting"
                    ]
                }
            },
            "DamageFunctionalityRelation": {
                "Type": "ReverseBinary"
            }
        },
        "Supply": {
            "Shelter": {
                "Amount": 0,
                "FunctionalityToAmountRelation": "Linear",
                "UnmetDemandToAmountRelation": "Constant"
            },
            "FunctionalHousing": {
                "Amount": 0,
                "FunctionalityToAmountRelation": "Linear",
                "UnmetDemandToAmountRelation": "Linear"
            }
        },
        "OperationDemand": {
            "Shelter": {
                "Amount": 0,
                "FunctionalityToAmountRelation": "Constant"
            },
            "FunctionalHousing": {
                "Amount": 0,
                "FunctionalityToAmountRelation": "Constant"
            },
            "ElectricPower": {
                "Amount": 0,
                "FunctionalityToAmountRelation": "Linear"
            },
            "PotableWater": {
                "Amount": 0,
                "FunctionalityToAmountRelation": "Linear"
            },
            "CellularCommunication": {
                "Amount": 0,
                "PostDisasterIncreaseDueToEmergencyCalls": "True",
                "FunctionalityToAmountRelation": "Linear"
            }
        }
    }

BUILDING_WITH_HOUSEHOLDS_PARAMETERS = {
          "AIM_id": "30",
          "location": {
            "latitude": 37.781398,
            "longitude": -122.2944375
          },
          "Latitude": 37.781398,
          "Longitude": -122.2944375,
          "NumberOfStories": 1,
          "YearBuilt": 1994,
          "OccupancyClass": "RES1",
          "StructureType": "W1",
          "PlanArea": 123736.9925,
          "ReplacementCost": 343713.868,
          "Population": 16,
          "SoilType": "B",
          "type": "Building",
          "Footprint": "{\"type\":\"Feature\",\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[-122.294322,37.781220],[-122.294299,37.781565],[-122.294553,37.781576],[-122.294576,37.781231],[-122.294322,37.781220]]]},\"properties\":{}}",
          "Households": [
            {
              "HouseholdID": "4271_32",
              "CensusBlock": "Block 1003",
              "CensusTract": "Census Tract 4271",
              "SocioEconomicParameters": {
                "Tenure": "Owner",
                "Income": "High",
                "Occupants": 4,
                "Elderly": 4,
                "Children": 0,
                "EmploymentStatus": 1,
                "ImmigrationStatus": "foreign born",
                "Home": "30",
                "Friends": [
                  13605
                ]
              },
              "ResourceDemand": {
                "PotableWater": 150
              }, "InformGPTMethod": "None"
            },
            {
              "HouseholdID": "4271_33",
              "CensusBlock": "Block 1003",
              "CensusTract": "Census Tract 4271",
              "SocioEconomicParameters": {
                "Tenure": "Renter",
                "Income": "Low",
                "Occupants": 3,
                "Elderly": 0,
                "Children": 1,
                "EmploymentStatus": 2,
                "ImmigrationStatus": "foreign born",
                "Home": "30",
                "Friends": [
                  10209
                ]
              },
              "ResourceDemand": {
                "PotableWater": 150
              }, "InformGPTMethod": "None"
            }
          ]
        }
