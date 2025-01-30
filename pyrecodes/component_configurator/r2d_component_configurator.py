from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
from pyrecodes.component.component import Component
from pyrecodes.component_configurator.r2d_dict_getter import R2DDictGetter, R2DPipeDictGetter
from pyrecodes.component_configurator.r2d_repair_configurator import R2DBuildingRepairConfigurator, R2DRoadwayRepairConfigurator, R2DPipeRepairConfigurator, R2DBridgeRepairConfigurator, R2DTunnelRepairConfigurator
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
import json
import shapely
import pyproj
from abc import abstractmethod

MAX_DAMAGE_STATE = 4

class R2DComponentConfigurator(ComponentConfigurator):
    """
    Abstract class for R2D component configurators.
    """

    def set_parameters(self, component: Component, locality: list, component_data: dict, component_damage_state: int): 
        """
        Method to set component parameters based on the data provided in the R2D output files.
        """
        self.set_geometry(component, component_data)   
        super().set_parameters(component, locality, component_data, component_damage_state)
        self.set_general_information(component, component_data)
        self.set_asset_ids(component, component_data) 
        self.set_r2d_dict_getter(component)
        self.set_supply_parameters(component, component_data)      
        return component
    
    def set_general_information(self, component: Component, component_data: dict):
        component.general_information = component_data['Information']['GeneralInformation']
        component.general_information[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value] = {resource.name: resource.current_amount for resource in component.demand[StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value].values()}
        component.general_information[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value] = {resource.name: resource.current_amount for resource in component.demand[StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value].values()}
    
    @abstractmethod
    def set_geometry(self, component, component_data: dict):
        """
        Implemented by subclasses.
        """
        pass

    @abstractmethod
    def set_supply_parameters(self, component, component_data: dict):
        """
        Implemented by subclasses.
        """
        pass

    def set_asset_ids(self, component, component_data:dict):
        component.asset_type = component_data['AssetType']
        component.asset_subtype = component_data['AssetSubtype']
        component.aim_id = component_data['Information']['GeneralInformation']['AIM_id']
        component.r2d_comp = True

    @abstractmethod
    def set_repair_configurator(self, component: Component) -> None:
        """
        Implemented by subclasses.
        """
        pass  
    
    def set_r2d_dict_getter(self, component: Component):        
        component.r2d_dict_getter = R2DDictGetter(component)

    def get_damage_state(self, damage_info: dict) -> int:
        """
        | Method to get the damage state of an R2D component based on the damage information provided in the R2D output files.
        | If building collapsed, damage state 4 is returned.
        | If not collapsed, maximum damage state of all damage states provided in the R2D output files is used.
        """
        if damage_info['Damage']['collapse-0'] == 1:
            return MAX_DAMAGE_STATE
        else:
            return max([value for key, value in damage_info['Damage'].items() if not('collapse' in key)]+ [0])

    
class R2DBuildingConfigurator(R2DComponentConfigurator):
    """
    Class that configures parameters of building components as provided in the R2D output files.
    """

    SYSTEM_LEVEL_DATA = ['START_TIME_STEP', 'MAX_TIME_STEP', 'MAX_REPAIR_CREW_DEMAND_PER_BUILDING',
                        'REPAIR_CREW_DEMAND_PER_SQFT',
                        'DEFAULT_REPAIR_DURATION_DICT', 'DEMAND_PER_PERSON', 'HOUSING_RESOURCES']

    def set_parameters(self, component: Component, locality: list, component_data: dict, component_DS: int): 
        super().set_parameters(component, locality, component_data, component_DS)     
        self.set_operation_demand_parameters(component, component_data)
        return component
    
    def set_repair_configurator(self, component: Component) -> None:
        self.repair_configurator = R2DBuildingRepairConfigurator(component, self.system_level_data)   

    def set_geometry(self, component, building_data: dict):
        self.set_building_area(component, building_data)
        self.set_building_footprint(component, building_data)
        self.set_building_num_stories(component, building_data)
    
    def set_building_area(self, component: Component, building_data: dict) -> None:
        component.area = self.get_total_building_area(building_data)

    def set_building_footprint(self, component: Component, building_data: dict) -> None:
        component.footprint = json.loads(building_data['Information']['GeneralInformation']['Footprint'])

    def set_building_num_stories(self, component: Component, building_data: dict) -> None:
        component.num_stories = building_data['Information']['GeneralInformation']['NumberOfStories']

    def get_total_building_area(self, building_data: dict) -> float:
        return building_data['Information']['GeneralInformation']['PlanArea'] * \
            building_data['Information']['GeneralInformation']['NumberOfStories']

    def get_building_housing_capacity(self, building_data: dict) -> int:  
        return building_data['Information']['GeneralInformation']['Population'] 
    
    def set_supply_parameters(self, component: Component, building_data: dict):
        if self.system_level_data['HOUSING_RESOURCES'] is not None:
            building_housing_capacity = self.get_building_housing_capacity(building_data)
            # TODO: Figure out a better way to define the housing resources - defining them in the system configuration file is not optimal.
            for housing_resource_name in self.system_level_data.get('HOUSING_RESOURCES', []):
                self.set_component_supply(component, housing_resource_name, building_housing_capacity)
    
    def set_operation_demand_parameters(self, component: Component, building_data: dict) -> None:
        self.set_housing_demand_parameters(component, building_data)
        self.set_infrastructure_demand_parameters(component, building_data)

    def set_housing_demand_parameters(self, component: Component, building_data: dict) -> None:
        # TODO: Not dry, similar to set_supply_parameters. Fix this.
        if self.system_level_data['HOUSING_RESOURCES'] is not None:
            building_housing_capacity = self.get_building_housing_capacity(building_data)
            for housing_resource_name in self.system_level_data.get('HOUSING_RESOURCES', []):
                self.set_component_operation_demand(component, housing_resource_name, building_housing_capacity)

    def set_infrastructure_demand_parameters(self, component: Component, building_data: dict) -> None:
        """
        |  Method sets the infrastructure demand for a building component based on two sources:
        |  1. Based on the number of people living in the building.
        | 2. Based on the demand data provided in the building data dictionary.

        | Note that the demand provided in the building data dictionary overwrites the demand based on the number of people.
        """          
        self.set_infrastructure_demand_parameters_based_on_number_of_people(component, building_data)
        self.set_infrastructure_demand_parameters_directly_based_on_building_data(component, building_data)
        
    def set_infrastructure_demand_parameters_based_on_number_of_people(self, component: Component, building_data: dict) -> None:
        """
        | Method sets the infrastructure demand for a building component based on the number of people living in the building (i.e., housing capacity).
        | Note that only the resources defined in the "DEMAND_PER_PERSON" attribute in the system configuration file are considered.
        """
        if self.system_level_data['DEMAND_PER_PERSON'] is not None:
            building_housing_capacity = self.get_building_housing_capacity(building_data)
            operation_demand_resources = [resource_name for resource_name in self.system_level_data.get('DEMAND_PER_PERSON', {}).keys()]
            for operation_demand_resource in operation_demand_resources:
                amount = building_housing_capacity*self.system_level_data['DEMAND_PER_PERSON'][operation_demand_resource]
                self.set_component_operation_demand(component, operation_demand_resource, amount)

    def set_infrastructure_demand_parameters_directly_based_on_building_data(self, component: Component, building_data: dict) -> None:
        """
        | Method sets the infrastructure demand for a building component based on the demand data provided in the building data dictionary.
        | This allows to overwrite the demand based on the number of people living in the building in case building's demand is not correlated to the number of people living in the building (e.g., a commercial or industrial building).
        """
        if 'Demand' in building_data['Information']['GeneralInformation']:
            for resource_name, amount in building_data['Information']['GeneralInformation']['Demand'].items():
                self.set_component_operation_demand(component, resource_name, amount)

class R2DTransportationComponentConfigurator(R2DComponentConfigurator):

    def set_general_information(self, component: Component, component_data: dict):
        super().set_general_information(component, component_data)
        component.general_information['FunctionalityLevel'] = 1.0

class R2DRoadwayConfigurator(R2DTransportationComponentConfigurator):
    """
    Class that sets parameters of a Roadway as provided in the R2D output files.
    """

    SYSTEM_LEVEL_DATA = ['START_TIME_STEP', 'MAX_TIME_STEP',                       
                        'DEFAULT_REPAIR_DURATION_DICT', 'REPAIR_CREW_DEMAND_PER_MILE_ROADWAY']

    def set_geometry(self, component, component_data: dict):
        component.geometry = component_data['Information']['GeneralInformation']['geometry']
        component.length = self.get_road_length(component)

    def set_repair_configurator(self, component: Component) -> None:
        self.repair_configurator = R2DRoadwayRepairConfigurator(component, self.system_level_data)  
    
    def set_supply_parameters(self, component: Component, component_data: dict) -> None:
        # TODO: Not sure what is really needed here.
        pass
    
    def get_road_length(self, component) -> float:
        shapely_line = shapely.from_wkt(component.geometry)
        # Transformer for reprojecting from WGS84 (EPSG:4326) to UTM Zone 10N (EPSG:32610) to get the length in meters.
        transformer = pyproj.Transformer.from_crs("epsg:4326", "epsg:32610", always_xy=True)
        utm_coordinates = [transformer.transform(*coord) for coord in shapely_line.coords]
        utm_line = shapely_line.__class__(utm_coordinates)
        length_in_meters = utm_line.length        
        return length_in_meters
    
class R2DPipeConfigurator(R2DComponentConfigurator):
    """
    Class that sets parameters of a Pipe as provided in the R2D output files.
    """

    SYSTEM_LEVEL_DATA = ['START_TIME_STEP', 'MAX_TIME_STEP',                       
                        'DEFAULT_REPAIR_DURATION_DICT', 'REPAIR_CREW_DEMAND_PER_MILE_PIPE']
    
    def __init__(self, system_level_data: dict, recovery_time_stepping: list) -> None:
        super().__init__(system_level_data, recovery_time_stepping)

    def set_geometry(self, component, component_data: dict):
        component.length = component_data['Information']['GeneralInformation']['Len']

    def set_repair_configurator(self, component: Component) -> None:
        self.repair_configurator = R2DPipeRepairConfigurator(component, self.system_level_data)  
    
    def set_supply_parameters(self, component: Component, component_data: dict) -> None:
        """
        At the moment, pipe supply is not defined. Pipe's ability to transfer water is based on its functionality level and defined in the r2d_dict attribute.
        """
        pass
    
    def set_r2d_dict_getter(self, component: Component):        
        component.r2d_dict_getter = R2DPipeDictGetter(component)

    def get_damage_state(self, damage_info: dict) -> int:
        """
        | Method to get the damage state of R2D pipes based on the damage information provided in the R2D output files.
        | Aggreggate dmage states are considered. Leak = 1. Break = 2.
        """
        return max([damage_info['Damage'].get('aggregate-1', 0), damage_info['Damage'].get('aggregate-2', 0)])

class R2DBridgeConfigurator(R2DTransportationComponentConfigurator):
    """
    Class that sets parameters of a Bridge as provided in the R2D output files.

    Not clear how the class should look like at the moment. Future work.
    """

    SYSTEM_LEVEL_DATA = ['START_TIME_STEP', 'MAX_TIME_STEP',                       
                        'DEFAULT_REPAIR_DURATION_DICT', 'REPAIR_CREW_DEMAND_PER_MILE_BRIDGE']

    def set_geometry(self, component, component_data: dict):
        # TODO: Check what is really needed here.
        component.geometry = component_data['Information']['GeneralInformation']['geometry']
        component.num_spans = component_data['Information']['GeneralInformation']['NumOfSpans']
        component.max_span_length = component_data['Information']['GeneralInformation']['MaxSpanLength']
        component.deck_width = component_data['Information']['GeneralInformation']['DeckWidth']

    def set_repair_configurator(self, component: Component) -> None:
        self.repair_configurator = R2DBridgeRepairConfigurator(component, self.system_level_data)  

    def set_supply_parameters(self, component: Component, component_data: dict) -> None:
        pass
    
class R2DTunnelConfigurator(R2DTransportationComponentConfigurator):
    """
    Class that sets parameters of a Tunnel as provided in the R2D output files.

    Not clear how the class should look like at the moment. Future work.
    """

    SYSTEM_LEVEL_DATA = ['START_TIME_STEP', 'MAX_TIME_STEP',                       
                        'DEFAULT_REPAIR_DURATION_DICT', 'REPAIR_CREW_DEMAND_PER_MILE_TUNNEL']

    def set_geometry(self, component, component_data: dict):
        component.length = component_data['Information']['GeneralInformation']['TunnelLength_ft']

    def set_repair_configurator(self, component: Component) -> None:
        self.repair_configurator = R2DTunnelRepairConfigurator(component, self.system_level_data)  
    
    def set_supply_parameters(self, component: Component, component_data: dict) -> None:
        pass       
    
