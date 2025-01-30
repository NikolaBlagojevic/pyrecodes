Example 3
=========

Example 3 shows how **pyrecodes** can integrate with the `SimCenter's R2DTool <https://github.com/NHERI-SimCenter/R2DTool>`_, automatically build a **pyrecodes** model based on R2DTool's outputs and assess housing resilience of a community to a scenario earthquake. 

.. figure:: ../../figures/Example_3_NorthEastSF.png
        :alt: North-East San Francisco buildings considered in Example 3.

        North-East San Francisco buildings considered in Example 3.

Running the example
-------------------

Example 3 Jupyter notebook illustrates how to run the pyrecodes simulation and plot the post-disaster supply/demand/consumption dynamics and the components' recovery gantt chart, as well as animate the building recovery process.

Run the example online using `Google Colab <https://colab.research.google.com/github/NikolaBlagojevic/pyrecodes/blob/main/Example3_NorthEast_SF_Housing_Colab.ipynb>`_.
    
Alternatively, the example can be run locally by downloading the `Example 3 Jupyter notebook <https://github.com/NikolaBlagojevic/pyrecodes/blob/main/Example3_NorthEast_SF_Housing.ipynb>`_ and the required files from the `Example 3 folder <https://github.com/NikolaBlagojevic/pyrecodes/tree/main/Example%203>`_.

Example description
-------------------

The example is based on `R2DTool's Example 1 <https://nheri-simcenter.github.io/R2D-Documentation/common/user_manual/examples/desktop/E1BasicHAZUS/README.html>`_. R2D Tool outputs initial post-earthquake damage states of all buildings in the considered region following a hypothetical earthquake. **pyrecodes** takes this information and simulates regional recovery considering impeding factors and resource constraints. Further details can be found `here <https://doi.org/10.1016/j.rcns.2022.03.001>`_.

Building recovery activities are conditioned on the initial building damage state and are defined in the component library file, as illustrated in the following figure.

.. figure:: ../../figures/Example_3_recovery_activities.png
        :alt: Building recovery activities conditioned on the initial post-earthquake damage state.

        Building recovery activities conditioned on the initial post-earthquake damage state.

Component library
-----------------

Components considered in Example 3 are the Emergency Response Center representing a supplier of recovery resources, such as engineers, workers and finances, and buildings. As functionality and recovery activities differ among buildings depending on their initial damage state, different component templates are defined for buildings in different initial post-earthquake damage states. The component templates follow the structure presented in the `How to use pyrecodes <./user_guide.html>`_ page.

.. note::

    Certain building parameters are different from one building to another, such as the shelter capacity which depends on the total area of the building in this example. These parameters are given dummy values in the component library file and are set when system is created in the SystemCreator class based on information provided from the R2DTool's outputs.

Emergency Response Center
`````````````````````````

Emergency Response Center component is a StandardiReCoDeSComponent object that is assumed not to experience damage due to the earthquake. Thus, its recovery model is a NoRecoveryActivityModel object and it provides the supply of recovery resources to components that are recovering.

.. toggle::

    .. code-block:: json

        {
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
                        "Amount": 500,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "SeniorEngineer": {
                        "Amount": 500,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "Contractor": {
                        "Amount": 500,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "Money": {
                        "Amount": 5500000000,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "PlanCheckEngineeringTeam": {
                        "Amount": 200,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "SitePreparationCrew": {
                        "Amount": 200,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "CleanUpCrew": {
                        "Amount": 200,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "EngineeringDesignTeam": {
                        "Amount": 500,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "DemolitionCrew": {
                        "Amount": 100,
                        "FunctionalityToAmountRelation": "Linear"
                    },
                    "RepairCrew": {
                        "Amount": 500,
                        "FunctionalityToAmountRelation": "Linear"
                    }
                }
            },

DS0 Building
`````````````````````````

A Building component in DS0 damage state experiences no damage and thus its recovery model is a NoRecoveryActivityModel object. The building provides shelter to its residents which is set to 0 in the component template, and set to it actual value during system creation in the SystemCreator class. The demand for shelter services, imposed by people that live in the building is placed in the component's operation demand and is assumed to be equal to the pre-earthquake shelter supply. 

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
                    }
                },
                "OperationDemand": {
                    "Shelter": {
                        "Amount": 0,
                        "FunctionalityToAmountRelation": "Constant"
                    }
                }
            },

DS1 Building
`````````````````````````

Building in Damage State 1 experiences minor damage and goes through several recovery activities until repaired, as shown in the figure above. However, it's ability to provide shelter to its residents is not decreased due to damage, and thus its damage-functionality relation is constant - functionality is always 1 regardless of the damage level. The recovery activities are defined in the RecoveryModel section of the component template. The duration of each activity is defined using a lognormal distribution. The demand for recovery resources is defined in the Demand section of the recovery activity. These values are constant among all DS1 buildings. However, repair duration and cost differs among DS1 buildings and is set during system creation in the SystemCreator class based on the R2DTool's output. Preceding activities for a recovery activity include all recovery activities that need to be performed before the current activity can start.

.. toggle:: 

    .. code-block:: json

        "DS1_Building": {
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
                }
            },
            "OperationDemand": {
                "Shelter": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Constant"
                }
            }
        },

DS2 Building
`````````````````````````

Damage state 2 building has a more complex recovery activities sequence than DS1 buildings as defined in its recovery model. Its functionality and thus its shelter capacity is reduced until the component's damage is eliminated, thus damage-functionality relation is a ReverseBinary object. Duration and resource demand of recovery activities is the same among all DS2 buildings, apart from the repair duration and financing demand (i.e., the repair costs) - these are set during system creation based on R2DTool's output.

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
                }
            },
            "OperationDemand": {
                "Shelter": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Constant"
                }
            }
        },

DS3 Building
`````````````````````````

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
                }
            },
            "OperationDemand": {
                "Shelter": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Constant"
                }
            }
        },

DS4 Building
`````````````````````````

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
                }
            },
            "OperationDemand": {
                "Shelter": {
                    "Amount": 0,
                    "FunctionalityToAmountRelation": "Constant"
                }
            }
        }

System configuration
--------------------

Sections of the system configuration file as presented in the `How to use pyrecodes <./user_guide.html>`_ are outlined next.

Constants
`````````

The starting time step of the recovery simulation is set to day 0, time step is a day, and the maximal duration is set at 3650 time steps. Building damage is assigned on day 1, to simulate the scenario earthquake. If the simulation is taking too long, one can set the maximal time step to a lower value.

Apart from these three constants that are required to create a system in **pyrecodes**, the R2DSubsystemCreator class requires several additional constants. These are:

- maximal number of repair crews that can be assigned to a building, which is set to 50.
- name of all housing resources
- the repair crew demand per square foot of building area, which is set to 5400 for DS1 and DS2 buildings and to 2700 for DS3 and DS4 buildings.
- the default repair duration distribution, which is set to a lognormal distribution with median 0 and dispersion 0.3. The median is set to its proper value during system creation, 0 is a placeholder value.

.. toggle::

    .. code-block:: json

        "Constants": {
            "START_TIME_STEP": 0,
            "MAX_TIME_STEP": 3650,
            "DISASTER_TIME_STEP": 1,
            "MAX_REPAIR_CREW_DEMAND_PER_BUILDING": 50,
            "HOUSING_RESOURCES": [
                "Shelter"
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
            }
        }

Content
```````

Example 3 places all components in a single locality - Locality 1. The spatial extent of Locality 1 is defined as a bounding box. All components whose centroid, as defined in the R2DTool's output, falls within the bounding box are placed in Locality 1. The bounding box is defined by the latitude and longitude of its four corners. The **EmergencyResponseCenter** component is the supplier of recovery resources for components in Locality 1. Sparse recovery time stepping for buildings is employed to reduce computational time.

.. hint::

    The number of buldings is limited to 100 to reduce the computational time of the example. This number can be increased to consider all buildings in the region.

.. toggle::

    .. code-block:: json

        "Content": {
            "Locality 1": {
            "Coordinates": {
                "BoundingBox":   
                    [[-122.43, 37.78], [-122.38, 37.78], [-122.38, 37.82], [-122.43, 37.82]] 
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
                "BuildingStock": [
                    {
                        "Buildings": {
                            "CreatorClassName": "R2DSubsystemCreator",
                            "CreatorFileName": "r2d_subsystem_creator",
                            "Parameters": {
                                "Resource": [
                                    "Shelter"
                                ],
                                "R2DJSONFile_Info": "./Example 3/NorthEast_SF_Housing_Exposure.json",
                                "SubsystemNameInR2DJSON": "Buildings",
                                "AssetTypes": [
                                    "Building"
                                ],
                                "MaxNumComponents": 10000,
                                "RecoveryTimeStepping": [
                                    {
                                        "start": 0,
                                        "end": 100,
                                        "step": 1
                                    },
                                    {
                                        "start": 100,
                                        "end": 1000,
                                        "step": 10
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }

Damage Input
````````````
Component damage is provided in the R2DTool's output and is loaded using the **R2DDamageInput** class in **pyrecodes**. The damage file is provided in the parameters section of the DamageInput object.

.. toggle::

    .. code-block:: json

        "DamageInput": {
            "FileName": "r2d_damage_input",
            "ClassName": "R2DDamageInput",
            "Parameters": {
                "DamageFile": "./Example 3/NorthEast_SF_Housing_Damage.json"
            }
        },

Resources
`````````

Considered resources are several recovery resources (e.g., engineers, workers, finances, contractors) and shelter services. These resources are distributed using UtilityDistributionModel with randomly prioritized components using the RandomPriority class that meet component's recovery demand.


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
            }
        },

Resilience calculators
``````````````````````

ReCoDeSResilienceCalculator and NISTGoalsResilienceCalculator are employed in Example 3. The scope of both calculators is the entire system. 

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
                        "FirstResponderEngineer",
                        "RepairCrew"
                    ]
                }
            },
            {
                "ClassName": "NISTGoalsCalculator",
                "FileName": "nist_goals_calculator",
                "Parameters": [
                    {
                        "Resource": "Shelter",
                        "DesiredFunctionalityLevel": 0.95
                    }
                ]
            }
        ]
        }

Main
-----

.. toggle::

    .. code-block:: json

        {
            "ComponentLibrary": {
                "ComponentLibraryCreatorFileName": "json_component_library_creator",
                "ComponentLibraryCreatorClassName": "JSONComponentLibraryCreator",
                "ComponentLibraryFile": "./Example 3/NorthEast_SF_Housing_ComponentLibrary.json"
            },
            "System": {
                "SystemCreatorClassName": "ConcreteSystemCreator",
                "SystemCreatorFileName": "concrete_system_creator",
                "SystemClassName": "BuiltEnvironment",
                "SystemFileName": "built_environment",
                "SystemConfigurationFile": "./Example 3/NorthEast_SF_Housing_SystemConfiguration.json"
            }
        }

.. note::

    Path to component library and system configuration file might differ on your local machine.

   
Outputs
-------

The outputs of the housing resilience assessment include the post-earthquake change in the capacity of the building stock to shelter its residents. This is shown in the following figure for the 100 buildings considered in Example 3. As the regional recovery simulation considers resource constraints, an example of a resource ihndering recovery is shown as well: the post-earthquake supply/demand for repair crews. The blue shaded area points to the amount and duration of unmet demand for repair crews in the repair crew supply/demand plot - whenever there is unmet demand for repair crews there is a building waiting to be repaired, and thus the recovery of shelter supply is hindered.

.. figure:: ../../figures/example_3_shelter.png
    :alt: Shelter supply/demand.

    Post-earthquake recovery of shelter supply of the 100 buildings considered in Example 3.

.. figure:: ../../figures/example_3_repair_crews.png
    :alt: Repair crew supply/demand.

    Post-earthquake supply and demand for repair crews.

.. figure:: ../../figures/example_3_gantt_chart.png
    :alt: Gantt chart illustrating the recovery of 20 damaged buildings.

    Gantt chart illustrating the progress of recovery activities for 20 damaged buildings.

.. figure:: ../../figures/example_3_recovery_animation.gif
    :alt: Simulated recovery of housing in North-East San Francisco.

    Simulated recovery of housing in North-East San Francisco.

Apart from the figures, the outputs of the resilience assesment indicate the total unmet resource demand and the time needed to meet the resilience goal specified in the ResilienceCalculator parameters in the system configuration file. First dictionary shows the results of the first ReCoDeSResilienceCalculator resilience calculator: the total unmet resource demand for selected resources. The second NISTResilienceGoals resilience calculator shows the time needed to meet the specified resilience goal. Note that the simulation is probabilistic, thus the results among different runs might differ.

.. code-block:: python

    Re-CoDeS Resilience Calculator 
    Scope: All
    ----------------------------- 
    Total unmet demand: 
    Shelter: 2567625.0
    FirstResponderEngineer: 0.0
    RepairCrew: 237951.0
    Money: 0.0

    NIST Resilience Goals Calculator: 
    -------------------------------- 
    Resource: Shelter
    Scope: All
    DesiredFunctionalityLevel: 0.95
    MetAtTimeStep: 321


    


