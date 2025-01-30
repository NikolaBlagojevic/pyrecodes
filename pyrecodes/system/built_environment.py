from pyrecodes.system.system import System
from pyrecodes.system_creator.system_creator import SystemCreator
from pyrecodes.component.component import Component
from pyrecodes.component.component import SupplyOrDemand
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.utilities import get_class
from pyrecodes.system.distribution_list_creator import DistributionListCreator
from pyrecodes.system.recovery_target_checker import NoDamageRecoveryTargetChecker
import pickle
import json
import math

class BuiltEnvironment(System):
    """
    This class represents a built environment system using the iRe-CoDeS framework as an assembly of components that exchange resources. It inherits from the System abstract class
    and implements the necessary methods to run the resilience assessment for the built environment.

    Attributes:
        | components (list[Component]): List of system components represented as Component objects.
        | resources (dict): Dictionary containing resource parameters.
        | system_creator (SystemCreator): The system creator object responsible for system initialization.
        | FINISH (bool): Flag indicating if the resilience assessment has finished.

    """

    components: list[Component]
    resources: dict
    system_creator: SystemCreator
    FINISH = False

    def __init__(self, system_configuration: dict, component_library: dict, system_creator: SystemCreator):
        """
        Constructor method for the BuiltEnvironmentSystem class. Initializes the system with the given configuration.

        Args:
            | configuration_file (str): The configuration file for the system.
            | component_library (dict): The component library containing system components' configurations.
            | system_creator (SystemCreator): The system creator object responsible for system initialization.
        """
        self.set_configuration_file(system_configuration)
        self.set_component_library(component_library)
        self.set_system_creator(system_creator)

    def __str__(self):
        """
        Returns a string representation of the system state, including the damage level of each component.
        """
        system_state = ''
        for component in self.components:
            system_state += f'{component.__str__()} | Damage Level: {component.get_damage_level()} \n'
        return system_state

    def set_configuration_file(self, system_configuration: dict):
        """
        Sets the configuration file for the system.

        Args:
            system_configuration (dict): Dict with system configuration parameters.
        """
        self.system_configuration = system_configuration

    def set_component_library(self, component_library: dict):
        """
        Sets the component library for the system.

        Args:
            component_library (dict): The component library to set for the system.
        """
        self.component_library = component_library

    def set_system_creator(self, system_creator: SystemCreator):
        """
        This method allows setting the SystemCreator object responsible for system initialization.

        Args:
            system_creator (SystemCreator): The SystemCreator object to set for the system.
        """
        self.system_creator = system_creator

    def create_system(self):
        """
        Creates the system based on the provided SystemCreator object.
        """
        self.system_creator.setup(self.component_library, self.system_configuration)
        self.components = self.system_creator.create_components()
        self.resources = self.system_creator.get_resource_parameters(self.components)
        self.resilience_calculators = self.system_creator.get_resilience_calculators()
        self.START_TIME_STEP = self.system_creator.START_TIME_STEP
        self.MAX_TIME_STEP = self.system_creator.MAX_TIME_STEP
        self.DISASTER_TIME_STEP = self.system_creator.DISASTER_TIME_STEP
        self.recovery_target_checker = NoDamageRecoveryTargetChecker()
        self.set_resource_distribution_dict()
        self.set_damage_input()

    def set_resource_distribution_dict(self):
        """
        Sets the resource distribution list for the system based on components and resource parameters using the DistributionListCreator object.
        """
        distribution_list_creator = DistributionListCreator(self.components, self.resources)
        self.resource_distribution_dict = distribution_list_creator.get_resource_distribution_dict()
    
    def set_damage_input(self):
        """
        Sets the damage input for the system based on the specified damage input type and parameters.
        """
        damage_input_class_filename, damage_input_class_name = self.system_creator.get_damage_input_type()
        target_damage_input_class = get_class(damage_input_class_filename, damage_input_class_name, 'damage_input')
        self.damage_input = target_damage_input_class(self.system_creator.get_damage_input_parameters(), self)        

    def start_resilience_assessment(self):
        """
        Initiates the resilience assessment for the built environment.

        The assessment consists of running a for loop where each pass represents the next time step in the system's recovery. 
        
        At each time step, components' state is update, resources are distributed among components to capture their interaction, and components recover following their recovery model. 
        
        Recovery starts after the disaster has occured.
        """
        for self.time_step in range(self.START_TIME_STEP, self.MAX_TIME_STEP):

            print("Time step: ", self.time_step)

            if self.recovery_target_met():
                self.FINISH = True

            if self.time_step == self.DISASTER_TIME_STEP:
                self.set_initial_damage()

            self.update()

            self.distribute_resources()

            self.update_resilience_calculators()

            if self.time_step > self.DISASTER_TIME_STEP:
                self.recover()

            if self.FINISH:
                print('Resilience assessment finished.')
                break

    def recovery_target_met(self) -> bool:
        """
        Checks whether the recovery target has been met for the built environment system.

        Returns:
            bool: True if the recovery target is met, False otherwise.
        """
        return self.recovery_target_checker.recovery_target_met(self)

    def set_initial_damage(self) -> None: 
        """
        Sets the initial damage for the components based on the damage input.
        """       
        self.damage_input.set_initial_damage()
    
    def get_percent_damaged_buildings(self) -> float:
        """
        Gets the percent of damaged buildings in the system.

        Returns:
            float: The percent of damaged buildings in the system.
        """
        num_damaged_buildings = 0
        for component in self.components:
            if component.get_damage_level() > 0:
                num_damaged_buildings += 1
        return num_damaged_buildings / len(self.components)

    def update(self) -> None:
        """
        Updates the system state during the resilience assessment by updating the state of components.
        """
        for component in self.components:
            component.update(self.time_step)

    def distribute_resources(self) -> None:
        """
        Distributes resources among components following the resource distribution list.
        """
        self.distribute_independent_resources()
        self.distribute_interdependent_resources()  

    def distribute_independent_resources(self) -> None:        
        for resource_name in self.resource_distribution_dict['IndependentResources']:
            self.resources[resource_name]['DistributionModel'].distribute(self.time_step)
    
    def distribute_interdependent_resources(self) -> None:
        system_converged = False
        system_supply = self.get_supply_of_interdependent_resources()
        updated_system_supply = self.get_supply_of_interdependent_resources()
        while not(system_converged):
            for resource_name in self.resource_distribution_dict['InterdependentResources']:
                self.resources[resource_name]['DistributionModel'].distribute(self.time_step)
            updated_system_supply = self.get_supply_of_interdependent_resources()
            system_converged = self.check_system_convergence(system_supply, updated_system_supply)
            system_supply = self.deepcopy(updated_system_supply)
        
    def get_supply_of_interdependent_resources(self) -> dict:
        """
        Gets the supply of interdependent resources in the system.

        Returns:
            dict: A dictionary with the supply of interdependent resources in the system.
        """
        system_supply = {}
        for resource_name in set(self.resource_distribution_dict['InterdependentResources']):            
            system_supply[resource_name] = self.get_system_supply(resource_name)
        return system_supply
    
    def get_system_supply(self, resource_name: str) -> dict:
        """
        Get the system-level supply for a resource resource_name based on current components' state.
        
        This method is already implemented in the ResourceDistributionClass but uses the system matrix. However, using that method requires one to update the system matrix outside of resource distribution which then screws up consumption calculation. This method is a workaround to avoid that.
        """
        system_supply = 0
        for component in self.components:
            if component.has_resource_supply(resource_name):
                system_supply += component.get_current_resource_amount(SupplyOrDemand.SUPPLY.value,
                                                                       StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
                                                                       resource_name)
        return system_supply
        
    def check_system_convergence(self, system_supply: dict, updated_system_supply: dict) -> bool:
        """
        Checks whether the system has converged to a stable state.

        This is checked by comparing the system-level resource supply before and after the resource distribution.

        Returns:
            bool: True if the system has converged, False otherwise.
        """
        system_converged = True
        for resource_name in set(self.resource_distribution_dict['InterdependentResources']):
            if not(math.isclose(system_supply[resource_name], updated_system_supply[resource_name])):
                system_converged = False
                break            
        return system_converged         

    def recover(self) -> None:
        """
        Simulates the recovery process in the system at a single time step.
        """
        for component in self.components:
            component.recover(self.time_step)

    def update_resilience_calculators(self) -> None:
        """
        Updates the resilience calculators with the current resource allocations.
        """
        for resilience_calculator in self.resilience_calculators:
            resilience_calculator.update(self)

    def calculate_resilience(self, print_output=True, return_output=False) -> dict:
        """
        Calculates and returns the resilience metrics for the system.

        Returns:
            list: A list containing resilience metrics specific to each of the resilience calculators.
        """
        resilience_metrics = []
        for resilience_calculator in self.resilience_calculators:
            resilience_metrics.append(resilience_calculator.calculate_resilience())
            if print_output:
                print(resilience_calculator)
        if return_output:
            return resilience_metrics
    
    def deepcopy(self, input):
        """
        Method to deepcopy a dict or a list. Alternative to copy.deepcopy as it is too expensive.
        """
        return json.loads(json.dumps(input))

    def save_as_pickle(self, savename='./system_object.pickle') -> None:
        """
        Saves the system object as a pickle file.

        Args:
            savename (str, optional): The name of the pickle file to save the system object. Defaults to './system_object.pickle'.
        """
        with open(savename, 'wb') as file: 
            pickle.dump(self, file) 
    
    def load_as_pickle(self, loadname='./system_object.pickle') -> None:
        """
        Loads the system object from a pickle file and returns it.

        Args:
            loadname (str, optional): The name of the pickle file to load the system object. Defaults to './system_object.pickle'.

        Returns:
            BuiltEnvironmentSystem: The loaded system object.
        """
        with open(loadname, 'rb') as file:
            system = pickle.load(file) 
        return system 