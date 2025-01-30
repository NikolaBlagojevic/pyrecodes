Example 1
=========

Example 1 illustrates how the resilience of a simple community with five components located in three localities can be assessed using **pyrecodes**. Initial damage levels are assigned to a subset of system components, simulating the effects of a disaster, and defined directly in the system configuration file. The recovery of the components is then simulated and the post-disaster system-level supply/demand/consumption dynamics are plotted, together with a gantt chart illustrating the recovery of components. Resilience is assessed by identifying the unmet system demand for electric power, communication and cooling water - more post-disaster unmet demand indicates lower resilience.

.. figure:: ../../figures/Example_1_Community.png
        :alt: Three localities community in Example 1.

        Three localities community in Example 1. 

Components considered in Example 1 are Base Transceiver Stations (BTS), Electric Power Plant (EPP), Cooling Water Facility (CWF), Building Stock Unit (BSU) and links transferring resources among components. 

Running the example
-------------------

Example 1 Jupyter notebook illustrates how to run the pyrecodes simulation and plot the post-disaster supply/demand/consumption dynamics and the components' recovery gantt chart.

Run the example online using `Google Colab <https://colab.research.google.com/github/NikolaBlagojevic/pyrecodes/blob/main/Example1_ThreeLocalityCommunity_Colab.ipynb>`_.
    
Alternatively, the example can be run locally by downloading the `Example 1 Jupyter notebook <https://github.com/NikolaBlagojevic/pyrecodes/blob/main/Example1_ThreeLocalityCommunity.ipynb>`_ and the required files from the `Example 1 folder <https://github.com/NikolaBlagojevic/pyrecodes/tree/main/Example%201>`_. 

Component library
-----------------

Component library JSON file contains the parameters for each of the considered components.

The component template parameters for BTSs are explained in more detail below. The logic is the same for other components.

There are two BTSs in the system: one that supplies 1 unit of communication service, and the other that supplies 2 units of communication service. Remaining parameters are identical. This simple example illustrates how very similar componets can be defined using slightly different templates in the component library file. An alternative would be to define their supply when system is created, as done in Example 3.

Both BTSs are instantiated using StandardiReCoDeSComponent class. Their recovery is simulated using the ComponentLevelRecoveryActivitiesModel, with a single recovery activity - repair, that takes 10 days to complete. The damage-functionality relation is defined as a reverse binary function, meaning that the component is fully functional (has a functionality level of 1) when its damage level is 0, and is non-functional (functionality level is 0) if damage level is above 0.

BTSs supply communication services, where the amount of service provided is linearly related to the component's functionality level. If the operation demand of the component is not fully met (percent of unmet demand is higher than 0), the component's supply is set to 0 - this is defined by employing the binary relation in the UnmetDemandToAmountRelation The component's operation demand is defined as a constant, meaning that the component's operation demand is independent of its functionality and is 1 unit of electric power.

The component's supply is defined as a linear function of its functionality, meaning that the component's supply is proportional to its functionality. The component's operation demand is 1 unit of electric power, with a constant FunctionalityToAmount relation, meaning that the component's operation demand is independent of its functionality.

Base Transceiver Stations
`````````````````````````

.. toggle::

    .. code-block:: json

        "BaseTransceiverStation_1": {
            "ComponentClass": {"FileName": "standard_irecodes_component", "ClassName": "StandardiReCoDeSComponent"},
                "RecoveryModel": {
                    "FileName": "component_level_recovery_activities_model",
                    "ClassName": "ComponentLevelRecoveryActivitiesModel",
                    "Parameters": {
                        "Repair": {
                            "Duration": {"Deterministic": {"Value": 10}}   
                        }                
                    },
                    "DamageFunctionalityRelation": {
                        "Type": "ReverseBinary"
                    }
                },       
                "Supply": {
                    "Communication": {
                        "Amount": 1,
                        "FunctionalityToAmountRelation": "Linear",
                        "UnmetDemandToAmountRelation": "Binary"
                    }
                },
                "OperationDemand": {
                    "ElectricPower": {
                        "Amount": 1,
                        "FunctionalityToAmountRelation": "Linear"                
                    }
                }
            },
        "BaseTransceiverStation_2": {
            "ComponentClass": {"FileName": "standard_irecodes_component", "ClassName": "StandardiReCoDeSComponent"},
            "RecoveryModel": {
                "FileName": "component_level_recovery_activities_model",
                "ClassName": "ComponentLevelRecoveryActivitiesModel",
                "Parameters": {
                    "Repair": {
                        "Duration": {"Deterministic": {"Value": 10}} 
                    }       
                },
                "DamageFunctionalityRelation": {
                    "Type": "ReverseBinary"
                }
            },       
            "Supply": {
                "Communication": {
                    "Amount": 2,
                    "FunctionalityToAmountRelation": "Linear",
                    "UnmetDemandToAmountRelation": "Binary"
                }
            },
            "OperationDemand": {
                "ElectricPower": {
                    "Amount": 1,
                    "FunctionalityToAmountRelation": "Linear"                
                }
            }
        },
            

Electric Power Plant
`````````````````````

.. toggle::

    .. code-block:: json

        
        "ElectricPowerPlant": {
            "ComponentClass": {"FileName": "standard_irecodes_component", "ClassName": "StandardiReCoDeSComponent"},
            "RecoveryModel": {
                "FileName": "component_level_recovery_activities_model",
                "ClassName": "ComponentLevelRecoveryActivitiesModel",
                "Parameters": {
                    "Repair": {
                        "Duration": {"Deterministic": {"Value": 10}}   
                    }     
                },
                "DamageFunctionalityRelation": {
                    "Type": "ReverseLinear"
                }
            },
            "Supply": {
                "ElectricPower": {
                    "Amount": 5,
                    "FunctionalityToAmountRelation": "Linear",
                    "UnmetDemandToAmountRelation": "Binary"
                }
            },
            "OperationDemand": {
                "Communication": {
                    "Amount": 1,
                    "FunctionalityToAmountRelation": "Constant"                
                },
                "CoolingWater": {
                    "Amount": 1,
                    "FunctionalityToAmountRelation": "Constant"               
                }
            }
        },
        

Cooling Water Facility
```````````````````````

.. toggle::

    .. code-block:: json
        
            "CoolingWaterFacility": {
                "ComponentClass": {"FileName": "standard_irecodes_component", "ClassName": "StandardiReCoDeSComponent"},
                "RecoveryModel": {
                    "FileName": "component_level_recovery_activities_model",
                    "ClassName": "ComponentLevelRecoveryActivitiesModel",
                    "Parameters": {
                        "Repair": {
                            "Duration": {"Deterministic": {"Value": 10}}  
                        }      
                    },
                    "DamageFunctionalityRelation": {
                        "Type": "ReverseLinear"
                    }
                },
                "Supply": {
                    "CoolingWater": {
                        "Amount": 3,
                        "FunctionalityToAmountRelation": "Linear",
                        "UnmetDemandToAmountRelation": "Binary"
                    }
                },
                "OperationDemand": {
                    "Communication": {
                        "Amount": 1,
                        "FunctionalityToAmountRelation": "Constant"
                    },
                    "ElectricPower": {
                        "Amount": 1,
                        "FunctionalityToAmountRelation": "Constant"
                    }
                }
            },

Building Stock Unit
```````````````````

.. toggle::

    .. code-block:: json
  
        "BuildingStockUnit": {
            "ComponentClass": {"FileName": "building_with_emergency_calls", "ClassName": "BuildingWithEmergencyCalls"},
            "RecoveryModel": {
                "FileName": "component_level_recovery_activities_model",
                "ClassName": "ComponentLevelRecoveryActivitiesModel",
                "Parameters": {
                    "Repair": {
                        "Duration": {"Deterministic": {"Value": 10}}  
                    }      
                },
                "DamageFunctionalityRelation": {
                    "Type": "ReverseLinear"
                }   
            },   
            "OperationDemand": {
                "Communication": {
                    "Amount": 1,
                    "FunctionalityToAmountRelation": "Constant",
                    "PostDisasterIncreaseDueToEmergencyCalls": "True"
                },
                "ElectricPower": {
                    "Amount": 1,
                    "FunctionalityToAmountRelation": "Linear"
                }
            }
        }

Link
`````

.. toggle::

    .. code-block:: json
        
        "SuperLink": {
            "ComponentClass": {"FileName": "standard_irecodes_component", "ClassName": "StandardiReCoDeSComponent"},
            "RecoveryModel": {
                "FileName": "component_level_recovery_activities_model",
                "ClassName": "ComponentLevelRecoveryActivitiesModel",
                "Parameters": {
                    "Repair": {
                        "Duration": {"Deterministic": {"Value": 10}}    
                    }    
                },
                "DamageFunctionalityRelation": {
                    "Type": "ReverseLinear"
                }   
            },
            "Supply": {
                "SuperTransferService": {
                    "Amount": 1000,
                    "FunctionalityToAmountRelation": "Linear"
                }
            }
        }
        

System configuration
--------------------

System's configuration is defined in a JSON file and consists of sections presented in the `How to use pyrecodes <../user_guide.html>`_ page.

Constants
`````````

Example 1 uses the BuiltEnvironmentSystem class which requires the definition of the start, max and disaster time step. The start time step is set to 0, max time step to 500 and disaster time step (i.e., the time step at which the damage is assigned to components) to 1.

.. toggle::

    .. code-block:: json

        {   
            "Constants": {
                "START_TIME_STEP": 0,
                "MAX_TIME_STEP": 500,
                "DISASTER_TIME_STEP": 1
            },  

Content
```````

Content section defines the components in and between localities. The coordinates of Locality 1 centroids are set to (1, 1). The locality contains one BTS, representing the communication system, and one EPP, representing the power supply system. Two link components of class SuperLink start at Locality 1 and connect to Locality 2 and 3. The content of other localities is similarly defined.

.. toggle::

    .. code-block:: json

            "Content": {
                "Locality 1": {
                    "Coordinates": {"X": 1,
                                    "Y": 1
                                },
                    "Components": {
                        "Infrastructure": [
                            {"ElectricPowerSystem": {
                                "CreatorClassName": "JSONSubsystemCreator",
                                "CreatorFileName": "json_subsystem_creator",
                                "Parameters": {
                                    "ComponentsInLocality": {
                                        "ElectricPowerPlant": 1
                                    }
                                }
                            }},
                            {"CommunicationSystem": {
                                "CreatorClassName": "JSONSubsystemCreator",
                                "CreatorFileName": "json_subsystem_creator",
                                "Parameters": {
                                    "ComponentsInLocality": {
                                        "BaseTransceiverStation_1": 1
                                    }
                                }
                            }},
                            {"Links": {
                                "CreatorClassName": "JSONSubsystemCreator",
                                "CreatorFileName": "json_subsystem_creator",
                                "Parameters": {
                                    "ComponentsBetweenLocalities": {
                                        "Locality 2": ["SuperLink"],
                                        "Locality 3": ["SuperLink"]
                                    }
                                }
                            }
                            }                    
                        ]
                    }
                },
                "Locality 2": {
                    "Coordinates": {"X": 0,
                                    "Y": 0
                                },
                    "Components": {
                        "Infrastructure": [
                            {"CoolingWaterSystem": {
                                "CreatorClassName": "JSONSubsystemCreator",
                                "CreatorFileName": "json_subsystem_creator",
                                "Parameters": {
                                    "ComponentsInLocality": {
                                        "CoolingWaterFacility": 1                            
                            }
                            }
                        }
                    },
                            {"Links": {
                                "CreatorClassName": "JSONSubsystemCreator",
                                "CreatorFileName": "json_subsystem_creator",
                                "Parameters": {
                                    "ComponentsBetweenLocalities": {
                                        "Locality 1": ["SuperLink"],
                                        "Locality 3": ["SuperLink"]
                                    }
                                }
                            }
                            }                    
                        ]
                    }
                },
                "Locality 3": {
                    "Coordinates": {"X": 2,
                                    "Y": 0
                                },
                    "Components": {
                        "Infrastructure": [
                            {"CommunicationSystem": {
                                "CreatorClassName": "JSONSubsystemCreator",
                                "CreatorFileName": "json_subsystem_creator",
                                "Parameters": {
                                    "ComponentsInLocality": {
                                        "BaseTransceiverStation_2": 1
                                }
                            }
                            }},
                            {"Links": {
                                "CreatorClassName": "JSONSubsystemCreator",
                                "CreatorFileName": "json_subsystem_creator",
                                "Parameters": {
                                    "ComponentsBetweenLocalities": {
                                        "Locality 1": ["SuperLink"],
                                        "Locality 2": ["SuperLink"]
                                    }
                                }
                            }
                            }],
                        "BuildingStock": [
                            {"Buildings": {
                                "CreatorClassName": "JSONSubsystemCreator",
                                "CreatorFileName": "json_subsystem_creator",
                                "Parameters": {
                                    "ComponentsInLocality": {
                                        "BuildingStockUnit": 1
                                }
                            }}}]
                    }
                }
            }

Damage Input
````````````

Components' damage is assigned using the ListDamageInput class, whose parameter is a list consisting of initial damage levels of components, in the same order as they are defined in the system object. In Example 1, the damage is assigned to the BTS and BSU at Locality 3, CWF at Locality 2 and EPP at Locality 1. The damage levels are set to 0.4, meaning that the components are 40% damaged.

.. toggle::

    .. code-block:: json
       
        "DamageInput": {
        "ClassName": "ListDamageInput",
        "FileName": "list_damage_input",
        "Parameters": [0.4, 0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0, 0.0]
    },  

Resources
`````````

Four resources are considered in Example 1: Electric Power, Cooling Water, Communication and SuperTransferService. Out of the four, Electric Power, Cooling Water and Communication belong to the utility resource group and are distributed among components using the UtilityDistributionModel object. Distribution priorities are defined using the ComponentBasedPriority object and parameters which specify the components' priority. Transfer service required to transfer Electric Power and Cooling Water is set as a SuperTransferService, to illustrate how transfer services are considered in **pyrecodes**. The SuperTransferService is distributed using the TransferServiceDistributionModelPotentialPathSets object.

.. toggle::

    .. code-block:: json

        "Resources": {
            "ElectricPower": {
                "Group": "Utilities",
                "DistributionModel": {"ClassName": "UtilityDistributionModel",
                                    "FileName": "utility_distribution_model",
                                    "Parameters": {
                                        "DistributionPriority": {"FileName": "component_based_priority",
                                                                "ClassName": "ComponentBasedPriority",
                                                                "Parameters": [
                                                                    ["ElectricPowerPlant", ["Locality 1"], "OperationDemand"],
                                                                    ["BaseTransceiverStation_1", ["Locality 1"], "OperationDemand"],
                                                                    ["CoolingWaterFacility", ["Locality 2"], "OperationDemand"],
                                                                    ["BaseTransceiverStation_2", ["Locality 3"], "OperationDemand"],
                                                                    ["BuildingStockUnit", ["Locality 3"], "OperationDemand"]
                                                                ]},
                                        "TransferService": "SuperTransferService"}
                                        }
                                    },    
            "CoolingWater": {  
                "Group": "Utilities",
                "DistributionModel": {"ClassName": "UtilityDistributionModel",
                                    "FileName": "utility_distribution_model",
                                    "Parameters": {
                                        "DistributionPriority": {"FileName": "component_based_priority",
                                                                "ClassName": "ComponentBasedPriority",
                                                            "Parameters": [
                                                                ["CoolingWaterFacility", ["Locality 2"], "OperationDemand"],       
                                                                ["ElectricPowerPlant", ["Locality 1"], "OperationDemand"],                            
                                                                ["BaseTransceiverStation_1", ["Locality 1"], "OperationDemand"],
                                                                ["BaseTransceiverStation_2", ["Locality 3"], "OperationDemand"],                                                                                                                
                                                                ["BuildingStockUnit", ["Locality 3"], "OperationDemand"]
                                                            ]},
                                        "TransferService": "SuperTransferService"}
                                        }
                                    },         
            "Communication": {     
                "Group": "Utilities",
                "DistributionModel": {"ClassName": "UtilityDistributionModel",
                                    "FileName": "utility_distribution_model",
                                    "Parameters": {
                                        "DistributionPriority": {"FileName": "component_based_priority",
                                                                "ClassName": "ComponentBasedPriority",
                                                        "Parameters": [
                                                            ["BaseTransceiverStation_1", ["Locality 1"], "OperationDemand"],
                                                            ["BaseTransceiverStation_2", ["Locality 3"], "OperationDemand"],
                                                            ["ElectricPowerPlant", ["Locality 1"], "OperationDemand"],
                                                            ["CoolingWaterFacility", ["Locality 2"], "OperationDemand"],                                        
                                                            ["BuildingStockUnit", ["Locality 3"], "OperationDemand"]
                                                        ]}
                                        }
                                        }
                                    },
            "SuperTransferService": {
                "Group": "TransferService",
                "DistributionModel": {
                    "ClassName": "TransferServiceDistributionModelPotentialPaths",
                    "FileName": "transfer_service_distribution_model_potential_paths",
                    "Parameters": {
                        "PathSetsFile": "./tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_potential_path_sets.json"
                    }
                }
            }       
        }  

Resilience Calculators
``````````````````````

Two resilience calculators are employed in Example 1: the ReCoDeSCalculator and the NISTGoalsCalculator.

The ReCoDeSCalculator assesses resilience by calculating the unmet demand of the system during the resilience assessment interval. This is done for the entire system (Scope: All) and for three utility resources: Electric Power, Cooling Water and Communication.

The NISTGoalsCalculator calculates the time that the system needs to reach the desired system's functionality level as specified by the resilience goal. In **pyrecodes** functionality level of a system is defined as the percent of met system demand at each time step of the resilience assessment interval. Three resilience goals are defined in Example 1, which consider the three utility resources, the entire system (as opposed to a subset of localities/components) and are set to different desired functionality levels.

.. toggle::

    .. code-block:: json

            "ResilienceCalculator": [{
                "FileName": "recodes_calculator",
                "ClassName": "ReCoDeSCalculator",
                "Parameters": {"Scope": "All", 
                            "Resources": ["ElectricPower", "CoolingWater", "Communication"]}                  
            },
                {
                "FileName": "nist_goals_calculator",
                "ClassName": "NISTGoalsCalculator",
                "Parameters": [{"Resource": "ElectricPower", "DesiredFunctionalityLevel": 0.95, "Scope": "All"},
                            {"Resource": "CoolingWater", "DesiredFunctionalityLevel": 0.9, "Scope": "All"},
                            {"Resource": "Communication", "DesiredFunctionalityLevel": 0.8, "Scope": "All"}]
            }]

Main file
---------

The main file to run Example 1 is defined as follows:

.. toggle::

    .. code-block:: json

        {
            "ComponentLibrary": {
                "ComponentLibraryCreatorFileName": "json_component_library_creator",
                "ComponentLibraryCreatorClassName": "JSONComponentLibraryCreator",
                "ComponentLibraryFile": "./Example 1/ThreeLocalitiesCommunity_ComponentLibrary.json"
            },
            "System": {
                "SystemCreatorClassName": "ConcreteSystemCreator",
                "SystemCreatorFileName": "concrete_system_creator",
                "SystemClassName": "BuiltEnvironment",
                "SystemFileName": "built_environment",
                "SystemConfigurationFile": "./Example 1/ThreeLocalitiesCommunity_SystemConfiguration.json"
            }
        }

.. note::

    Path to component library and system configuration file might differ on your local machine.

Outputs
-------

The outputs of Example 1 are plotted using the `Plotter class <../documentation/plotter_class_docs.html>`_ and should produce the following output:

.. figure:: ../../figures/example_1_power_plot.png
        :alt: Post-disaster supply/demand/consumption dynamics for electric power in the three localities community.

        Post-disaster supply/demand/consumption dynamics of electric power in the three localities community.

.. figure:: ../../figures/example_1_water_plot.png
        :alt: Post-disaster supply/demand/consumption dynamics for cooling water in the three localities community.

        Post-disaster supply/demand/consumption dynamics for cooling water in the three localities community.

.. figure:: ../../figures/example_1_communication_plot.png
        :alt: Post-disaster supply/demand/consumption dynamics for cellular communication in the three localities community.

        Post-disaster supply/demand/consumption dynamics for cellular communication in the three localities community.
    
.. figure:: ../../figures/example_1_gantt_chart.png
        :alt: Component recovery gantt chart.

        Component repair gantt chart. All damaged components are assumed to take 10 days to repair (check out their component library templates above) - these are the BTS and BSU at Locality 3, CWF at Locality 2 and EPP at Locality 1. Components that are not damaged do not need repair.


Apart from the plots, the output of Example 1 includes the resilience metrics in terms of total unmet resource demand and assessment of resilience goals in the following format:

.. code-block:: text

    Re-CoDeS Resilience Calculator 
    Scope: All
    ----------------------------- 
    Total unmet demand: 
    ElectricPower: 30.400000000000002
    CoolingWater: 11.0
    Communication: 60.082792050515444

    NIST Resilience Goals Calculator: 
    -------------------------------- 
    Resource: ElectricPower
    DesiredFunctionalityLevel: 0.95
    Scope: All
    MetAtTimeStep: 12

    Resource: CoolingWater
    DesiredFunctionalityLevel: 0.9
    Scope: All
    MetAtTimeStep: 12

    Resource: Communication
    DesiredFunctionalityLevel: 0.8
    Scope: All
    MetAtTimeStep: 12
