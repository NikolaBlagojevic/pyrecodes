Example 4
=========

Example 4 shows how infrastructure simulators can be integrated within an iRe-CoDeS system-of-systems model using the supply/demand interfaces. Such interfaces allow the integration of third-party infrastructure simulators to capture their interdependencies and their impact on buildings' functional recovery. Interfaces are tiered to accomodate infrastructure managers privacy and/or security concerns. Interface application is illustrated by extending the Example 3 North-East San Francisco Case Study to include the impact of infrastructure systems on building's functionality. Further details are available `here <https://link.springer.com/article/10.1007/s10669-023-09931-0>`_.

.. figure:: ../../figures/Example_4_infrastructure_interfaces.png
        :alt: Tiered supply/demand interfaces for infrastructure systems

        Tiered supply/demand infrastructure simulator interfaces. Tier 1 interface requires post-event resource supply dynamics defined per locality. Tier 2 interface additionally requires the information on the resources that the infrastructure system needs to operate on a locality level. Tier 3 interfaces needs component-level supply/demand dynamics.

Running the example
-------------------

Example 4 Jupyter notebook illustrates how to run the pyrecodes simulation and plot the post-disaster supply/demand/consumption dynamics and the components' recovery gantt chart, as well as animate the building recovery process.

Run the example online using `Google Colab <https://colab.research.google.com/github/NikolaBlagojevic/pyrecodes/blob/main/Example4_NorthEast_SF_Interfaces_Colab.ipynb>`_.
    
Alternatively, the example can be run locally by downloading the `Example 4 Jupyter notebook <https://github.com/NikolaBlagojevic/pyrecodes/blob/main/Example4_NorthEast_SF_Interfaces.ipynb>`_ and the required files from the `Example 4 folder <https://github.com/NikolaBlagojevic/pyrecodes/tree/main/Example%204>`_. 

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
                "ComponentClass": "StandardiReCoDeSComponent",
                "RecoveryModel": {
                    "Type": "NoRecoveryActivityModel",
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

DS0 Residential Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS0_ResidentialBuilding": {
                "ComponentClass": "StandardiReCoDeSComponent",
                "RecoveryModel": {
                    "Type": "NoRecoveryActivityModel",
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
                    },
                    "CellularCommunication": {
                        "Amount": 0,
                        "FunctionalityToAmountRelation": "Linear"
                    }
                }
            }

DS1 Residential Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS1_ResidentialBuilding": {
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
                    },
                    "CellularCommunication": {
                        "Amount": 0,
                        "PostDisasterIncreaseDueToEmergencyCalls": "True",
                        "FunctionalityToAmountRelation": "Linear"
                    }
                }
            }

DS2 Residential Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS2_ResidentialBuilding": {
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
                    },
                    "CellularCommunication": {
                        "Amount": 0,
                        "PostDisasterIncreaseDueToEmergencyCalls": "True",
                        "FunctionalityToAmountRelation": "Linear"
                    }
                }
            }


DS3 Residential Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS3_ResidentialBuilding": {
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
                },
                "CellularCommunication": {
                    "Amount": 0,
                    "PostDisasterIncreaseDueToEmergencyCalls": "True",
                    "FunctionalityToAmountRelation": "Linear"
                }
            }
        }

DS4 Residential Building
````````````````````````

.. toggle::

    .. code-block:: json

        "DS4_ResidentialBuilding": {
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
                },
                "CellularCommunication": {
                    "Amount": 0,
                    "PostDisasterIncreaseDueToEmergencyCalls": "True",
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
            "ComponentClass": "InfrastructureInterface",
            "RecoveryModel": {
                "Type": "InfrastructureInterfaceRecoveryModel",
                "Parameters": {},
                "DamageFunctionalityRelation": "MultipleSteps"
            },
            "Supply": {
                "ElectricPower": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Linear",
                    "UnmetDemandToAmountRelation": "Binary"
                }
            },
            "OperationDemand": {
                "CellularCommunication": {
                    "Amount": 0.0,
                    "FunctionalityToAmountRelation": "Constant"
                }
            }
        }  

Water Supply System
````````````````````````````

.. toggle::

    .. code-block:: json

        "WaterSupplySystem": {
            "ComponentClass": "InfrastructureInterface",
            "RecoveryModel": {
                "Type": "InfrastructureInterfaceRecoveryModel",
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
                },
                "CellularCommunication": {
                    "Amount": 0.0,
                    "FunctionalityToAmountRelation": "Binary"
                }
            }
        }

Cellular Communication System
`````````````````````````````

.. toggle::

    .. code-block:: json

        "CellularCommunicationSystem": {
            "ComponentClass": "InfrastructureInterface",
            "RecoveryModel": {
                "Type": "InfrastructureInterfaceRecoveryModel",
                "Parameters": {},
                "DamageFunctionalityRelation": ""
            },
            "Supply": {
                "CellularCommunication": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Linear",
                    "UnmetDemandToAmountRelation": "Binary"
                }
            },
            "OperationDemand": {
                "ElectricPower": {
                    "Amount": 0.0,
                    "FunctionalityToAmountRelation": "Constant"
                },
                "CellularCommunication": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Binary"
                }
            }
        }

System configuration
--------------------

System configuration file in Example 4 is very similar to the one used in Example 3. The only differences come from the consideration of infrastructure systems. These differences are outlined next.


Constants
`````````

Novel constants introduced in Example 4 are contained in the **DEMAND_PER_PERSON** key. They include the values used to estimate operational demand of residential buildings for infrastructure services. Such values are obtained by multiplying the number of residents in a building at a time step of the resilience assessment interval and the resource demand per person. Remaining constants are explained in Example 3.

.. toggle::

    .. code-block:: json

        "Constants": {
            "START_TIME_STEP": 0,
            "MAX_TIME_STEP": 3650,
            "DISASTER_TIME_STEP": 1,
            "DS4_REPAIR_DURATION": 240,
            "MAX_REPAIR_CREW_DEMAND_PER_BUILDING": 50,
            "MAX_RESIDENTS_PER_BUILDING": 2000,
            "HOUSING_RESOURCES": ["Shelter"],
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
                "PotableWater": 150,
                "CellularCommunication": 0.033
            }
        },

Content
```````

Example 4 divides the considered region, north-east San Francisco, into 5 localities, defined by their bounding box coordinates, as opposed to storing all components in a single locality as in Example 3. The effect of infrastructure systems is captured through supply/demand interfaces defined at the locality level. For each of the three considered infrastructure systems, their post-earthquake supply dynamics are defined in terms of the amount of resources they can provide to the components in their locality and the times at which these amounts are restored. For example, the electric power supply system in Locality 1 provides 150MWh from day 0 - immediately after the earthquake, and increase the supply to 450MWh, 60 days after the earthquake.

.. hint::

    The number of buildings per locality is limited to 50 to reduce the computational time of the example. This number can be increased to consider more buildings in the region.

.. toggle::

    .. code-block:: json

        "Content": {
            "Locality 1": {
                "ComponentsInLocality": {
                    "Coordinates": {
                        "BoundingBox": {
                            "Latitude": [
                                37.809410,
                                37.809991,
                                37.795523,
                                37.791310
                            ],
                            "Longitude": [
                                -122.426388,
                                -122.397014,
                                -122.391161,
                                -122.422544
                            ]
                        }
                    },
                    "RecoveryResourceSuppliers": [
                        "EmergencyResponseCenter"
                    ],
                    "Infrastructure": [
                        {
                            "ElectricPowerSupplySystem": {
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
                        },
                        {
                            "WaterSupplySystem": {
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
                                    "Amount": 2.5
                                }
                            }
                        },
                        {
                            "CellularCommunicationSystem": {
                                "Resource": "CellularCommunication",
                                "Amount": [
                                    750
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 0
                                        }
                                    }
                                ],
                                "Demand": {
                                    "Resource": "ElectricPower",
                                    "Amount": 0.5
                                }
                            }
                        }
                    ],
                    "BuildingsInfoFolder": "./Example 3/R2D Output/",
                    "BuildingIDsRange": [
                        8000,
                        9000
                    ],
                    "MaxNumBuildings": 50,
                    "AreaPerPerson": 541
                }
            },
            "Locality 2": {
                "ComponentsInLocality": {
                    "Coordinates": {
                        "BoundingBox": {
                            "Latitude": [
                                37.790065,
                                37.803214,
                                37.804204,
                                37.791310
                            ],
                            "Longitude": [
                                -122.432440,
                                -122.432965,
                                -122.425129,
                                -122.422585
                            ]
                        }
                    },
                    "RecoveryResourceSuppliers": [],
                    "Infrastructure": [
                        {
                            "ElectricPowerSupplySystem": {
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
                        },
                        {
                            "WaterSupplySystem": {
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
                                    "Amount": 1.5
                                }
                            }
                        },
                        {
                            "CellularCommunicationSystem": {
                                "Resource": "CellularCommunication",
                                "Amount": [
                                    130
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 5
                                        }
                                    }
                                ],
                                "Demand": {
                                    "Resource": "ElectricPower",
                                    "Amount": 0.2
                                }
                            }
                        }
                    ],
                    "BuildingsInfoFolder": "./Example 3/R2D Output/",
                    "BuildingIDsRange": [
                        8000,
                        9000
                    ],
                    "MaxNumBuildings": 50,
                    "AreaPerPerson": 541
                }
            },
            "Locality 3": {
                "ComponentsInLocality": {
                    "Coordinates": {
                        "BoundingBox": {
                            "Latitude": [
                                37.791342,
                                37.777871,
                                37.776836,
                                37.790065
                            ],
                            "Longitude": [
                                -122.422585,
                                -122.419838,
                                -122.431406,
                                -122.432644
                            ]
                        }
                    },
                    "RecoveryResourceSuppliers": [],
                    "Infrastructure": [
                        {
                            "ElectricPowerSupplySystem": {
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
                        },
                        {
                            "WaterSupplySystem": {
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
                                    "Amount": 0.5
                                }
                            }
                        },
                        {
                            "CellularCommunicationSystem": {
                                "Resource": "CellularCommunication",
                                "Amount": [
                                    100
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 5
                                        }
                                    }
                                ],
                                "Demand": {
                                    "Resource": "ElectricPower",
                                    "Amount": 0.1
                                }
                            }
                        }
                    ],
                    "BuildingsInfoFolder": "./Example 3/R2D Output/",
                    "BuildingIDsRange": [
                        8000,
                        9000
                    ],
                    "MaxNumBuildings": 50,
                    "AreaPerPerson": 541
                }
            },
            "Locality 4": {
                "ComponentsInLocality": {
                    "Coordinates": {
                        "BoundingBox": {
                            "Latitude": [
                                37.791388,
                                37.794985,
                                37.775381
                            ],
                            "Longitude": [
                                -122.422568,
                                -122.394280,
                                -122.419321
                            ]
                        }
                    },
                    "RecoveryResourceSuppliers": [],
                    "Infrastructure": [
                        {
                            "ElectricPowerSupplySystem": {
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
                        },
                        {
                            "WaterSupplySystem": {
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
                                    "Amount": 5
                                }
                            }
                        },
                        {
                            "CellularCommunicationSystem": {
                                "Resource": "CellularCommunication",
                                "Amount": [
                                    1600
                                ],
                                "RestoredIn": [
                                    {
                                        "Deterministic": {
                                            "Value": 5
                                        }
                                    }
                                ],
                                "Demand": {
                                    "Resource": "ElectricPower",
                                    "Amount": 1
                                }
                            }
                        }
                    ],
                    "BuildingsInfoFolder": "./Example 3/R2D Output/",
                    "BuildingIDsRange": [
                        8000,
                        9000
                    ],
                    "MaxNumBuildings": 50,
                    "AreaPerPerson": 541
                }
            },
            "Locality 5": {
                "ComponentsInLocality": {
                    "Coordinates": {
                        "BoundingBox": {
                            "Latitude": [
                                37.794821,
                                37.777747,
                                37.775757
                            ],
                            "Longitude": [
                                -122.394309,
                                -122.391442,
                                -122.418291
                            ]
                        }
                    },
                    "RecoveryResourceSuppliers": [],
                    "Infrastructure": [
                        {
                            "ElectricPowerSupplySystem": {
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
                        },
                        {
                            "WaterSupplySystem": {
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
                                    "Amount": 1.5
                                }
                            }
                        },
                        {
                            "CellularCommunicationSystem": {
                                "Resource": "CellularCommunication",
                                "Amount": [
                                    140
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
                                    "Amount": 0.2
                                }
                            }
                        }
                    ],
                    "BuildingsInfoFolder": "./Example 3/R2D Output/",
                    "BuildingIDsRange": [
                        8000,
                        9000
                    ],
                    "MaxNumBuildings": 50,
                    "AreaPerPerson": 541
                }
            }
        },


Damage Input
````````````

Damage input is read from the R2DTool's output in the same manner as in Example 3. The damage of the infrastructure systems is not explicitly considered, but is implicitly contained in their post-disaster supply dynamics defined in the previous section.

.. toggle::

    .. code-block:: json

        "DamageInput": {
            "Type": "R2DDamageInput",
            "Parameters": {
                "ScenarioID": 1
            }
        },

Resources
``````````

In addition to Shelter and recovery resources considered in Example 3, Example 4 considers Functional Housing and three infrastructure resources: Electric Power, Potable Water and Communication. Functional Housing is distributed in the same way as Shelter: using the UtilityDistributionModel and the SupplierOnlyDistributionPriority object. The infrastructure resources are also distributed using UtilityDistributionModel, but components are prioritized using the RandomPriorityWithPrioritizedInterfaces class which start distributing a resource from the supplier - the infrastructure interface component - and then randomly shuffles remaining components within a locality. To ensure that an infrastructure interface component in a locality only transfer resources within that locality, IsolatingLocalitiesTransferService is introduced.

.. toggle::

    .. code-block:: json

        "Resources": {
            "Shelter": {
                "Group": "Utilities",
                "DistributionModel": {
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "SupplierOnlyDistributionPriority",
                            "Parameters": {}
                        }
                    }
                }
            },
            "FunctionalHousing": {
                "Group": "Utilities",
                "DistributionModel": {
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "SupplierOnlyDistributionPriority",
                            "Parameters": {}
                        }
                    }
                }
            },
            "FirstResponderEngineer": {
                "Group": "RecoveryResources",
                "DistributionModel": {
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriority",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriorityWithPrioritizedInterfaces",
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
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriorityWithPrioritizedInterfaces",
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
            "CellularCommunication": {
                "Group": "Utilities",
                "IsCommunicationResource": "True",
                "DistributionModel": {
                    "Type": "UtilityDistributionModel",
                    "Parameters": {
                        "DistributionPriority": {
                            "Type": "RandomPriorityWithPrioritizedInterfaces",
                            "Parameters": {
                                "Seed": 42.0,
                                "DemandType": [
                                    "OperationDemand"
                                ]
                            }
                        },
                        "TransferService": "IsolatingLocalitiesTransferService",
                        "IsCommunicationResource": "True"
                    }
                }
            },
            "IsolatingLocalitiesTransferService": {
                "Group": "TransferService",
                "DistributionModel": {
                    "Type": "TransferServiceDistributionModelPotentialPathSets",
                    "Parameters": {
                        "PathSetsFile": "./Example 4/potential_path_sets.json"
                    }
                }
            }
        },


Resilience calculators
``````````````````````

Several ReCoDeSResilienceCalculator are used in Example 4. All calculators consider Shelter, Functional Housing, Electric Power, Potable Water and Cellular Communication, but their scope is different: they either consider the entire systems (i.e., all localities) or a single locality. This allows the user to assess resilience, that is the unmet system demand, on a locality level.

.. toggle::

    .. code-block:: json

        "ResilienceCalculator": [
            {
                "Type": "ReCoDeSResilienceCalculator",
                "Parameters": {
                    "Scope": "All",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater",
                        "CellularCommunication"
                    ]
                }
            },
            {
                "Type": "ReCoDeSResilienceCalculator",
                "Parameters": {
                    "Scope": "Locality 1",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater",
                        "CellularCommunication"
                    ]
                }
            },
            {
                "Type": "ReCoDeSResilienceCalculator",
                "Parameters": {
                    "Scope": "Locality 2",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater",
                        "CellularCommunication"
                    ]
                }
            },
            {
                "Type": "ReCoDeSResilienceCalculator",
                "Parameters": {
                    "Scope": "Locality 3",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater",
                        "CellularCommunication"
                    ]
                }
            },
            {
                "Type": "ReCoDeSResilienceCalculator",
                "Parameters": {
                    "Scope": "Locality 4",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater",
                        "CellularCommunication"
                    ]
                }
            },
            {
                "Type": "ReCoDeSResilienceCalculator",
                "Parameters": {
                    "Scope": "Locality 5",
                    "Resources": [
                        "Shelter",
                        "FunctionalHousing",
                        "ElectricPower",
                        "PotableWater",
                        "CellularCommunication"
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
                "ComponentLibraryCreatorClass": "JSONComponentLibraryCreator",
                "ComponentLibraryFile": "./Example 4/NorthEast_SF_Housing_Interface_Infrastructure_ComponentLibrary.json"
            },
            "System": {
                "SystemCreatorClass": "R2DSystemWithInterfacesCreator",
                "SystemClass": "BuiltEnvironmentSystem",
                "SystemConfigurationFile": "./Example 4/NorthEast_SF_Housing_Interface_Infrastructure_Interdependent_SystemConfiguration.json"
            }
        }

Outputs
-------

Resilience assessment outputs are provided in terms of post-earthquake supply/demand/consumption dynamics for functional housing, electric power, potable water and cellular communication. The results identify how much and for how long user demand is not met, pointing out the lack of system's resilience. The results are provided for the entire system and for Locality 4 only, to illustrate that the outputs can be provided per locality.

.. figure:: ../../figures/example_4_localities_max_50_buildings.png
        :alt: Localities in the considered region.

        Localities in the considered region. Dark blue colored buildings are in Locality 1, light blue in Locality 2, ligth red in Locality 3, dark red in Locality 4 and purple in Locality 5.

.. figure:: ../../figures/example_4_functional_housing_all.png
        :alt: Functional housing supply/demand/consumption following the scenario earthquake for the considered region. Functional housing resource represents how many people are sheltered in their homes and have access to electric power, potable water and cellular communication.

        Functional housing supply/demand/consumption following the scenario earthquake for the considered region. Functional housing resource represents how many people are sheltered in their homes and have access to electric power, potable water and cellular communication.

.. figure:: ../../figures/example_4_electric_power_all.png
        :alt: Electric Power post-earthquake supply/demand/consumption dynamics for the considered region.

        Electric Power post-earthquake supply/demand/consumption dynamics for the considered region.

.. figure:: ../../figures/example_4_potable_water_all.png
        :alt: Potable Water post-earthquake supply/demand/consumption dynamics for the considered region.

        Potable Water post-earthquake supply/demand/consumption dynamics for the considered region.

.. figure:: ../../figures/example_4_communication_all.png
        :alt: Cellular Communication post-earthquake supply/demand/consumption dynamics for the considered region.

        Cellular Communication post-earthquake supply/demand/consumption dynamics for the considered region.

.. figure:: ../../figures/example_4_functional_housing_locality_4.png
        :alt: Functional housing supply/demand/consumption following the scenario earthquake for Locality 4.

        Functional housing supply/demand/consumption following the scenario earthquake for Locality 4.

.. figure:: ../../figures/example_4_electric_power_locality_4.png
        :alt: Electric Power post-earthquake supply/demand/consumption dynamics for Locality 4.

        Electric Power post-earthquake supply/demand/consumption dynamics for Locality 4.

.. figure:: ../../figures/example_4_potable_water_locality_4.png
        :alt: Potable Water post-earthquake supply/demand/consumption dynamics for Locality 4.

        Potable Water post-earthquake supply/demand/consumption dynamics for Locality 4.

.. figure:: ../../figures/example_4_communication_locality_4.png
        :alt: Cellular Communication post-earthquake supply/demand/consumption dynamics for Locality 4.

        Cellular Communication post-earthquake supply/demand/consumption dynamics for Locality 4.

Apart from figures, the analysis outputs the resilience metrics as text. Note that the simulation is probabilistic, thus the results among different runs might differ.

.. code-block:: text

    Re-CoDeS Resilience Calculator 
    Scope: All
    ----------------------------- 
    Total unmet demand: 
    Shelter: 2442513.0
    FunctionalHousing: 3538479.0
    ElectricPower: 12498.739999999998
    PotableWater: 152223900.0
    CellularCommunication: 75282.58874280643

    Re-CoDeS Resilience Calculator 
    Scope: Locality 1
    ----------------------------- 
    Total unmet demand: 
    Shelter: 99197.0
    FunctionalHousing: 435145.0
    ElectricPower: 0.0
    PotableWater: 50392200.0
    CellularCommunication: 1848.5171499241221

    Re-CoDeS Resilience Calculator 
    Scope: Locality 2
    ----------------------------- 
    Total unmet demand: 
    Shelter: 164184.0
    FunctionalHousing: 174072.0
    ElectricPower: 224.96
    PotableWater: 1483200.0
    CellularCommunication: 2107.391296466136

    Re-CoDeS Resilience Calculator 
    Scope: Locality 3
    ----------------------------- 
    Total unmet demand: 
    Shelter: 113905.0
    FunctionalHousing: 147057.0
    ElectricPower: 462.44000000000005
    PotableWater: 4972800.0
    CellularCommunication: 2478.392991861871

    Re-CoDeS Resilience Calculator 
    Scope: Locality 4
    ----------------------------- 
    Total unmet demand: 
    Shelter: 2062891.0
    FunctionalHousing: 2372448.0
    ElectricPower: 6797.139999999999
    PotableWater: 46433550.0
    CellularCommunication: 53510.24260081496

    Re-CoDeS Resilience Calculator 
    Scope: Locality 5
    ----------------------------- 
    Total unmet demand: 
    Shelter: 2336.0
    FunctionalHousing: 409757.0
    ElectricPower: 5014.2
    PotableWater: 48942150.0
    CellularCommunication: 15338.044703739364




