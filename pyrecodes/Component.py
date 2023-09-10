import math
from abc import ABC, abstractmethod
from enum import Enum
from pyrecodes import ComponentRecoveryModel
from pyrecodes import Resource
from pyrecodes import Relation
from pyrecodes import ProbabilityDistribution
import numpy as np

"""
Module used to define the Component class and its subclasses.
"""

class SupplyOrDemand(Enum):
    """
    Enum Class to specify the strings used for component's supply and demand parameters.
    """
    SUPPLY = 'supply'
    DEMAND = 'demand'

class Component(ABC):
    """
    Abstract Class to define the required methods and properties of a component.
    """
    name: str
    functionality_level: float 
    functional: list[int]
    locality: list
    supply: dict
    demand: dict

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def construct(self, component_name: str, component_parameters: dict) -> None:
        pass

    @abstractmethod
    def set_initial_damage_level(self, damage_level: float) -> None:
        pass

    @abstractmethod
    def get_damage_level(self) -> float:
        pass

    @abstractmethod
    def update(self, time_step: int) -> None:
        pass

    @abstractmethod
    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        pass

    @abstractmethod
    def recover(self) -> None:
        pass

    @abstractmethod
    def update_supply_based_on_unmet_demand(self, percent_of_met_demand: float) -> None:
        pass

    @abstractmethod
    def set_locality(self, locality_id: list) -> None:
        pass

    @abstractmethod
    def get_locality(self) -> int:
        pass

    @abstractmethod
    def has_operation_demand(self) -> bool:
        pass

    @abstractmethod
    def has_resource_supply(self, resource_name: str) -> bool:
        pass
    
class StandardiReCoDeSComponent(Component):
    """
    Implementation of the Component abstract class to define standard functionality of a component in iRe-CoDeS. 
    """
    class SupplyTypes(Enum):
        """
        | Enum Class to specify the strings used for component's supply types.
        | Only one supply type is currently considered in pyrecodes.
        """
        SUPPLY = 'Supply'

    class DemandTypes(Enum):
        """
        | Enum Class to specify the strings used for component's demand types.
        | Two demand types are currently considered in pyrecodes: operation and recovery demand.
        """
        OPERATION_DEMAND = 'OperationDemand'
        RECOVERY_DEMAND = 'RecoveryDemand'

    def __init__(self) -> None:
        """
        | Initialiaze the StandardiReCoDeSComponent. Set functionality level of a component to 1.
        | Initialize the "functional" time step list and supply and demand of a component as empty dicts.
        """
        self.functionality_level = 1.0
        self.functional = []
        self.recovery_model = None
        self.locality = None
        self.supply = {supply_type.value: dict() for supply_type in self.SupplyTypes}
        self.demand = {demand_type.value: dict() for demand_type in self.DemandTypes}

    def __str__(self) -> str:
        """
        Define a string to describe a component in the print statement.
        """
        return f'{self.name} | Locality: {self.locality}'
    
    def construct(self, component_name: str, component_parameters: dict) -> None:
        self.set_recovery_model(component_parameters['RecoveryModel'])
        self.set_supply(component_parameters.get('Supply', {}))
        self.set_operation_demand(component_parameters.get('OperationDemand', {}))
        self.set_name(component_name)
    
    def set_recovery_model(self, recovery_model_parameters: dict) -> None:
        """
        | Set component recovery model as defined in recovery_model_parameters dict.
        | The data provided in the recovery_model_parameters depends on the recovery model type.
        """
        target_recovery_model = getattr(ComponentRecoveryModel, recovery_model_parameters['Type'])
        self.recovery_model = target_recovery_model(recovery_model_parameters)
    
    def set_supply(self, supply_parameters: dict) -> None:
        """
        | Set component's supply as defined in supply_parameters.
        | Check out the supply_parameters in the examples to get the dict structure.
        | **TODO**: Add the dict structure here. Future work.
        """
        self.add_resources(SupplyOrDemand.SUPPLY.value,
                                self.SupplyTypes.SUPPLY.value,
                                supply_parameters)
    
    def set_operation_demand(self, operation_demand_parameters: dict) -> None:
        """
        | Set component's operation demand as defined in operation_demand_parameters.
        | Check out the operation_demand in the component library files in the examples to get the dict structure.
        | **TODO**: Add the dict structure here. Future work.
        """
        self.add_resources(SupplyOrDemand.DEMAND.value,
                                self.DemandTypes.OPERATION_DEMAND.value,
                                operation_demand_parameters)

    def set_initial_damage_level(self, damage_level: float) -> None:
        """
        Set the initial damage level of the component. Damage level must be between 0 and 1.
        """
        self.recovery_model.set_initial_damage_level(damage_level)

    def get_damage_level(self) -> float:
        """
        Get the current damage level of the component.
        """
        return self.recovery_model.get_damage_level()

    def set_name(self, name: str) -> None:
        """
        Set component name.
        """
        self.name = name

    def set_locality(self, locality_id: list([int])) -> None:
        """
        Set component locality ids. Locality id is a list of integers.
        """
        self.locality = locality_id

    def get_locality(self) -> list:
        """
        Get component locality ids.
        """
        return self.locality

    def has_operation_demand(self) -> bool:
        """
        Check whether the component has any operation demand - if it needs any resource to operate.
        """
        return len(self.demand[self.DemandTypes.OPERATION_DEMAND.value]) > 0

    def has_resource_supply(self, resource_name: str) -> bool:
        """
        Check whether the component has a supply of the resource resource_name.
        """
        return resource_name in list(self.supply[self.SupplyTypes.SUPPLY.value].keys())
    
    def unmet_demand_can_affect_resource_supply(self, resource_name: str) -> bool:
        """
        Check if the component has a supply of the resource resource_name and if the supply can be affected by unmet demand - i.e., if the UnmetDemandToAmountRelation is not constant.
        """
        if resource_name in list(self.supply[self.SupplyTypes.SUPPLY.value].keys()):
            return not(isinstance(self.supply[self.SupplyTypes.SUPPLY.value][resource_name].unmet_demand_to_amount, Relation.Constant))
        else:
            return False

    def add_resources(self, supply_or_demand: str, type: str, resource_dict: dict) -> None:
        """
        | Add resources to the component's supply or demand, depending on the supply_or_demand parameter.
        | The type parameter specifies the type of the supply or demand.
        | The resource_dict parameter is a dict with resource names as keys and resource parameters as values.
        """
        place_to_add = getattr(self, supply_or_demand)[type]
        for resource_name, resource_parameters in resource_dict.items():            
            place_to_add[resource_name] = self.form_resource(resource_name, resource_parameters)
    
    def form_resource(self, resource_name: str, resource_parameters: dict, default_resource_class = 'NonConsumableResource') -> None:
        """
        | Form a resource object based on the resource_name and resource_parameters.
        | Default resource class is NonConsumableResource. Specify a different default resource class if needed.
        | Check out the resource parameters dict in the component library files in the examples to get the dict structure.
        | **TODO**: Add the dict structure here. Future work.
        """
        target_resource_object = getattr(Resource, resource_parameters.get('ResourceClass', default_resource_class))
        return target_resource_object(resource_name, resource_parameters)
    
    def get_current_resource_amount(self, supply_or_demand: str, type: str, resource_name: str) -> float:
        """
        | Get the current amount of a resource resource_name in component's supply or demand and the type of the supply or demand.
        | In case resource is not in component's supply or demand, returns 0.
        """
        resource = getattr(self, supply_or_demand)[type].get(resource_name, None)
        if not (resource is None):
            return resource.current_amount
        else:
            return 0.0

    def update(self, time_step: int) -> None:
        """
        | Update component's state based on its current damage level and damage-to-functionality relation.
        | This includes updating component's functionality_level, checking if the component is functional at time_step and updating its supply, operation and recovery demand.
        """
        self.update_functionality()
        self.check_if_functional(time_step)
        self.update_supply_based_on_component_functionality()
        self.update_operation_demand()
        self.update_recovery_demand()

    def update_functionality(self) -> None:
        """
        Update component's functionality level by calling the recovery model's get_functionality_level method.
        """
        self.functionality_level = self.recovery_model.get_functionality_level()
        
    def check_if_functional(self, time_step: int) -> None:
        """
        | Check if the component is functional at time_step. Component is considered functional if its functionality level is higher than 0.
        | If the component is functional at time_step, add time_step to the component's "functional" list.
        """
        if self.functionality_level > 0:
            self.functional.append(time_step)

    def update_resources_based_on_component_functionality(self, supply_or_demand: str, type: str) -> None:
        """
        Update component's supply or demand based on its current functionality level.
        """
        resources_to_update = getattr(self, supply_or_demand)[type]
        for resource_object in resources_to_update.values():
            resource_object.update_based_on_component_functionality(self.functionality_level)

    def update_supply_based_on_component_functionality(self) -> None:
        """
        Update component's supply based on its current functionality level.
        """
        self.update_resources_based_on_component_functionality(SupplyOrDemand.SUPPLY.value,
                                                               self.SupplyTypes.SUPPLY.value)

    def update_operation_demand(self) -> None:
        """
        Update component's operation demand based on its current functionality level.
        """
        self.update_resources_based_on_component_functionality(SupplyOrDemand.DEMAND.value,
                                                               self.DemandTypes.OPERATION_DEMAND.value)

    def update_recovery_demand(self):
        """
        | Update component's recovery demand based on its currently active recovery activities.
        | Before resources are distributed, it is assumed that all recovery demand is met. 
        | It is important that this method is called before the resource distribution in a time step of the resilience assessment.
        """
        self.set_recovery_model_activities_demand_to_met()
        self.demand[self.DemandTypes.RECOVERY_DEMAND.value] = self.recovery_model.get_demand()

    def set_recovery_model_activities_demand_to_met(self):
        """
        Set the demand of all component's recovery activities as met.
        """
        self.recovery_model.set_activities_demand_to_met()

    def update_supply_based_on_unmet_demand(self, percent_of_met_demand: float) -> None:
        """
        | Update component's supply based on how much of its operation demand is met.
        | This is how component interdependencies are captured.
        | This method is called during resource distribution.
        """
        resources_to_update = getattr(self, SupplyOrDemand.SUPPLY.value)[self.SupplyTypes.SUPPLY.value] 
        for resource_object in resources_to_update.values():
            resource_object.update_based_on_unmet_demand(percent_of_met_demand)   
    
    def update_supply_based_on_consumption(self, resource_name: str, consumed_amount: float) -> None:
        """
        | Update component's supply based on how much of its consumable resource is consumed.
        | If resource is non-consumable, this method does nothing.
        | This method is called during resource distribution.
        """
        resources_to_update = getattr(self, SupplyOrDemand.SUPPLY.value)[self.SupplyTypes.SUPPLY.value] 
        resources_to_update[resource_name].update_based_on_consumption(consumed_amount)
    
    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        """
        | Set the demand_met for the component's recovery activity that require the resource resource_name.
        | This is how recovery resource constraints are captured.
        | This method is called once the resource distribution is performed at a time step.
        | **Note**: At this point, two recovery activities CANNOT ask for the same resource! 
        | **TODO**: Add recovery_activity as input, then it would be possible. Future work. 
        """
        self.recovery_model.set_met_demand_for_recovery_activities(resource_name,
                                                                     percent_of_met_demand)  

    def recover(self, time_step: int):
        """
        Recover the component as defined in its recovery model.
        """
        self.recovery_model.recover(time_step)


class BuildingStockUnitWithEmergencyCalls(StandardiReCoDeSComponent):
    """
    Subclass of the StandardiReCoDeSComponent class that simulates the performance of building stock units 
    with increased post-disaster demand for communication services due to emergency calls.

    Attributes
    ----------
    (only subclass specific)

    COMMUNICATION_RESOURCE_NAME : str
        | The demand for this resource will increase after a disaster.
        | This name should be defined in the component library file by adding the 'PostDisasterIncreaseDueToEmergencyCalls' key with a 'True' value.
    COMMUNICATION_DEMAND_MULTIPLIER : float
        Defines by how much the pre-disaster demand for the communication resource 
        is increased after a disaster.
    COMMUNICATION_DEMAND_INCREASE_TIME_STEP : int
        | Define at which time step of the recovery simulation will the demand for communication resource increase.
        | **Note**: this time step should be after the DISASTER_TIME_STEP defined in the system configuration file.
    COMMUNICATION_DEMAND_EXP_DECREASE_COEFF : float
        Define the parameter of the exponential function that simulates the post-disaster decrease of the
        demand for communication resource following the initial demand surge.   
    """

    COMMUNICATION_RESOURCE_NAME = ''
    COMMUNICATION_DEMAND_MULTIPLIER = 10.0
    COMMUNICATION_DEMAND_INCREASE_TIME_STEP = 1
    COMMUNICATION_DEMAND_EXP_DECREASE_COEFF = -0.3

    def update(self, time_step: int) -> None:
        """
        | *extend parent method*
        | Update the demand for communication services conditioned on the current time step.
        """
        super().update(time_step)
        self.update_communication_demand(time_step)

    def update_communication_demand(self, time_step: int) -> None:
        """
        | Calculate the communication resource demand at the current time step
        | and update in component's operation demand.
        """
        communication_resource_object = \
            getattr(self, SupplyOrDemand.DEMAND.value)[self.DemandTypes.OPERATION_DEMAND.value][
                self.COMMUNICATION_RESOURCE_NAME]
        current_communication_demand = communication_resource_object.current_amount
        initial_communication_demand = communication_resource_object.initial_amount
        if time_step >= self.COMMUNICATION_DEMAND_INCREASE_TIME_STEP:
            current_communication_demand = self.modify_emergency_calls_demand(initial_communication_demand, time_step)
        communication_resource_object.set_current_amount(current_communication_demand)

    def modify_emergency_calls_demand(self, initial_communication_demand: float, time_step: int) -> float:
        """
        | Modify communication demand based on the current time step, the exponential function parameters and initial communication demand.
        | The modified communication demand cannot be smaller than the initial, pre-disaster, demand.
        """
        modified_communication_demand = (initial_communication_demand * self.COMMUNICATION_DEMAND_MULTIPLIER) * math.exp(
            self.COMMUNICATION_DEMAND_EXP_DECREASE_COEFF) ** (time_step - self.COMMUNICATION_DEMAND_INCREASE_TIME_STEP)
        if modified_communication_demand < initial_communication_demand:
            return initial_communication_demand
        else:
            return modified_communication_demand
    
    def add_resources(self, supply_or_demand: str, type: str, resource_dict: dict) -> None:
        """
        | *override parent method*
        | While adding resources check if a resource is a communication resource.
        | If yes, set the COMMUNICATION_RESOURCE_NAME attribute.
        | **Note**: only one resource can be a communication resource that has increased demand following a disaster.
        | **TODO**: Implement a check for multiple communication resources. Future work.
        """
        place_to_add = getattr(self, supply_or_demand)[type]
        for resource_name, resource_parameters in resource_dict.items():
            self.check_if_demand_increase_considered(resource_name, resource_parameters)
            place_to_add[resource_name] = self.form_resource(resource_name, resource_parameters)
    
    def check_if_demand_increase_considered(self, resource_name: str, resource_parameters: dict) -> None:
        """
        | Check if the resource demand should be increased following the disaster for the resource resource_name.
        | Communication resource parameters dict in ComponentLibrary should have the 'PostDisasterIncreaseDueToEmergencyCalls' key with a 'True' value.
        """
        if resource_parameters.get('PostDisasterIncreaseDueToEmergencyCalls', None) == "True":
            self.COMMUNICATION_RESOURCE_NAME = resource_name


class InfrastructureInterface(StandardiReCoDeSComponent):
    """
    | Subclass of the StandardiReCoDeSComponent class used to interface third-party infrastructure simulators into an iRe-CoDeS system-of-systems model.
    | Infrastructure simulator performance is defined in the system configuration file.    
    """   
    def set_supply_dynamics(self, supply_dynamics: dict) -> None:   
        """
        | Set the predefined supply dynamics of the infrastructure interface component by specifying the parameters of the component's recovery model.
        | These are defined in the system configuration file by specifying the amounts of resource supplied by the infrastructure system and the time step at which the supply is restored.
        | **Note 1**: The supply dynamics are defined in the system configuration file, but in the component library file the interface component has to have the resource defined.
        | **Note 2**: It is assumed that last value in the Amount key is the initial supply amount and the highest value that the infrastructure system provides. 
        """
        restoration_times = self.get_restoration_times(supply_dynamics)
        step_limits = list(np.divide(restoration_times, restoration_times[-1]))
        step_values = list(np.divide(supply_dynamics['Amount'], max(supply_dynamics['Amount'])))   
        
        self.recovery_model.set_parameters({'RestoredIn': supply_dynamics['RestoredIn'],
                                            'StepLimits': step_limits,
                                            'StepValues': step_values})
        self.supply['Supply'][supply_dynamics['Resource']].set_initial_amount(max(supply_dynamics['Amount']))
    
    def get_restoration_times(self, supply_dynamics: dict) -> list:
        """
        | Sample the restoration times from the distribution defined in the system configuration file.
        | These times define the time steps at which the interface restors the supply amounts defined in the Amount key in the system configuration file.
        """
        restoration_times = []
        for restoration_time_dict in supply_dynamics.get('RestoredIn', []):
            distribution_name, distribution_parameters = list(restoration_time_dict.items())[0]
            restoration_time = getattr(ProbabilityDistribution, distribution_name)(distribution_parameters).sample()
            restoration_times.append(restoration_time)
        return restoration_times
    
class Bridge(StandardiReCoDeSComponent):
    """
    Subclass used to identify bridges in a system. For now that's the only purpose.

    **TODO**: Add specific bridge methods and attributes. Future work.
    """
    pass
        
        