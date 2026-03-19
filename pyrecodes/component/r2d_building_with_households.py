from pyrecodes.component.r2d_component import R2DBuilding
from pyrecodes.utilities import get_class
from pyrecodes.component.component import SupplyOrDemand
import copy

class R2DBuildingWithHouseholds(R2DBuilding):

    def __init__(self) -> None:
        super().__init__()
        self.households = []      
        self.occupied_or_vacant = []

    def construct(self, component_name, component_parameters):
        super().construct(component_name, component_parameters)
        target_household_class = get_class(component_parameters['HouseholdClass']['FileName'], component_parameters['HouseholdClass']['ClassName'], 'household')
        self.household_object = target_household_class()

    def create_households(self, households: list):
        for household_data in households:
            household = copy.deepcopy(self.household_object)
            household.set_parameters(household_data)
            self.households.append(household)

    def set_initial_damage_level(self, damage_level: float) -> None:
        super().set_initial_damage_level(damage_level)
        # If households need to see the building damage level when assigned, they can do it here.
        # No need to do it now.

    def map_buildings_to_households(self, built_environment) -> None:
        """
        Map building components(home, friends, out of town) to households.
        """
        for household in self.households:
            household.map_buildings_to_households(built_environment)

    def update(self, time_step: int, households_in_town: dict) -> None:
        # update households first so they can modify their demand/supply based on where they are
        self.update_households(time_step, households_in_town)
        self.update_occupancy_status()
        super().update(time_step)

    def update_occupancy_status(self):
        """
        If there are households in the building, set the occupancy status to occupied.
        """
        if len(self.households) > 0:
            self.occupied_or_vacant.append('Occupied')
        else:
            self.occupied_or_vacant.append('Vacant')

    def update_operation_demand(self):
        super().update_operation_demand()
        self.update_demand_from_households()

    def update_supply_based_on_component_functionality(self):
        super().update_supply_based_on_component_functionality()
        # TODO: Include how labor supply from households impacts recovery and operations of the city.
        # self.update_supply_from_households()

    def update_supply_based_on_unmet_demand(self, percent_of_met_demand: float, resource_name: str, time_step: int) -> None:
        """
        | Update component's supply based on how much of its operation demand is met.
        | This is how component interdependencies are captured.
        | This method is called during resource distribution.
        """
        super().update_supply_based_on_unmet_demand(percent_of_met_demand, resource_name, time_step)
        self.update_households_based_on_unmet_demand(percent_of_met_demand, resource_name)

    def update_households_based_on_unmet_demand(self, percent_of_met_demand: float, resource_name: str) -> None:
        """
        Update component's households based on how much of their operation demand is met.
        """
        for household in self.households:
            household.update_based_on_unmet_demand(percent_of_met_demand, resource_name)

    def update_demand_from_households(self):
        # TODO: update_demand_from_households and update_supply_from_households can be merged into a single method.
        for household in self.households:
            household_demand = household.get_demand()
            for resource_name, value in household_demand.items():
                if resource_name in self.demand['OperationDemand']:
                    self.demand['OperationDemand'][resource_name].current_amount += value
                else:
                    self.demand['OperationDemand'][resource_name].current_amount = value

    def update_supply_from_households(self):
        for household in self.households:
            household_supply = household.get_supply()
            for resource_name, value in household_supply.items():
                if resource_name in self.supply['Supply']:
                    self.supply['Supply'][resource_name].current_amount += value
                else:
                    raise ValueError(f"{resource_name} is not initialized in {self.name}. Please initialize the resource in component's template in component library.")

    def component_represents_out_of_town(self) -> bool:
        return self.general_information['OccupancyClass'] == 'OutOfTown'
    
    def component_represents_friends_house(self, household) -> bool:
        return int(self.general_information['AIM_id']) in household.friends

    def component_represents_home(self, household) -> bool:
        return int(self.general_information['AIM_id']) == int(household.home_id)
          
    def update_households(self, time_step: int, households_in_town: list) -> None:
        for household in self.households:
            household.update(time_step, self, households_in_town)
          
    def recover(self, time_step):
        super().recover(time_step)
            
    def households_decide(self) -> None:    
        for household in self.households:
            household.decide(self)

    def households_move(self) -> None:
        """
        Move households to the component that they decided to move to.
        Make a copy of the households list to avoid modifying the original list while iterating over it. If a household moves, it is removed from the original list and then the loop will skip the next household.
        """
        component_households = self.households[:]
        for household in component_households:
            household.move(self)

    def print_household_ids(self):
        print(f"\n Building ID: {self.general_information['AIM_id']}. Locality: {self.locality}. Households: ")
        for household in self.households:
            print(household.id)

class R2DTown(R2DBuildingWithHouseholds):
    """
    Component representing a town where households can move to if they decide to leave their home.

    Assume all resources are available in the town.
    """

    def update_supply_based_on_unmet_demand(self, percent_of_met_demand: float, resource_name: str, time_step: int) -> None:
        """
        | Assume all demand is met in the town.
        """
        percent_of_met_demand = 1.0
        super().update_supply_based_on_unmet_demand(percent_of_met_demand, resource_name, time_step)          
    

    