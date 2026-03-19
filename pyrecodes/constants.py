INCH_TO_MILE = 63360
FEET_TO_MILE = 5280
METER_TO_MILE = 1609.34
SECONDS_IN_TIME_STEP = 3600 
GANTT_BAR_DISTANCE = 10
GANTT_BAR_WIDTH = 5
LOR_ALPHA = 0.2
DAMAGE_LEVEL_TOLERANCE = 1e-5
ALL_RECOVERY_ACTIVITIES_COLORS = {'RapidInspection': 'lightblue',
                                  'DetailedInspection': 'blue',
                                  'SitePreparation': 'lightgreen',
                                    'Financing': 'orange',
                                    'ContractorMobilization': 'springgreen',
                                    'ClaimProcessing': 'purple',
                                    'CleanUp': 'yellow',
                                    'ToxicCleanUp': 'tomato',
                                    'ArchAndEngDesign': 'pink',
                                    'Permitting': 'darkblue',
                                    'Demolition': 'gray',
                                    'Repair': 'red',
                                    'Functional': 'green',
                                    'HouseholdDecisionMaking': 'brown',
                                    'PlanningApproval': 'cyan',
                                    'FinalPlanCheckAndFees': 'magenta',
                                    'EngineeringDesign': 'olive',
                                    'FirstPlanCheck': 'navy',
                                    'EngineeringCorrections': 'teal',
                                    'Waiting': 'lightgray'
                                    }

ALL_RECOVERY_ACTIVITIES_LABELS = {'RapidInspection': 'Rapid Inspection',
                                  'DetailedInspection': 'Detailed Inspection',
                                  'SitePreparation': 'Site Preparation',
                                    'Financing': 'Financing',
                                    'ContractorMobilization': 'Contractor Mobilization',
                                    'ClaimProcessing': 'Claim Processing',
                                    'CleanUp': 'Clean Up',
                                    'ToxicCleanUp': 'Toxic Clean Up',
                                    'ArchAndEngDesign': 'Architectural and Engineering Design',
                                    'Permitting': 'Permitting',
                                    'Demolition': 'Demolition',
                                    'Repair': 'Repair',
                                    'Functional': 'Functional',
                                    'HouseholdDecisionMaking': 'Household Decision Making',
                                    'PlanningApproval': 'Planning Approval',
                                    'FinalPlanCheckAndFees': 'Final Plan Check and Fees',
                                    'EngineeringDesign': 'Engineering Design',
                                    'FirstPlanCheck': 'First Plan Check',
                                    'EngineeringCorrections': 'Engineering Corrections',
                                    'Waiting': 'Waiting'
                                    }

RECOVERY_FINANCING_ACTIVITY_NAME = 'Financing'
MONEY_RESOURCE_NAME = 'Money'

HOUSEHOLD_GANTT_CHART_COLORS = {'Home': 'green',
                                'OutOfTown': 'red',
                                'Friend': 'blue'}

DAMAGE_STATE_COLORS = {
    'None': 'green',
    'Minor': 'yellow',
    'Moderate': 'orange',
    'Severe': 'red',
    'Complete': 'black'
}

DAMAGE_STATE_NUMBER_TO_NAME = {
    0: 'None',
    1: 'Minor',
    2: 'Moderate',
    3: 'Severe',
    4: 'Complete'
}

MET_DEMAND_STATE_COLORS = {
    'Met': 'green',
    'NotMet': 'red'
}

HOUSEHOLD_OCCUPANCY_COLORS = {
    'Occupied': 'green',
    'Vacant': 'red',
    'Unknown': 'gray'
}