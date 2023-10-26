"""
Module that defines the **pyrecodes** System class and its two helper classes: DistributionListCreator and RecoveryTargetChecker.
"""

from abc import ABC, abstractmethod
import math
from pyrecodes import SystemCreator
from pyrecodes import DamageInput
from pyrecodes import Component
import pickle
import copy

class System(ABC):
    """
    Abstract base class representing a generic system for resilience assessment.

    Attributes:
        | components (list[Component.Component]): List of system components represented as Component objects.
        | resources (dict): Dictionary containing resource parameters.
        | system_creator (SystemCreator.SystemCreator): The system creator object responsible for system initialization.

    """
    components: list([Component.Component])
    resources: dict
    system_creator: SystemCreator.SystemCreator

    @abstractmethod
    def __init__(self, system_configuration_file: dict, component_library: dict, system_creator: SystemCreator.SystemCreator):
        """
        Constructor method for the System class. Initializes the system with the given configuration.

        Args:
            | configuration_file (dict): The configuration file for the system.
            | component_library (dict): The component library containing system components' configurations.
            | system_creator (SystemCreator.SystemCreator): The system creator object responsible for system initialization.
        """
        pass

    @abstractmethod
    def set_configuration_file(self, system_configuration: dict):
        """
        Sets the configuration file for the system.

        Args:
            system_configuration (dict): System configuration dictionary.
        """
        pass

    @abstractmethod
    def set_component_library(self, component_library: dict):
        """
        Sets the component library for the system.

        Args:
            component_library (dict): The component library to set for the system.
        """
        pass

    @abstractmethod
    def create_system(self, system_creator: SystemCreator.SystemCreator):
        """
        Creates the system based on the provided SystemCreator object.

        Args:
            system_creator (SystemCreator.SystemCreator): The system creator object responsible for system initialization.
        """
        pass

    @abstractmethod
    def set_initial_damage(self):
        """
        Sets the initial damage state of the system components.
        """
        pass

    @abstractmethod
    def start_resilience_assessment(self):
        """
        Initiates the resilience assessment for the system. This is the entry point for running the assessment.
        """
        pass

    @abstractmethod
    def distribute_resources(self):
        """
        Distributes resources among the system component's.
        """
        pass

    @abstractmethod
    def update(self):
        """
        Updates the system state at a time step of the resilience assessment.
        """
        pass

    @abstractmethod
    def recover(self):
        """
        Simulates the recovery process in the system.
        """
        pass

    @abstractmethod
    def calculate_resilience(self):
        """
        Calculates and returns the resilience metric for the system.
        """
        pass

class DistributionListCreator:
    """
    Creates a list specifying the order of resource distribution in the system.

    This class determines the order in which resources should be distributed to capture components' interdependencies and calculate consumption.
    The resource order is fixed: Bridge Services, Transfer Services, Independent Resources, Interdependent Resources.

    Attributes:
        | components (list[Component.Component]): A list of components in the system.
        | resources (dict): A dictionary containing resource parameters for the system.

    """

    def __init__(self, components: list[Component.Component], resources: dict):
        """
        Initialize the DistributionListCreator with components and resources.

        Args:
            | components (list[Component.Component]): A list of components in the system.
            | resources (dict): A dictionary containing resource parameters for the system.

        """
        self.components = components
        self.resources = resources

    def get_resource_distribution_dict(self):
        """
        Generate the resource distribution dict based on the specified order.

        The resource distribution dict is formed by grouping resources into four categories:
        1. Bridge Services
        2. Transfer Services
        3. Other Independent Resources
        4. Interdependent Resources

        The reason is that Bridge Services are here assumed always to be independent resources that only affect Transfer Services.
        Transfer Services are assumed to only be affected by Bridge Services and to affect other resources, 
        both the distribution of Independent and Interdependent Resources.
        Remaining Independent Resources can only be distriuted once per time step, as their supply won't be affected by unmet demand for other resources.
        The supply of Interdependent Resources can be affected by unmet demand and to capture potential cascading effects,
        their distribution is last and in an iterative manner.

        TODO: this method can be improved by making it more generic and flexible. Future work.

        Returns:
            dict: A dict separating independent and interdependent resources and specifying the order of resource distribution.

        
        """
        resource_distribution_dict = {'IndependentResources': [],
                                      'InterdependentResources': []}

        # Group resources that belong to the Bridge Services group
        resource_distribution_dict['IndependentResources'] += self.get_resource_group('BridgeService')

        # Group resources that belong to the Transfer Services group
        resource_distribution_dict['IndependentResources'] += self.get_resource_group('TransferService')

        # Separate Independent and Interdependent Resources excluding Bridge and Transfer Services
        resource_distribution_dict = self.get_independent_interdependent_resources(
            resource_distribution_dict)

        # Form the resource distribution vector using Interdependent Resources
        resource_distribution_dict['InterdependentResources'] = self.form_resource_distribution_vector(resource_distribution_dict['InterdependentResources'])

        return resource_distribution_dict

    def get_resource_group(self, group_name: str):
        """
        Get a list of resource names belonging to the specified group.

        Args:
            group_name (str): The name of the resource group.

        Returns:
            list[str]: A list of resource names in the specified group.

        """
        resource_group = []
        for resource_name, resource_parameters in self.resources.items():
            if resource_parameters['Group'] == group_name:
                resource_group.append(resource_name)
        return resource_group

    def get_independent_interdependent_resources(self, resource_distribution_dict: dict):
        """
        Separate resources that are not Bridge or Transfer services into Independent and Interdependent Resources.

        Args:
            resource_distribution_list (list[str]): The list specifying the order of resource distribution.

        Returns:
            tuple[list[str], list[str]]: Two lists containing Independent and Interdependent Resources, respectively.

        """        
        for resource_name in self.resources.keys():
            if resource_name not in resource_distribution_dict['IndependentResources']:
                for component in self.components:
                    if self.resource_is_interdependent(resource_name, component):
                        resource_distribution_dict['InterdependentResources'].append(resource_name)
                        break
                else:
                    resource_distribution_dict['IndependentResources'].append(resource_name)

        return resource_distribution_dict
    
    def resource_is_interdependent(self, resource_name: str, component: Component.Component) -> bool:
        """
        Check whether the specified resource is interdependent.

        A resource is assumed interdependent if there is a single component that:
        1. Has a supply of the resource
        2. Has an operation demand
        3. Component's supply can be affected by unmet demand of the resource (i.e., the relation is not Constant)

        Args:
            resource_name (str): The name of the resource.
            component (Component.Component): The component to check.

        Returns:
            bool: True if the resource is interdependent, False otherwise.

        """
        return component.has_resource_supply(resource_name) and \
               component.has_operation_demand() and \
               component.unmet_demand_can_affect_resource_supply(resource_name)                 

    def form_resource_distribution_vector(self, interdependent_resources):
        """
        Form the resource distribution vector by repeating Interdependent Resources.

        The number of repetitions is equal to the number of Interdependent Resources.

        Reasoning behind this is provided in:
         Blagojevic et al. (2022) Quantifying disaster resilience of a community with
         interdependent civil infrastructure systems

        Args:
            interdependent_resources (list[str]): List of Interdependent Resources.

        Returns:
            list[str]: The resource distribution vector.

        """
        num_resources = len(interdependent_resources)
        return interdependent_resources * num_resources
    
class RecoveryTargetChecker(ABC):
    """
    Abstract base class for a recovery target checker.

    This class defines the interface for checking whether the system has recovered and the resilience assessment interval
    is finished.
    """

    @abstractmethod
    def recovery_target_met(self, system: System) -> bool:
        """
        Check whether the recovery target has been met for the given system.

        Args:
            system (System): The system object to check for recovery.

        Returns:
            bool: True if the recovery target is met, False otherwise.
        """
        pass


class CompleteDamageRecoveryTargetChecker(RecoveryTargetChecker):
    """
    Concrete subclass of RecoveryTargetChecker.

    This class implements the recovery target checker where the system has recovered once all components are damage-free.

    """

    def recovery_target_met(self, system: System) -> bool:
        """
        Check whether the recovery target has been met for the given system.

        The system is considered to have recovered once all components are damage-free (damage level close to 0).

        Args:
            system (System): The system object to check for recovery.

        Returns:
            bool: True if the recovery target is met, False otherwise.
        """
        if system.time_step <= system.DISASTER_TIME_STEP:
            return False
        else:
            for component in system.components:
                if not (math.isclose(component.get_damage_level(), 0, abs_tol=1e-10)):
                    return False
        return True


class BuiltEnvironmentSystem(System):
    """
    This class represents a built environment system using the iRe-CoDeS framework as an assembly of components that exchange resources. It inherits from the System abstract class
    and implements the necessary methods to run the resilience assessment for the built environment.

    Attributes:
        | components (list[Component.Component]): List of system components represented as Component objects.
        | resources (dict): Dictionary containing resource parameters.
        | system_creator (SystemCreator.SystemCreator): The system creator object responsible for system initialization.
        | FINISH (bool): Flag indicating if the resilience assessment has finished.

    """

    components: list([Component.Component])
    resources: dict
    system_creator: SystemCreator.SystemCreator
    FINISH = False

    def __init__(self, system_configuration: dict, component_library: dict, system_creator: SystemCreator.SystemCreator):
        """
        Constructor method for the BuiltEnvironmentSystem class. Initializes the system with the given configuration.

        Args:
            | configuration_file (str): The configuration file for the system.
            | component_library (dict): The component library containing system components' configurations.
            | system_creator (SystemCreator.SystemCreator): The system creator object responsible for system initialization.
        """
        self.set_configuration_file(system_configuration)
        self.set_component_library(component_library)
        self.set_system_creator(system_creator)
        # self.create_system()

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

    def set_system_creator(self, system_creator: SystemCreator.SystemCreator):
        """
        This method allows setting the SystemCreator object responsible for system initialization.

        Args:
            system_creator (SystemCreator.SystemCreator): The SystemCreator object to set for the system.
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
        self.recovery_target_checker = CompleteDamageRecoveryTargetChecker()
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
        target_damage_input_class = getattr(DamageInput, self.system_creator.get_damage_input_type())
        self.damage_input = target_damage_input_class(self.system_creator.get_damage_input_parameters())        

    def start_resilience_assessment(self):
        """
        Initiates the resilience assessment for the built environment.

        The assessment consits of running a for loop where each pass represents the next time step in the system's recovery. 
        
        At each time step, components' state is update, resources are distributed among components to capture their interaction, and components recover following their recovery model. 
        
        Recovery starts after the disaster has occured.
        """
        for self.time_step in range(self.START_TIME_STEP, self.MAX_TIME_STEP):

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
        self.damage_input.set_initial_damage(self.components)

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
        self.distribute_indepedent_resources()
        self.distribute_interdependent_resources()
    
    def distribute_indepedent_resources(self) -> None:        
        for resource_name in self.resource_distribution_dict['IndependentResources']:
            self.resources[resource_name]['DistributionModel'].distribute()
    
    def distribute_interdependent_resources(self) -> None:
        system_converged = False
        system_supply = self.get_supply_of_interdependent_resources()
        updated_system_supply = self.get_supply_of_interdependent_resources()
        while not(system_converged):
            for resource_name in self.resource_distribution_dict['InterdependentResources']:
                self.resources[resource_name]['DistributionModel'].distribute()
            updated_system_supply = self.get_supply_of_interdependent_resources()
            system_converged = self.check_system_convergence(system_supply, updated_system_supply)
            system_supply = copy.deepcopy(updated_system_supply)
        
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
                system_supply += component.get_current_resource_amount(Component.SupplyOrDemand.SUPPLY.value,
                                                                       Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value,
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
            resilience_calculator.update(self.resources)

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

