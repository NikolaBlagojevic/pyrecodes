from pyrecodes.component.component import Component
from pyrecodes.component.component import SupplyOrDemand
from enum import Enum
from pyrecodes.utilities import get_class
from pyrecodes.relation import relation

class StandardiReCoDeSComponent(Component):
    """
    Implementation of the Component interface to define standard functionality of a component in pyrecodes.
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
        target_recovery_model = get_class(recovery_model_parameters['FileName'],
                                          recovery_model_parameters['ClassName'],
                                          "component_recovery_model")
        self.recovery_model = target_recovery_model(recovery_model_parameters)
    
    def set_recovery_time_steps(self, recovery_time_steps: list) -> None:
        self.recovery_model.set_recovery_time_steps(recovery_time_steps)
    
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
        try:
            self.recovery_model.set_initial_damage_level(damage_level)
        except ZeroDivisionError as e:
            print(f'Error: {e}')

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
        for resource_object in self.demand[self.DemandTypes.OPERATION_DEMAND.value].values():
            if resource_object.initial_amount > 0:
                return True
        return False

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
            return not(isinstance(self.supply[self.SupplyTypes.SUPPLY.value][resource_name].unmet_demand_to_amount, relation.Constant))
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
    
    def form_resource(self, resource_name: str, resource_parameters: dict, 
                      default_resource_class_name = 'ConcreteResource', 
                      default_resource_file_name = 'concrete_resource') -> None:
        """
        | Form a resource object based on the resource_name and resource_parameters.
        | Default resource class is ConcreteResource. Specify a different default resource class if needed.
        | Check out the resource parameters dict in the component library files in the examples to get the dict structure.
        | **TODO**: Add the dict structure here. Future work.
        """
        resource_class_dict = resource_parameters.get('ResourceClass', {'FileName': default_resource_file_name, 'ClassName': default_resource_class_name})
        target_resource_object = get_class(resource_class_dict['FileName'], 
                                           resource_class_dict['ClassName'],
                                           'resource')
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