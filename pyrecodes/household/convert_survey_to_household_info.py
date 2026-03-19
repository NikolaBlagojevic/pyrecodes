import copy
import numpy as np
import pandas as pd

# Mapping defined based on HPS_data.dictionary_Phase 4.1 Cycle 04_CSV

def convert_survey_to_household_info(survey_row, household_info_template):
    household_info = copy.deepcopy(household_info_template)
    household_info['SocioEconomicParameters']['MSA'] = get_msa(survey_row['EST_MSA'])
    household_info['SocioEconomicParameters']['State'] = get_state(survey_row['EST_ST'])
    household_info['SocioEconomicParameters']['Tenure'] = get_tenure_from_survey_code(int(survey_row['TENURE']))
    household_info['SocioEconomicParameters']['Income'] = map_income_code_to_income_level(int(survey_row['INCOME']))
    household_info['SocioEconomicParameters']['Occupants'] = get_number_of_occupants(int(survey_row['THHLD_NUMPER']))
    household_info['SocioEconomicParameters']['Kids5years'] = get_number_of_children(survey_row['KIDS_LT5Y'])
    household_info['SocioEconomicParameters']['Kids5-11years'] = get_number_of_children(survey_row['KIDS_5_11Y'])
    household_info['SocioEconomicParameters']['Kids12-17years'] = get_number_of_children(survey_row['KIDS_12_17Y'])
    household_info['SocioEconomicParameters']['EmploymentStatus'] = map_employed_code_to_num_occupants_employed(int(survey_row['ANYWORK']))
    household_info['BuildingDamage'] = map_damage_code_to_damage_level(int(survey_row['ND_DAMAGE']))
    household_info['DisasterType'] = get_disaster_type(survey_row['ND_TYPE1'], survey_row['ND_TYPE2'], survey_row['ND_TYPE3'], survey_row['ND_TYPE4'], survey_row['ND_TYPE5'])
    household_info['DisplacementDuration'] = get_displacement_duration(int(survey_row['ND_HOWLONG']))
    household_info['WaterAccess'] = map_water_access_code_to_water_demand_fulfillment(int(survey_row['ND_WATER']))
    household_info['PowerAccess'] = map_power_access_code_to_power_demand_fulfillment(int(survey_row['ND_ELCTRC']))
    household_info['FoodAccess'] = map_food_access_code_to_food_demand_fulfillment(int(survey_row['ND_FDSHRTAGE']))
    household_info['UnsanitaryConditions'] = map_unsanitary_conditions_code_to_condition_level(int(survey_row['ND_UNSANITARY']))
    return household_info

def get_msa(msa_code):
    msa_mapping = {
        35620: 'New York-Newark-Jersey City, NY-NJ-PA Metro Area',
        31080: 'Los Angeles-Long Beach-Anaheim, CA Metro Area',
        16980: 'Chicago-Naperville-Elgin, IL-IN-WI Metro Area',
        19100: 'Dallas-Fort Worth-Arlington, TX Metro Area',
        26420: 'Houston-The Woodlands-Sugar Land, TX Metro Area',
        47900: 'Washington-Arlington-Alexandria, DC-VA-MD-WV Metro Area',
        33100: 'Miami-Fort Lauderdale-Pompano Beach, FL Metro Area',
        37980: 'Philadelphia-Camden-Wilmington, PA-NJ-DE-MD Metro Area',
        12060: 'Atlanta-Sandy Springs-Alpharetta, GA Metro Area',
        38060: 'Phoenix-Mesa-Chandler, AZ Metro Area',
        14460: 'Boston-Cambridge-Newton, MA-NH Metro Area',
        41860: 'San Francisco-Oakland-Berkeley, CA Metro Area',
        40140: 'Riverside-San Bernardino-Ontario, CA Metro Area',
        19820: 'Detroit-Warren-Dearborn, MI Metro Area',
        42660: 'Seattle-Tacoma-Bellevue, WA Metro Area'
    }
    return msa_mapping.get(msa_code, '') # too many MSA missing to put a None and skip each household, put an empty string instead

def get_state(state_code):
    state_mapping = {
        1: 'Alabama',
        2: 'Alaska',                
        4: 'Arizona',
        5: 'Arkansas',
        6: 'California',
        8: 'Colorado',
        9: 'Connecticut',
        10: 'Delaware',
        11: 'District of Columbia',
        12: 'Florida',
        13: 'Georgia',
        15: 'Hawaii',
        16: 'Idaho',
        17: 'Illinois',
        18: 'Indiana',
        19: 'Iowa',
        20: 'Kansas',
        21: 'Kentucky',
        22: 'Louisiana',
        23: 'Maine',
        24: 'Maryland',
        25: 'Massachusetts',
        26: 'Michigan',
        27: 'Minnesota',
        28: 'Mississippi',
        29: 'Missouri',
        30: 'Montana',
        31: 'Nebraska',
        32: 'Nevada',
        33: 'New Hampshire',
        34: 'New Jersey',
        35: 'New Mexico',
        36: 'New York',
        37: 'North Carolina',
        38: 'North Dakota',
        39: 'Ohio',
        40: 'Oklahoma',
        41: 'Oregon',
        42: 'Pennsylvania',
        44: 'Rhode Island',
        45: 'South Carolina',
        46: 'South Dakota',
        47: 'Tennessee',
        48: 'Texas',
        49: 'Utah',
        50: 'Vermont',
        51: 'Virginia',
        53: 'Washington',
        54: 'West Virginia',
        55: 'Wisconsin',
        56: 'Wyoming'
    }
    return state_mapping.get(state_code, None) 
   
def get_tenure_from_survey_code(tenure_code):
    # TENURE code in the survey is:
    # 1) Owned by you or someone in this household free and clear?
    # 2) Owned by your or someone in this household with a mortgage or loan (including home equity loans)?
    # 3) Rented?
    # 4) Occupied without payment of rent?
    # -99) Question seen but category not selected
    # -88) Missing / Did not report
    if tenure_code in [1, 2]:
        return 'Owner'
    elif tenure_code == 3:
        return 'Renter'
    elif tenure_code == 4:
        return 'Occupied without payment of rent'
    else:
        return None
        
def map_income_code_to_income_level(income_code):
        # income code in the survey is from 1 to 8 (from less than $25k to more than $200k). 
        if income_code == 1:
            return '<$25,000'
        elif income_code == 2:
            return '$25,000-$34,999'
        elif income_code == 3:
            return '$35,000-$49,999'
        elif income_code == 4:
            return '$50,000-$74,999'
        elif income_code == 5:  
            return '$75,000-$99,999'
        elif income_code == 6:
            return '$100,000-$149,999'
        elif income_code == 7:
            return '$150,000-$199,999'
        elif income_code == 8:
            return '>$200,000'
        else:
            return None

def get_number_of_occupants(num_occupants):
        # number of occupants code in the survey is either a number or a negative number for no answer, missing information
        if num_occupants >= 0:
            return num_occupants
        else:
            return None
        
def get_number_of_children(num_children):
        num_children = float(num_children)
        if not(np.isnan(num_children)) and num_children >= 0:
            return int(num_children)
        else:
            return 0 # return 0 if no answer - too many missing values otherwise
        
def get_disaster_type(type1, type2, type3, type4, type5):
        disaster_types = []
        if int(type1) == 1:
            disaster_types.append('Hurricane')
        if int(type2) == 1:
            disaster_types.append('Flood')
        if int(type3) == 1:
            disaster_types.append('Fire')
        if int(type4) == 1:
            disaster_types.append('Tornado')
        if int(type5) == 1:
            disaster_types.append('Disaster')

        return disaster_types

def get_displacement_duration(displacement_code):
        # ND_HOWLONG code in the survey
        if displacement_code == 1:
            return 'Less than a week'
        elif displacement_code == 2:
            return 'More than a week but less than a month'
        elif displacement_code == 3:
            return 'One to six months'
        elif displacement_code == 4:
            return 'More than six months'
        elif displacement_code == 5:
            return 'Never returned home'
        else:
            return None
        
def map_employed_code_to_num_occupants_employed(employed_code):
        # ANYWORK code in the survey is:
        # 1 - Did any work for pay or profit in the last 7 days
        # 2 - No work for pay or profit in the last 7 days
        # Assume if ANYWORK == 1, all adults are employed
        if employed_code == 1:
            return 'Employed'  # number of employed occupants
        else:
            return 'Not employed'
        
def map_damage_code_to_damage_level(damage_code):
        # ND_DAMAGE code in the survey
        if damage_code == 1:
            return 'No Damage'
        elif damage_code == 2:
            return 'Some Damage'
        elif damage_code == 3:
            return 'Moderate Damage'
        elif damage_code == 4:
            return 'A lot of Damage'
        else:
            return None
        
def map_water_access_code_to_water_demand_fulfillment(water_access_code):
        # ND_WATER code in the survey 
        if water_access_code == 1:
            return "No Shortage of Water"
        elif water_access_code == 2:
            return "A Little Shortage of Water"
        elif water_access_code == 3:
            return "Some Shortage of Water"
        elif water_access_code == 4:
            return "A Lot of Shortage of Water"
        else:
            return None
        
def map_power_access_code_to_power_demand_fulfillment(power_access_code):
            # ND_POWER code in the survey 
        if power_access_code == 1:
            return "No Loss of Electricity"
        elif power_access_code == 2:
            return "A Little Loss of Electricity"
        elif power_access_code == 3:
            return "Some Loss of Electricity"
        elif power_access_code == 4:
            return "A Lot of Loss of Electricity"
        else:
            return None
        
def map_food_access_code_to_food_demand_fulfillment(food_access_code):
        # ND_FDSHRTAGE code in the survey
        if food_access_code == 1:
            return "No Food Shortage"
        elif food_access_code == 2:
            return "A Little Food Shortage"
        elif food_access_code == 3:
            return "Some Food Shortage"
        elif food_access_code == 4:
            return "A Lot of Food Shortage"
        else:
            return None
        
def map_unsanitary_conditions_code_to_condition_level(unsanitary_conditions_code):
        # ND_UNSANITARY code in the survey
        if unsanitary_conditions_code == 1:
            return "No Unsanitary Conditions"
        elif unsanitary_conditions_code == 2:
            return "A Little Unsanitary Conditions"
        elif unsanitary_conditions_code == 3:
            return "Some Unsanitary Conditions"
        elif unsanitary_conditions_code == 4:
            return "A Lot of Unsanitary Conditions"
        else:
            return None