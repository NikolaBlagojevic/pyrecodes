from pyrecodes.component_configurator.repair_configurator import RepairConfigurator
from pyrecodes.constants import METER_TO_MILE, INCH_TO_MILE, FEET_TO_MILE
import math

class R2DRepairConfigurator(RepairConfigurator):

    def set_repair_demand(self, component_DS: int, recovery_demand_setter: callable) -> None:
        # TODO: This works only if there is a single resource needed for repair. Fix if multiple resources are needed.
        repair_resource_name = list(self.component.recovery_model.recovery_activities['Repair'].demand.keys())[0]
        repair_demand = self.get_repair_demand(component_DS)            
        recovery_demand_setter(self.component, 'Repair', repair_resource_name, repair_demand)
    
    def set_repair_time(self, component_data: dict) -> None:     
        repair_time = self.get_repair_time(component_data)
        if repair_time is not None:
            self.component.recovery_model.recovery_activities['Repair'].set_duration(
                {"Deterministic": {"Value": repair_time}})                       
            
    def get_repair_time(self, component_data: dict) -> int:    
        if 'Repair' in component_data['Loss']:
            return max(list(component_data['Loss']['Repair']['Time'].values()))
        else:
            return None

    def get_repair_cost(self, component_data: dict) -> float:
        # TODO: Check how to exactly get the repair cost ratio. At the moment I take the max of all ratios.
        # Assume the ratios are given as percents as they are higher than 1. Fix when Jinyan provides the correct data.
        if 'Repair' in component_data['Loss']:
            repair_cost_ratio = max(list(component_data['Loss']['Repair']['Cost'].values())) / 100
            return repair_cost_ratio * component_data['Information']['GeneralInformation'].get('ReplacementCost', 0)
        else:
            return None

    def get_repair_demand(self, building_DS: int) -> int:
        # To be implemented in the child classes.
        pass
    
class R2DBuildingRepairConfigurator(R2DRepairConfigurator):

    def get_repair_demand(self, component_damage_state: int) -> int:
        repair_crew_demand = math.ceil(self.component.area / self.system_level_data['REPAIR_CREW_DEMAND_PER_SQFT'].get(f'DS{component_damage_state}', math.inf))
        return min(self.system_level_data['MAX_REPAIR_CREW_DEMAND_PER_BUILDING'], repair_crew_demand)
    
class R2DRoadwayRepairConfigurator(R2DRepairConfigurator):

    def get_repair_demand(self, component_damage_state: int) -> int:
        if component_damage_state > 0:
            return math.ceil((self.component.length/METER_TO_MILE) * self.system_level_data['REPAIR_CREW_DEMAND_PER_MILE_ROADWAY'])
        else:
            return 0
    
class R2DPipeRepairConfigurator(R2DRepairConfigurator):

    def get_repair_demand(self, component_damage_state: int) -> int:
        if component_damage_state > 0:
            return math.ceil((self.component.length/METER_TO_MILE) * self.system_level_data['REPAIR_CREW_DEMAND_PER_MILE_PIPE'])
        else:
            return 0
    
class R2DBridgeRepairConfigurator(R2DRepairConfigurator):

    def get_repair_demand(self, component_damage_state: int) -> int:
        if component_damage_state > 0:
            bridge_length = (self.component.num_spans * self.component.max_span_length) / INCH_TO_MILE # TODO: This is a conservative estimate, check if you can do something better.
            return math.ceil(bridge_length * self.system_level_data['REPAIR_CREW_DEMAND_PER_MILE_BRIDGE'])
        else:
            return 0

class R2DTunnelRepairConfigurator(R2DRepairConfigurator):

    def get_repair_demand(self, component_damage_state: int) -> int:
        if component_damage_state > 0:
            return math.ceil((self.component.length/FEET_TO_MILE) * self.system_level_data['REPAIR_CREW_DEMAND_PER_MILE_TUNNEL'])
        else:
            return 0
    