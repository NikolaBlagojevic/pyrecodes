from copyreg import pickle
from pyrecodes.component.r2d_component import R2DBuilding
from pyrecodes.household.household_gpt import HouseholdGPT
from pyrecodes.system.built_environment import BuiltEnvironment
from pyrecodes.utilities import unpack_time_stepping_rules
from pyrecodes.component.r2d_building_with_households import R2DBuildingWithHouseholds
from pyrecodes.system.recovery_target_checker import NoDamageRecoveryTargetWithExtraTimeChecker

class BuiltEnvironmentWithHouseholds(BuiltEnvironment):

    def __init__(self, system_configuration: dict, component_library: dict, system_creator):
        super().__init__(system_configuration, component_library, system_creator)
        self.households_to_move = {}
        self.households_in_town = []

    def create_system(self):
        super().create_system()
        self.recovery_target_checker = NoDamageRecoveryTargetWithExtraTimeChecker()
        self.set_household_decision_making_time_steps()
        # has to be called after the system is created so all components are created
        self.map_buildings_to_households()
        self.register_hook('post_time_step', self._household_step)

    def set_household_decision_making_time_steps(self) -> None:
        """
        Set the time steps at which household make decisions.
        """
        household_decision_making_time_stepping_rules = self.system_configuration['Constants'].get('HOUSEHOLD_DECISION_MAKING_TIME_STEPS', None)
        if household_decision_making_time_stepping_rules is not None:
            self.household_decision_making_time_steps = unpack_time_stepping_rules(household_decision_making_time_stepping_rules)
        else:
            self.household_decision_making_time_steps = list(range(self.START_TIME_STEP, self.MAX_TIME_STEP))
    
    def map_buildings_to_households(self) -> None:
        """
        Map building components(home, friends, out of town) to households.
        """
        for component in self.components:
            if isinstance(component, R2DBuildingWithHouseholds):
                component.map_buildings_to_households(self)

    def _household_step(self, time_step: int) -> None:
        """Hook callback: run household decisions and moves at eligible time steps."""
        if time_step in self.household_decision_making_time_steps:
            self.households_decide()
            self.households_move()

    def update(self):
        self.update_the_number_of_households_in_town()  
        for component in self.components:                      
            component.update(self.time_step, self.households_in_town)

    def households_move(self):
        for component in self.components:
            if hasattr(component, 'households'):
                component.households_move()
        
    def households_decide(self) -> dict:
        """
        Households decide what to do based on the current situation.
        """
        for component in self.components:
            if hasattr(component, 'households'):
                component.households_decide()

    def update_households_to_move(self, households_to_move: dict):
        for key, value in households_to_move.items():
            if key in self.households_to_move:
                self.households_to_move[key] += value
            else:
                self.households_to_move[key] = value

    def update_the_number_of_households_in_town(self):
        """
        Updates the system property indicating the number of households in that are in a neighborhood.
        """
        self.households_in_town.append(0)
        for component in self.components:
            if hasattr(component, 'households') and self.component_in_town(component):
                number_of_households = 0
                for household in component.households:
                    if len(household.staying_at) == 0 or household.staying_at[-1] != 'OutOfTown': # in the first time step the list is empty and all households are in town, hence the first condition
                        number_of_households += 1
                self.households_in_town[self.time_step] += number_of_households
    
    def component_in_town(self, component):
        """
        Returns True if the component is in town.
        """
        return component.general_information['OccupancyClass'] != 'OutOfTown'

    def save_as_pickle(self, savename='./system_object.pickle'):
        save_dicts = {}
        for save_object, object_name in zip([self.components, self.resilience_calculators], ['components', 'resilience_calculators']):            
            save_dicts[object_name] = []
            for element in save_object:
                filtered_dict = {}
                for key, value in getattr(element, '__dict__', {}).items():
                    if key == 'households':
                        filtered_dict[key] = []
                        for household in value:
                            filtered_dict[key].append({'ID': household.id, 'Decisions': household.decisions, 'StayingAt': household.staying_at})
                    try:
                        pickle.dumps(value)
                        filtered_dict[key] = value
                    except Exception:
                        print(f"Skipping non-pickleable attribute: {key}")
                save_dicts[object_name].append(filtered_dict)

        with open(savename, 'wb') as file:
            pickle.dump(save_dicts, file)

    def load_as_pickle(self, loadname='./system_object.pickle'):
        with open(loadname, 'rb') as file:
            loaded_dicts = pickle.load(file)
        
        formed_components = self.load_components(loaded_dicts['components'])
        self.components = formed_components
        self.resilience_calculators = loaded_dicts['resilience_calculators']
        return self

    def load_components(self, component_dicts: list):
        real_components = []
        for component_dict in component_dicts:
            if 'Building' in component_dict['name'] or 'Town' in component_dict['name']:
                # see what is needed to initialize R2DBuilding and add important fields from dict to plot results
                component = R2DBuilding()
                for key, value in component_dict.items():
                    if key == 'households':
                        component.households = []
                        for household in value:
                            household_object = HouseholdGPT()
                            setattr(household_object, 'id', household['ID'])
                            setattr(household_object, 'decisions', household['Decisions'])
                            setattr(household_object, 'staying_at', household['StayingAt'])
                            component.households.append(household_object)
                    else:
                        setattr(component, key, value)        
                real_components.append(component)
        return real_components
        