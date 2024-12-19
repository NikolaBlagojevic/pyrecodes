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
