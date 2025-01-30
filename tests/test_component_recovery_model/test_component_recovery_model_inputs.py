RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY = {"Type": "ComponentLevelRecoveryActivitiesModel",
                                 "Parameters": {"Repair": {"Duration": {"Deterministic": {"Value": 10}},
                                                           "Demand": [{"Resource": "RepairCrew", "Amount": 10}], }},
                                 "DamageFunctionalityRelation": {"Type": "ReverseLinear"}}
    
RECOVERY_TIME_STEPS_DENSE = list(range(500))
RECOVERY_TIME_STEPS_SPARSE = list(range(0, 500, 5))

RECOVERY_MODEL_PARAMETERS_MULTIPLE_ACTIVITIES = {"Type": "ComponentLevelRecoveryActivitiesModel",
                                 "Parameters": {
                                     "RapidInspection": {
                                         "Duration": {"Lognormal": {"Median": 1, "Dispersion": 0.0}},
                                         "Demand": [{"Resource": "FirstResponderEngineer", "Amount": 0.1}],
                                         "PrecedingActivities": []
                                     },
                                     "ContractorMobilization": {
                                         "Duration": {"Lognormal": {"Median": 1, "Dispersion": 0.0}},
                                         "Demand": [{"Resource": "Contractor", "Amount": 1}],
                                         "PrecedingActivities": ["RapidInspection"]
                                     },
                                     "Repair": {
                                         "Duration": {"Lognormal": {"Median": 10, "Dispersion": 0.0}},
                                         "Demand": [{"Resource": "RepairCrew", "Amount": 10}],
                                         "PrecedingActivities": ["RapidInspection", "ContractorMobilization"]
                                     }
                                 },
                                 "DamageFunctionalityRelation": {
                                     "Type": "ReverseLinear"
                                 }
                                 }

RECOVERY_MODEL_PARAMETERS_NO_ACTIVITY = {"Type": "NoRecoveryActivityModel",
                                 "Parameters": {},
                                 "DamageFunctionalityRelation": {
                                     "Type": "Constant"
                                 }
                                 }

RECOVERY_MODEL_PARAMETERS_INFRASTRUCTURE_INTERFACE = {"Type": "InfrastructureInterfaceRecoveryModel",
                                "Parameters": {},
                                "DamageFunctionalityRelation": ""}
    
STEP_DICT = {'StepLimits': [0.0, 0.2, 0.4, 1.0],
            'StepValues': [0.0, 0.1, 0.6, 1.0],
            'RestoredIn': 50}