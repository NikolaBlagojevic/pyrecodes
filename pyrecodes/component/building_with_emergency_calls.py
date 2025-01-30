from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand
import math

class BuildingWithEmergencyCalls(StandardiReCoDeSComponent):
    """
    Subclass of the StandardiReCoDeSComponent class that simulates the performance of a building 
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
        | **Note**: this time step should be at or after the DISASTER_TIME_STEP defined in the system configuration file.
    COMMUNICATION_DEMAND_EXP_DECREASE_COEFF : float
        Define the parameter of the exponential function that simulates the post-disaster decrease of the
        demand for communication resource following the initial demand surge.   

    # TODO: Write a decorator to increase/decrease the demand of any resource of any component based on the time step, not functionality. 
    # This class is then the standard component with a decorator.
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
        if resource_parameters.get('PostDisasterIncreaseDueToEmergencyCalls', 'False') == "True":
            self.COMMUNICATION_RESOURCE_NAME = resource_name

