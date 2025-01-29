from pyrecodes.component_configurator.repair_configurator import RepairConfigurator
from pyrecodes.constants import METER_TO_MILE, INCH_TO_MILE, FEET_TO_MILE
import math

class R2DRepairConfigurator(RepairConfigurator):
    """
    | Class that configures the parameters of the repair and financing activity of R2D components. 
    
    | These parameters are repair duration, repair cost and repair resource demand.
    """

    def set_repair_demand(self, component_DS: int, recovery_demand_setter: callable) -> None:
        """
        | Method that sets the repair resource demand of the component. 

        | At the moment, it only works if there is a single resource needed for repair. Modify if multiple resources are needed.
        """
        repair_resource_name = list(self.component.recovery_model.recovery_activities['Repair'].demand.keys())[0]
        repair_demand = self.get_repair_demand(component_DS)            
        recovery_demand_setter(self.component, 'Repair', repair_resource_name, repair_demand)
    
    def set_repair_time(self, component_data: dict) -> None:
        """
        | Method sets the repair duration of the component as deterministic by default. 
        | It is assumed that the uncertainty is captured in the R2D output files.
        """
        repair_time = self.get_repair_time(component_data)
        if repair_time is not None:
            self.component.recovery_model.recovery_activities['Repair'].set_duration(
                {"Deterministic": {"Value": repair_time}})                       
            
    def get_repair_time(self, component_data: dict, default_repair_time=30) -> int:   
        """
        | Method that gets the repair duration of the component from the R2D output files. 
        """ 
        if 'Repair' in component_data['Loss']:
            repair_time = max(list(component_data['Loss']['Repair']['Time'].values()))
            if repair_time == 0:
                print(f'Repair time is 0 for component {component_data["Information"]["GeneralInformation"]["AIM_id"]}. Setting it to default value of {default_repair_time} days.')
                return default_repair_time
            return repair_time
        else:
            return None

    def get_repair_cost(self, component_data: dict) -> float:
        """
        | Method to get the repair cost of the component from the R2D output files.
        | It is assumed that R2D provides the repair cost ratio as a value from 0 to 1. If repair cost is higher than 1, it is assumed that repair cost is provided in (2020) dollar values.
        | Repair cost is taken as the maximum over all repair costs provided by R2D.
        """
        if 'Repair' in component_data['Loss']:
            repair_cost = max(list(component_data['Loss']['Repair']['Cost'].values()))
            if repair_cost < 1.0:
                return repair_cost * component_data['Information']['GeneralInformation'].get('ReplacementCost', 0)
            else:
                return repair_cost
        else:
            return None

    def get_repair_demand(self, building_DS: int) -> int:
        """
        | To be implemented by the child classes.
        """
        pass
    
class R2DBuildingRepairConfigurator(R2DRepairConfigurator):
    """
    Class that configures repair activities of R2D buildings.
    """

    def get_repair_demand(self, component_damage_state: int) -> int:
        """
        | Method that calculates the repair crew demand for the building component. 
        | The demand is calculated based on the area of the building and the repair crew demand per square foot for different damage states defined in the system configuration file.
        """
        repair_crew_demand = math.ceil(self.component.area / self.system_level_data['REPAIR_CREW_DEMAND_PER_SQFT'].get(f'DS{component_damage_state}', math.inf))
        return min(self.system_level_data['MAX_REPAIR_CREW_DEMAND_PER_BUILDING'], repair_crew_demand)
    
class R2DPipeRepairConfigurator(R2DRepairConfigurator):
    """
    Class that configures repair activities of R2D pipes.
    """

    def get_repair_demand(self, component_damage_state: int) -> int:
        """
        | Method that calculates the repair crew demand for the pipe component.
        | The demand is calculated based on the length of the pipe and the repair crew demand per mile defined in the system configuration file.
        | It is assumed that pipe length is defined in meters in the component object.
        """
        if component_damage_state > 0:
            return math.ceil((self.component.length/METER_TO_MILE) * self.system_level_data['REPAIR_CREW_DEMAND_PER_MILE_PIPE'])
        else:
            return 0
        
class R2DTransportationRepairConfigurator(R2DRepairConfigurator):

    def get_repair_cost(self, component_data: dict) -> float:
        """
        | Method to get the repair cost of the component from the R2D output files.
        | R2D provides the repair cost of transportation components (Bridge, Roadway, Tunnel) in (2020) dollar values, not ratios as for buildings.
        | Repair cost is taken as the maximum over all repair cost ratios provided by R2D.
        *TODO* This method might be redundant, since parent class takes care of the repair cost calculation.
        """
        if 'Repair' in component_data['Loss']:
            return max(list(component_data['Loss']['Repair']['Cost'].values()))
        else:
            return None
        
class R2DRoadwayRepairConfigurator(R2DTransportationRepairConfigurator):
    """
    Class that configures repair activities of R2D roadways.
    """

    def get_repair_demand(self, component_damage_state: int) -> int:
        """
        | Method that calculates the repair crew demand for the roadway component.
        | The demand is calculated based on the length of the roadway and the repair crew demand per mile defined in the system configuration file.
        | It is assumed that roadway length is defined in meters in the component object.
        """
        if component_damage_state > 0:
            return math.ceil((self.component.length/METER_TO_MILE) * self.system_level_data['REPAIR_CREW_DEMAND_PER_MILE_ROADWAY'])
        else:
            return 0
    
class R2DBridgeRepairConfigurator(R2DTransportationRepairConfigurator):
    """
    Class that configures repair activities of R2D bridges.
    """

    def get_repair_demand(self, component_damage_state: int) -> int:
        """
        | Method that calculates the repair crew demand for the bridge component.
        | The demand is calculated based on the length of the bridge and the repair crew demand per mile defined in the system configuration file.
        | Bridge length is conservatively estimates as the product of the number of spans and maximum span length assumed in inches.
        | If more accurate bridge length information is provided in the R2D output files, this method should be updated.
        """
        if component_damage_state > 0:
            bridge_length = (self.component.num_spans * self.component.max_span_length) / INCH_TO_MILE # TODO: This is a conservative estimate, check if you can do something better.
            return math.ceil(bridge_length * self.system_level_data['REPAIR_CREW_DEMAND_PER_MILE_BRIDGE'])
        else:
            return 0

class R2DTunnelRepairConfigurator(R2DTransportationRepairConfigurator):
    """
    Class that configures repair activities of R2D tunnels.
    """

    def get_repair_demand(self, component_damage_state: int) -> int:
        """
        | Method that calculates the repair crew demand for the tunnel component.
        | The demand is calculated based on the length of the tunnel and the repair crew demand per mile defined in the system configuration file.
        | It is assumed that tunnel length is defined in feet in the component object.
        """
        if component_damage_state > 0:
            return math.ceil((self.component.length/FEET_TO_MILE) * self.system_level_data['REPAIR_CREW_DEMAND_PER_MILE_TUNNEL'])
        else:
            return 0
    