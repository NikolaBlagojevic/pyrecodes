Example 4
=========

Example 4 shows how infrastructure performance data can be integrated within an iRe-CoDeS system-of-systems model using supply/demand interfaces. Such interfaces allow the integration of individual infrastructure performance assessment performed outside of pyrecodes that can capture interdependencies among systems and their impact on buildings' functional recovery. Interfaces are tiered to accomodate infrastructure managers privacy and/or security concerns. Interface application is illustrated by extending the Example 3 North-East San Francisco Case Study to include the impact of infrastructure systems on building's functionality. Further details are available `here <https://link.springer.com/article/10.1007/s10669-023-09931-0>`_.

.. figure:: ../../figures/Example_4_infrastructure_interfaces.png
        :alt: Tiered supply/demand interfaces for infrastructure systems

        Tiered supply/demand infrastructure simulator interfaces. Tier 1 interface requires post-event resource supply dynamics defined per locality. Tier 2 interface additionally requires the information on the resources that the infrastructure system needs to operate on a locality level. Tier 3 interfaces needs component-level supply/demand dynamics.

Running the example
-------------------

Example 4 Jupyter notebook illustrates how to run the pyrecodes simulation and plot the post-disaster supply/demand/consumption dynamics and the components' recovery gantt chart, as well as animate the building recovery process.

.. Run the example online using `Google Colab <https://colab.research.google.com/github/NikolaBlagojevic/pyrecodes/blob/main/Example4_NorthEast_SF_Interfaces_Colab.ipynb>`_.
    
The example can be run locally by downloading the `Example 4 Jupyter notebook <https://github.com/NikolaBlagojevic/pyrecodes/blob/main/Example4_NorthEast_SF_Interfaces.ipynb>`_ and the required files from the `Example 4 folder <https://github.com/NikolaBlagojevic/pyrecodes/tree/main/Example%204>`_. 

Component library
-----------------

As Example 4 extends Example 3, building recovery activities, their duration and resource demand as well as the supply of recovery resources from the Emergency Response Center are identical as in Example 3. However, to consider the infrastructure systems, the Example 3 component library file is supplemented as follows:

- operational demand of residential buildings for electric power, potable water and communication services is now considered and estimated based on building's occupancy (i.e., number of people residing in the building at each time step of the recovery simulation). Dummy values are set in the component library file and the true values are set when system is created in the SystemCreator class where building occupancy is set.

- two housing resources provided by buildings to their inhabitants are considered: shelter and functional housing. Supply of shelter is conditioned only on the building's damage state, while functional housing supply is also conditioned on the fulfillment of building's demand for infrastructure services.

- components representing the three infrastructure systems whose post-earthquake performance is evaluated using supply/demand interfaces are added.

EmergencyResponseCenter
```````````````````````

.. toggle::

    .. code-block:: json

        "EmergencyResponseCenter": {
                "ComponentClass": {"FileName": "standard_irecodes_component", "ClassName": "StandardiReCoDeSComponent"},
                "RecoveryModel": {
                    "FileName": "no_recovery_activity_model",
                    "ClassName": "NoRecoveryActivityModel",
                    "Parameters": {},
                    "DamageFunctionalityRelation": {
                        "Type": "Constant"
                    }
                },
                "Supply": {
                    "FirstResponderEngineer": {
                        "Amount": 50,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "SeniorEngineer": {
                        "Amount": 50,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "Contractor": {
                        "Amount": 50,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "Money": {
                        "Amount": 5500000000,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "PlanCheckEngineeringTeam": {
                        "Amount": 20,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "SitePreparationCrew": {
                        "Amount": 20,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "CleanUpCrew": {
                        "Amount": 20,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "EngineeringDesignTeam": {
                        "Amount": 50,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "DemolitionCrew": {
                        "Amount": 10,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "RepairCrew": {
                        "Amount": 400,
                        "FunctionalityToAmountRelation": "Linear"
                    }
                }
            } 

DS0 Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS0_Building": {
                "ComponentClass": {"FileName": "r2d_component", "ClassName": "R2DBuilding"},
                "RecoveryModel": {
                    "FileName": "no_recovery_activity_model",
                    "ClassName": "NoRecoveryActivityModel",
                    "Parameters": {},
                    "DamageFunctionalityRelation": {
                        "Type": "Constant"
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
                    }
                }
            }

DS1 Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS1_Building": {
                "ComponentClass": "BuildingStockUnitWithEmergencyCalls",
                "RecoveryModel": {
                    "Type": "ComponentLevelRecoveryActivitiesModel",
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
                        "ContractorMobilization": {
                            "Duration": {
                                "Lognormal": {
                                    "Median": 7,
                                    "Dispersion": 0.2
                                }
                            },
                            "Demand": [
                                {
                                    "Resource": "Contractor",
                                    "Amount": 1
                                }
                            ],
                            "PrecedingActivities": [
                                "RapidInspection"
                            ]
                        },
                        "Repair": {
                            "Duration": {
                                "Lognormal": {
                                    "Median": 1,
                                    "Dispersion": 0.2
                                }
                            },
                            "Demand": [
                                {
                                    "Resource": "RepairCrew",
                                    "Amount": 10
                                }
                            ],
                            "PrecedingActivities": [
                                "RapidInspection",
                                "ContractorMobilization"
                            ]
                        }
                    },
                    "DamageFunctionalityRelation": {
                        "Type": "Constant"
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
                    }
                }
            }

DS2 Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS2_Building": {
                "ComponentClass": {"FileName": "r2d_component", "ClassName": "R2DBuilding"},
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
                                    "Median": 7,
                                    "Dispersion": 0.2
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
                                    "Median": 3,
                                    "Dispersion": 0.2
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
                        "Financing": {
                            "Duration": {
                                "Lognormal": {
                                    "Median": 7,
                                    "Dispersion": 0.2
                                }
                            },
                            "Demand": [
                                {
                                    "Resource": "Money",
                                    "Amount": 0
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
                                    "Median": 21,
                                    "Dispersion": 0.2
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
                                    "Median": 7,
                                    "Dispersion": 0.2
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
                                    "Median": 14,
                                    "Dispersion": 0.2
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
                                    "Dispersion": 0.2
                                }
                            },
                            "Demand": [
                                {
                                    "Resource": "RepairCrew",
                                    "Amount": 0
                                }
                            ],
                            "PrecedingActivities": [
                                "RapidInspection",
                                "DetailedInspection",
                                "CleanUp",
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
                    }
                }
            }


DS3 Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS3_Building": {
            "ComponentClass": {"FileName": "r2d_component", "ClassName": "R2DBuilding"},
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
                                "Median": 14,
                                "Dispersion": 0.2
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
                                "Median": 7,
                                "Dispersion": 0.2
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
                                "Median": 7,
                                "Dispersion": 0.2
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
                                "Median": 42,
                                "Dispersion": 0.2
                            }
                        },
                        "Demand": [
                            {
                                "Resource": "Money",
                                "Amount": 0
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
                                "Median": 42,
                                "Dispersion": 0.2
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
                                "Median": 14,
                                "Dispersion": 0.2
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
                                "Median": 28,
                                "Dispersion": 0.2
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
                                "Dispersion": 0.2
                            }
                        },
                        "Demand": [
                            {
                                "Resource": "RepairCrew",
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
                }
            }
        }

DS4 Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS4_Building": {
            "ComponentClass": {"FileName": "r2d_component", "ClassName": "R2DBuilding"},
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
                    "CleanUp": {
                        "Duration": {
                            "Lognormal": {
                                "Median": 7,
                                "Dispersion": 0.2
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
                                "Median": 7,
                                "Dispersion": 0.2
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
                    "Demolition": {
                        "Duration": {
                            "Lognormal": {
                                "Median": 10,
                                "Dispersion": 0.2
                            }
                        },
                        "Demand": [
                            {
                                "Resource": "DemolitionCrew",
                                "Amount": 1
                            }
                        ],
                        "PrecedingActivities": [
                            "RapidInspection",
                            "SitePreparation",
                            "CleanUp"
                        ]
                    },
                    "Financing": {
                        "Duration": {
                            "Lognormal": {
                                "Median": 42,
                                "Dispersion": 0.2
                            }
                        },
                        "Demand": [
                            {
                                "Resource": "Money",
                                "Amount": 0
                            }
                        ],
                        "PrecedingActivities": [
                            "RapidInspection"
                        ]
                    },
                    "ArchAndEngDesign": {
                        "Duration": {
                            "Lognormal": {
                                "Median": 42,
                                "Dispersion": 0.2
                            }
                        },
                        "Demand": [
                            {
                                "Resource": "EngineeringDesignTeam",
                                "Amount": 1
                            }
                        ],
                        "PrecedingActivities": [
                            "RapidInspection"
                        ]
                    },
                    "ContractorMobilization": {
                        "Duration": {
                            "Lognormal": {
                                "Median": 14,
                                "Dispersion": 0.2
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
                            "ArchAndEngDesign"
                        ]
                    },
                    "Permitting": {
                        "Duration": {
                            "Lognormal": {
                                "Median": 28,
                                "Dispersion": 0.2
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
                            "ArchAndEngDesign"
                        ]
                    },
                    "Repair": {
                        "Duration": {
                            "Lognormal": {
                                "Median": 1,
                                "Dispersion": 0.2
                            }
                        },
                        "Demand": [
                            {
                                "Resource": "RepairCrew",
                                "Amount": 0
                            }
                        ],
                        "PrecedingActivities": [
                            "RapidInspection",
                            "CleanUp",
                            "SitePreparation",
                            "Financing",
                            "ArchAndEngDesign",
                            "ContractorMobilization",
                            "Permitting",
                            "Demolition"
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
                }
            }
        }

Electric Power Supply System
````````````````````````````

The Electric Power Supply System component represents the electric power supply system in a locality whose performance is defined using the supply/demand interface. Component template defines the recovery model - InfrastructureInterfaceRecoveryModel - which is used to simulate the pre-defined post-earthquake resource supply of the electric power supply system using the MultipleSteps relation as defined in the system configuration file. The operational demand of the system is initialized in the component library file and defined in the system configuration file as well.

.. toggle::

    .. code-block:: json

        "ElectricPowerSupplySystem": {
            "ComponentClass": {"FileName": "infrastructure_interface", "ClassName": "InfrastructureInterface"},
            "RecoveryModel": {
                "FileName": "infrastructure_interface_recovery_model",
                "ClassName": "InfrastructureInterfaceRecoveryModel",
                "Parameters": {},
                "DamageFunctionalityRelation": "MultipleSteps"
            },
            "Supply": {
                "ElectricPower": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Linear",
                    "UnmetDemandToAmountRelation": "Binary"
                }
            }
        }  

Water Supply System
````````````````````````````

.. toggle::

    .. code-block:: json

        "WaterSupplySystem": {
            "ComponentClass": {"FileName": "infrastructure_interface", "ClassName": "InfrastructureInterface"},            
            "RecoveryModel": {
                "FileName": "infrastructure_interface_recovery_model",
                "ClassName": "InfrastructureInterfaceRecoveryModel",
                "Parameters": {},
                "DamageFunctionalityRelation": ""
            },
            "Supply": {
                "PotableWater": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Linear",
                    "UnmetDemandToAmountRelation": "Binary"
                }
            },
            "OperationDemand": {
                "ElectricPower": {
                    "Amount": 0.0,
                    "FunctionalityToAmountRelation": "Constant"
                }
            }
        }

System configuration
--------------------

System configuration file in Example 4 is very similar to the one used in Example 3. The only differences come from the consideration of infrastructure systems. These differences are outlined next.

Note that two system configuration files are provided: one illustrating the implemention of Tier 1 interface, and the other illustrating the Tier 2 interface implementation. Tier 1 is presented here.

Constants
`````````

Novel constants introduced in Example 4 are contained in the **DEMAND_PER_PERSON** key. They include the values used to estimate operational demand of buildings for infrastructure services. Such values are obtained by multiplying the number of residents in a building at a time step of the resilience assessment interval and the resource demand per person. Remaining constants are explained in Example 3.

.. toggle::

    .. code-block:: json

        "Constants": {
            "START_TIME_STEP": 0,
            "MAX_TIME_STEP": 3650,
            "DISASTER_TIME_STEP": 1,
            "MAX_REPAIR_CREW_DEMAND_PER_BUILDING": 50,
            "HOUSING_RESOURCES": [
                "Shelter",
                "FunctionalHousing"
            ],
            "REPAIR_CREW_DEMAND_PER_SQFT": {
                "DS1": 5400,
                "DS2": 5400,
                "DS3": 2700,
                "DS4": 2700
            },
            "DEFAULT_REPAIR_DURATION_DICT": {
                "Lognormal": {
                    "Median": 0,
                    "Dispersion": 0.3
                }
            },
            "DEMAND_PER_PERSON": {
                "ElectricPower": 0.02,
                "PotableWater": 150
            }
        },

Content
```````

Example 4 divides the considered region, north-east San Francisco, into 5 localities, defined by their bounding box coordinates, as opposed to storing all components in a single locality as in Example 3. The effect of infrastructure systems is captured through supply/demand interfaces defined at the locality level. For each of the three considered infrastructure systems, their post-earthquake supply dynamics are defined in terms of the amount of resources they can provide to the components in their locality and the times at which these amounts are restored. For example, the electric power supply system in Locality 1 provides 150MWh from day 0 - immediately after the earthquake, and increase the supply to 450MWh, 60 days after the earthquake.

.. hint::

    The number of buildings per locality is limited to 100 to reduce the computational time of the example. This number can be increased to consider more buildings in the region.

.. toggle::

    .. code-block:: json

        "Content": {
            "Locality 1": {
                "Coordinates": {
                    "BoundingBox": [
                        [
                            -122.426388,
                            37.809410
                        ],
                        [
                            -122.397014,
                            37.809991
                        ],
                        [
                            -122.391161,
                            37.795523
                        ],
                        [
                            -122.422544,
                            37.791310
                        ]
                    ]
                },
                "Components": {
                    "RecoveryResourceSuppliers": [
                        {
                            "EmergencyResponseCenter": {
                                "CreatorClassName": "RecoveryResourceSuppliersCreator",
                                "CreatorFileName": "recovery_resource_suppliers_creator",
                                "Parameters": {
                                    "ComponentName": [
                                        "EmergencyResponseCenter"
                                    ]
                                }
                            }
                        }
                    ],
                    "Infrastructure": [
                        {
                            "ElectricPowerSupplySystem": {
                                "CreatorClassName": "Tier1InfrastructureCreator",
                                "CreatorFileName": "tier1_infrastructure_creator",
                                "Parameters": {
                                    "ComponentName": ["ElectricPowerSupplySystem"],
                                    "Resource": "ElectricPower",
                                    "Amount": [
                                        150,
                                        450
                                    ],
                                    "RestoredIn": [
                                        {
                                            "Deterministic": {
                                                "Value": 0
                                            }
                                        },
                                        {
                                            "Deterministic": {
                                                "Value": 60
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            "WaterSupplySystem": {
                                "CreatorClassName": "Tier1InfrastructureCreator",
                                "CreatorFileName": "tier1_infrastructure_creator",
                                "Parameters": {
                                    "ComponentName": ["WaterSupplySystem"],
                                    "Resource": "PotableWater",
                                    "Amount": [
                                        3400000
                                    ],
                                    "RestoredIn": [
                                        {
                                            "Deterministic": {
                                                "Value": 100
                                            }
                                        }
                                    ],
                                    "Demand": {
                                        "Resource": "ElectricPower",
                                        "Amount": 0.0
                                    }
                                }
                            }
                        }
                    ],
                    "BuildingStock": [
                        {
                            "Buildings": {
                                "CreatorClassName": "R2DSubsystemCreator",
                                "CreatorFileName": "r2d_subsystem_creator",
                                "Parameters": {
                                    "Resource": [
                                        "Shelter"
                                    ],
                                    "R2DJSONFile_Info": "./Example 4/NorthEast_SF_Housing_Exposure.json",
                                    "SubsystemNameInR2DJSON": "Buildings",
                                    "AssetTypes": [
                                        "Building"
                                    ],
                                    "MaxNumComponents": 100
                                }
                            }
                        }
                    ]
                },
                "Locality 2": {
            "Coordinates": {
                "BoundingBox": [
                    [
                        -122.432440,
                        37.790065
                    ],
                    [
                        -122.432965,
                        37.803214
                    ],
                    [
                        -122.425129,
                        37.804204
                    ],
                    [
                        -122.422585,
                        37.791310
                    ]
                ]
            },
            "Components": {
                "Infrastructure": [
                    {
                        "ElectricPowerSupplySystem": {
                            "CreatorClassName": "Tier1InfrastructureCreator",
                            "CreatorFileName": "tier1_infrastructure_creator",
                            "Parameters": {
                                "ComponentName": ["ElectricPowerSupplySystem"],
                                "Resource": "ElectricPower",
                                "Amount": [
                                    40,
                                    80
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 15
                                        }
                                    },
                                    {
                                        "Deterministic": {
                                            "Value": 30
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "WaterSupplySystem": {
                            "CreatorClassName": "Tier1InfrastructureCreator",
                            "CreatorFileName": "tier1_infrastructure_creator",
                            "Parameters": {
                                "ComponentName": ["WaterSupplySystem"],
                                "Resource": "PotableWater",
                                "Amount": [
                                    600000
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 10
                                        }
                                    }
                                ],
                                "Demand": {
                                    "Resource": "ElectricPower",
                                    "Amount": 0.0
                                }
                            }
                        }
                    }
                ],
                "BuildingStock": [
                    {
                        "Buildings": {
                            "CreatorClassName": "R2DSubsystemCreator",
                            "CreatorFileName": "r2d_subsystem_creator",
                            "Parameters": {
                                "Resource": [
                                    "Shelter"
                                ],
                                "R2DJSONFile_Info": "./Example 4/NorthEast_SF_Housing_Exposure.json",
                                "SubsystemNameInR2DJSON": "Buildings",
                                "AssetTypes": [
                                    "Building"
                                ],
                                "MaxNumComponents": 100
                            }
                        }
                    }
                ]
            }
        },
        "Locality 3": {
            "Coordinates": {
                "BoundingBox": [
                    [
                        -122.422585,
                        37.791342
                    ],
                    [
                        -122.419838,
                        37.777871
                    ],
                    [
                        -122.431406,
                        37.776836
                    ],
                    [
                        -122.432644,
                        37.790065
                    ]
                ]
            },
            "Components": {
                "Infrastructure": [
                    {
                        "ElectricPowerSupplySystem": {
                            "CreatorClassName": "Tier1InfrastructureCreator",
                            "CreatorFileName": "tier1_infrastructure_creator",
                            "Parameters": {
                                "ComponentName": ["ElectricPowerSupplySystem"],
                                "Resource": "ElectricPower",
                                "Amount": [
                                    60
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 10
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "WaterSupplySystem": {
                            "CreatorClassName": "Tier1InfrastructureCreator",
                            "CreatorFileName": "tier1_infrastructure_creator",
                            "Parameters": {
                                "ComponentName": ["WaterSupplySystem"],
                                "Resource": "PotableWater",
                                "Amount": [
                                    450000
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 15
                                        }
                                    }
                                ],
                                "Demand": {
                                    "Resource": "ElectricPower",
                                    "Amount": 0.0
                                }
                            }
                        }
                    }
                ],
                "BuildingStock": [
                    {
                        "Buildings": {
                            "CreatorClassName": "R2DSubsystemCreator",
                            "CreatorFileName": "r2d_subsystem_creator",
                            "Parameters": {
                                "Resource": [
                                    "Shelter"
                                ],
                                "R2DJSONFile_Info": "./Example 4/NorthEast_SF_Housing_Exposure.json",
                                "SubsystemNameInR2DJSON": "Buildings",
                                "AssetTypes": [
                                    "Building"
                                ],
                                "MaxNumComponents": 100
                            }
                        }
                    }
                ]
            }
        },
        "Locality 4": {
            "Coordinates": {
                "BoundingBox": [
                    [
                        -122.422568,
                        37.791388
                    ],
                    [
                        -122.394280,
                        37.794985
                    ],
                    [
                        -122.419321,
                        37.775381
                    ]
                ]
            },
            "Components": {
                "Infrastructure": [
                    {
                        "ElectricPowerSupplySystem": {
                            "CreatorClassName": "Tier1InfrastructureCreator",
                            "CreatorFileName": "tier1_infrastructure_creator",
                            "Parameters": {
                                "ComponentName": ["ElectricPowerSupplySystem"],
                                "Resource": "ElectricPower",
                                "Amount": [
                                    1000
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 100
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "WaterSupplySystem": {
                            "CreatorClassName": "Tier1InfrastructureCreator",
                            "CreatorFileName": "tier1_infrastructure_creator",
                            "Parameters": {
                                "ComponentName": ["WaterSupplySystem"],
                                "Resource": "PotableWater",
                                "Amount": [
                                    3600000,
                                    7250000
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 20
                                        }
                                    },
                                    {
                                        "Deterministic": {
                                            "Value": 80
                                        }
                                    }
                                ],
                                "Demand": {
                                    "Resource": "ElectricPower",
                                    "Amount": 0.0
                                }
                            }
                        }
                    }
                ],
                "BuildingStock": [
                    {
                        "Buildings": {
                            "CreatorClassName": "R2DSubsystemCreator",
                            "CreatorFileName": "r2d_subsystem_creator",
                            "Parameters": {
                                "Resource": [
                                    "Shelter"
                                ],
                                "R2DJSONFile_Info": "./Example 4/NorthEast_SF_Housing_Exposure.json",
                                "SubsystemNameInR2DJSON": "Buildings",
                                "AssetTypes": [
                                    "Building"
                                ],
                                "MaxNumComponents": 100
                            }
                        }
                    }
                ]
            }
        },
        "Locality 5": {
            "Coordinates": {
                "BoundingBox": [
                    [
                        -122.394309,
                        37.794821
                    ],
                    [
                        -122.391442,
                        37.777747
                    ],
                    [
                        -122.418291,
                        37.775757
                    ]
                ]
            },
            "Components": {
                "Infrastructure": [
                    {
                        "ElectricPowerSupplySystem": {
                            "CreatorClassName": "Tier1InfrastructureCreator",
                            "CreatorFileName": "tier1_infrastructure_creator",
                            "Parameters": {
                                "ComponentName": ["ElectricPowerSupplySystem"],
                                "Resource": "ElectricPower",
                                "Amount": [
                                    85
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 60
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "WaterSupplySystem": {
                            "CreatorClassName": "Tier1InfrastructureCreator",
                            "CreatorFileName": "tier1_infrastructure_creator",
                            "Parameters": {
                                "ComponentName": ["WaterSupplySystem"],
                                "Resource": "PotableWater",
                                "Amount": [
                                    610000
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 80
                                        }
                                    }
                                ],
                                "Demand": {
                                    "Resource": "ElectricPower",
                                    "Amount": 0.0
                                }
                            }
                        }
                    }
                ],
                "BuildingStock": [
                    {
                        "Buildings": {
                            "CreatorClassName": "R2DSubsystemCreator",
                            "CreatorFileName": "r2d_subsystem_creator",
                            "Parameters": {
                                "Resource": [
                                    "Shelter"
                                ],
                                "R2DJSONFile_Info": "./Example 4/NorthEast_SF_Housing_Exposure.json",
                                "SubsystemNameInR2DJSON": "Buildings",
                                "AssetTypes": [
                                    "Building"
                                ],
                                "MaxNumComponents": 100
                            }
                        }
                    }
                ]
            }
        }

Damage Input
````````````

Damage input is read from the R2DTool's output as in Example 3. The damage of the infrastructure systems is not explicitly considered, but is implicitly contained in their post-disaster supply dynamics defined in the previous section.

.. toggle::

    .. code-block:: json

        "DamageInput": {
            "FileName": "r2d_damage_input",
            "ClassName": "R2DDamageInput",
            "Parameters": {
                "DamageFile": "./Example 4/NorthEast_SF_Housing_Damage.json"
            }
        },

Resources
``````````

In addition to shelter and recovery resources considered in Example 3, Example 4 considers Functional Housing and two infrastructure resources: Electric Power and Potable Water. Functional Housing is distributed in the same way as Shelter: using the UtilityDistributionModel and the SupplierOnlyDistributionPriority object. The infrastructure resources are also distributed using UtilityDistributionModel, but components are prioritized using the RandomPriorityWithPrioritizedInterfaces class which start distributing a resource from the supplier - the infrastructure interface component - and then randomly shuffles remaining components within a locality. To ensure that an infrastructure interface component in a locality only transfer resources within that locality, IsolatingLocalitiesTransferService is introduced. Sparse distribution time stepping is applied to reduce computational time.

.. toggle::

    .. code-block:: json

        "Resources": {
            "Shelter": {
                "Group": "Utilities",
                "DistributionModel": {
                    "ClassName": "HousingDistributionModel",
                    "FileName": "housing_distribution_model",
                    "Parameters": {
                        "DistributionTimeStepping": [
                            {
                                "start": 0,
                                "end": 50,
                                "step": 1
                            },
                            {
                                "start": 50,
                                "end": 1000,
                                "step": 50
                            }
                        ]
                    }
                }
            },
            "FunctionalHousing": {
                "Group": "Utilities",
                "DistributionModel": {
                    "ClassName": "HousingDistributionModel",
                    "FileName": "housing_distribution_model",
                    "Parameters": {
                        "DistributionTimeStepping": [
                            {
                                "start": 0,
                                "end": 50,
                                "step": 1
                            },
                            {
                                "start": 50,
                                "end": 1000,
                                "step": 50
                            }
                        ]
                    }
                }
            },
            "FirstResponderEngineer": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "SeniorEngineer": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "Contractor": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "Money": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "PlanCheckEngineeringTeam": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "SitePreparationCrew": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "CleanUpCrew": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "EngineeringDesignTeam": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "DemolitionCrew": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "RepairCrew": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority",
                            "ClassName": "RandomPriority",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "RecoveryDemand"
                                ]
                            }
                        }
                    }
                }
            },
            "ElectricPower": {
                "Group": "Utilities",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority_with_prioritized_interfaces",
                            "ClassName": "RandomPriorityWithPrioritizedInterfaces",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "OperationDemand"
                                ]
                            }
                        },
                        "TransferService": "IsolatingLocalitiesTransferService"
                    }
                }
            },
            "PotableWater": {
                "Group": "Utilities",
                "DistributionModel": {
                    "ClassName": "UtilityDistributionModel",
                    "FileName": "utility_distribution_model",
                    "Parameters": {
                        "DistributionPriority": {
                            "FileName": "random_priority_with_prioritized_interfaces",
                            "ClassName": "RandomPriorityWithPrioritizedInterfaces",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "OperationDemand"
                                ]
                            }
                        },
                        "TransferService": "IsolatingLocalitiesTransferService"
                    }
                }
            },
            "IsolatingLocalitiesTransferService": {
                "Group": "TransferService",
                "DistributionModel": {
                    "ClassName":"TransferServiceDistributionModelPotentialPaths",
                    "FileName": "transfer_service_distribution_model_potential_paths",
                    "Parameters": {}
                }
            }
        },


Resilience calculators
``````````````````````

Several ReCoDeSResilienceCalculator are used in Example 4. All calculators consider Shelter, Functional Housing, Electric Power and Potable Water, but their scope is different: they either consider the entire systems (i.e., all localities) or a single locality. This allows the user to assess resilience, that is the unmet system demand, on a locality level.

.. toggle::

    .. code-block:: json

        "ResilienceCalculator": [
            {
                "ClassName": "ReCoDeSCalculator",
                "FileName": "recodes_calculator",
                "Parameters": {
                    "Scope": "All",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater"
                    ]
                }
            },
            {
                "ClassName": "ReCoDeSCalculator",
                "FileName": "recodes_calculator",
                "Parameters": {
                    "Scope": "Locality 1",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater"
                    ]
                }
            },
            {
                "ClassName": "ReCoDeSCalculator",
                "FileName": "recodes_calculator",
                "Parameters": {
                    "Scope": "Locality 2",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater"
                    ]
                }
            },
            {
                "ClassName": "ReCoDeSCalculator",
                "FileName": "recodes_calculator",
                "Parameters": {
                    "Scope": "Locality 3",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater"
                    ]
                }
            },
            {
                "ClassName": "ReCoDeSCalculator",
                "FileName": "recodes_calculator",
                "Parameters": {
                    "Scope": "Locality 4",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater"
                    ]
                }
            },
            {
                "ClassName": "ReCoDeSCalculator",
                "FileName": "recodes_calculator",
                "Parameters": {
                    "Scope": "Locality 5",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater"
                    ]
                }
            }
        ]
        }

Main
----

.. toggle::

    .. code-block:: json

        {
            "ComponentLibrary": {
                "ComponentLibraryCreatorFileName": "json_component_library_creator",
                "ComponentLibraryCreatorClassName": "JSONComponentLibraryCreator",
                "ComponentLibraryFile": "./Example 4/NorthEast_SF_Housing_Interface_Infrastructure_ComponentLibrary.json"
        },
            "System": {
                "SystemCreatorClassName": "ConcreteSystemCreator",
                "SystemCreatorFileName": "concrete_system_creator",
                "SystemClassName": "BuiltEnvironment",
                "SystemFileName": "built_environment",
                "SystemConfigurationFile": "./Example 4/NorthEast_SF_Housing_Interface_Infrastructure_Tier_2_SystemConfiguration.json"
            }
        }

Outputs
-------

Resilience assessment outputs are provided in terms of post-earthquake supply/demand/consumption dynamics for functional housing, electric power, potable water and cellular communication. The results identify how much and for how long user demand is not met, pointing out the lack of system's resilience. The results are provided for the entire system and for Locality 4 only, to illustrate that the outputs can be provided per locality.

.. figure:: ../../figures/example_4_functional_housing.png
        :alt: Functional housing supply/demand/consumption following the scenario earthquake for the considered region. Functional housing resource represents how many people are sheltered in their homes and have access to electric power, potable water and cellular communication.

        Functional housing supply/demand/consumption following the scenario earthquake. Functional housing resource represents how many people are sheltered in their homes and have access to electric power and potable water.

.. figure:: ../../figures/example_4_electric_power.png
        :alt: Electric Power post-earthquake supply/demand/consumption dynamics for the considered region.

        Electric Power post-earthquake supply/demand/consumption dynamics.

.. figure:: ../../figures/example_4_potable_water.png
        :alt: Potable Water post-earthquake supply/demand/consumption dynamics for the considered region.

        Potable Water post-earthquake supply/demand/consumption dynamics.

.. figure:: ../../figures/example_4_functional_housing_locality_1.png
        :alt: Functional housing supply/demand/consumption following the scenario earthquake for Locality 1.

        Functional housing supply/demand/consumption following the scenario earthquake for Locality 1.

.. figure:: ../../figures/example_4_electric_power_locality_1.png
        :alt: Electric Power post-earthquake supply/demand/consumption dynamics for Locality 1.

        Electric Power post-earthquake supply/demand/consumption dynamics for Locality 1.

.. figure:: ../../figures/example_4_potable_water_locality_1.png
        :alt: Potable Water post-earthquake supply/demand/consumption dynamics for Locality 1.

        Potable Water post-earthquake supply/demand/consumption dynamics for Locality 1.

.. figure:: ../../figures/example_4_recovery_animation.gif
        :alt: Simulated recovery of up to 100 buildings in 5 localities in the North-East San Francisco.

        Simulated recovery of up to 100 buildings in 5 localities in the North-East San Francisco.

Apart from figures, the analysis outputs the resilience metrics as text. Note that the simulation is probabilistic, thus the results among different runs might differ.

.. code-block:: text

    Re-CoDeS Resilience Calculator 
    Scope: All
    ----------------------------- 
    Total unmet demand: 
    Shelter: 751983.0
    FunctionalHousing: 4071202.0
    ElectricPower: 53382.52
    PotableWater: 324922950.0

    Re-CoDeS Resilience Calculator 
    Scope: Locality 1
    ----------------------------- 
    Total unmet demand: 
    Shelter: 213429.0
    FunctionalHousing: 463167.0
    ElectricPower: 0.0
    PotableWater: 37460700.0

    Re-CoDeS Resilience Calculator 
    Scope: Locality 2
    ----------------------------- 
    Total unmet demand: 
    Shelter: 71558.0
    FunctionalHousing: 85974.0
    ElectricPower: 288.32000000000005
    PotableWater: 1486650.0

    Re-CoDeS Resilience Calculator 
    Scope: Locality 3
    ----------------------------- 
    Total unmet demand: 
    Shelter: 42245.0
    FunctionalHousing: 62517.0
    ElectricPower: 278.74
    PotableWater: 3040800.0

    Re-CoDeS Resilience Calculator 
    Scope: Locality 4
    ----------------------------- 
    Total unmet demand: 
    Shelter: 423199.0
    FunctionalHousing: 1862211.0
    ElectricPower: 28780.239999999998
    PotableWater: 43567650.0

    Re-CoDeS Resilience Calculator 
    Scope: Locality 5
    ----------------------------- 
    Total unmet demand: 
    Shelter: 1552.0
    FunctionalHousing: 1597333.0
    ElectricPower: 24035.219999999998
    PotableWater: 239367150.0



