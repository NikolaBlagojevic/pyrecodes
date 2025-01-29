from pyrecodes.resource_distribution_model.abstract_resource_distribution_model import AbstractResourceDistributionModel
from pyrecodes.resource_distribution_model.utility_distribution_model_constructor import UtilityDistributionModelConstructor
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.resource_distribution_model.single_resource_system_matrix_creator import SingleResourceSystemMatrixCreator
from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand
import json
import math
import numpy as np
import itertools

class UtilityDistributionModel(AbstractResourceDistributionModel):
    """
    | Class to distribute resources in the system. This is the simplest distribution model, which distributes resources based on the priority of the components.
    | Resource distribution is done using the system matrix, containing the supply and demand of each component.
    | No physical laws (e.g., power flow or water flow physics) are considered in the distribution of resources.
    """
    components: list[Component]
    resource_name: str
    transfer_service_distribution_model: ResourceDistributionModel
    system_matrix: SingleResourceSystemMatrixCreator

    def __init__(self, resource_name: str, resource_parameters: dict, components: list[Component]):
        self.constructor = UtilityDistributionModelConstructor()
        self.constructor.construct(resource_name, resource_parameters, components, self)
        self.transfer_service_distribution_model = None

    def distribute(self, time_step: int) -> None:
        if self.distribute_at_this_time_step(time_step):
            self.fill_system_matrix()

            component_priorities_by_row, component_demand_types = self.get_component_priorities()    

            suppliers = []
            for component_row_id, component_demand_type in zip(component_priorities_by_row, component_demand_types):
                suppliers, component_is_supplier = self.add_supplier(component_row_id, suppliers)
                suppliers = self.meet_component_demand(suppliers, component_row_id, component_demand_type)

                if component_is_supplier:                
                    self.reset_supplier_order(suppliers)
            
            self.update_suppliers_based_on_consumption(suppliers)

    def fill_system_matrix(self):
        self.system_matrix.update_components(self.components)
        self.system_matrix.fill_system_matrix()

    def get_component_priorities(self):
        component_priorities_id, component_demand_types = self.priority.get_component_priorities()
        component_row_in_system_matrix = self.set_component_row_based_on_demand_type(component_priorities_id,
                                                                                     component_demand_types)
        return component_row_in_system_matrix, component_demand_types

    def set_component_row_based_on_demand_type(self, component_priorities_id: list[int],
                                               component_demand_types: list[str]):
        component_row_ids = []
        for component_priority_id, component_demand_type in zip(component_priorities_id, component_demand_types):
            if component_demand_type == StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value:
                component_row_ids.append(component_priority_id + self.system_matrix.RECOVERY_DEMAND_ROW_OFFSET)
            elif component_demand_type == StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value:
                component_row_ids.append(component_priority_id)
        return component_row_ids

    def add_supplier(self, component_row_id: int, suppliers: list) -> 'tuple[list, bool]':
        current_supply = self.system_matrix.matrix[component_row_id, self.system_matrix.SUPPLY_COL_ID]
        start_locality = self.system_matrix.matrix[component_row_id, self.system_matrix.START_LOCALITY_COL_ID]
        end_locality = self.system_matrix.matrix[component_row_id, self.system_matrix.END_LOCALITY_COL_ID]
        component_is_supplier = False
        if current_supply > 0:
            suppliers.append({'StartLocality': start_locality, 'EndLocality': end_locality, 
                              'CurrentSupply': current_supply, 'ConsumedAmount': 0, 
                              'ComponentRowID': component_row_id})
            self.put_current_supplier_on_top(suppliers)
            component_is_supplier = True
        return suppliers, component_is_supplier

    def put_current_supplier_on_top(self, suppliers):
        suppliers[0], suppliers[1:] = suppliers[-1], suppliers[0:-1]
        return suppliers

    def meet_component_demand(self, suppliers: dict, component_row_id: int, component_demand_type: str):
        component_demand = self.get_demand(component_row_id)  
        component_localities = [self.system_matrix.matrix[component_row_id, self.system_matrix.START_LOCALITY_COL_ID],
                                self.system_matrix.matrix[component_row_id, self.system_matrix.END_LOCALITY_COL_ID]]
        
        if component_demand > 0.0:
            initial_suppliers = self.deepcopy(suppliers)
            transfer_service_demand = self.get_transfer_service_demand(component_row_id, component_demand_type)
            component_demand_after_distribution, suppliers = self.suppliers_meet_component_demand(suppliers,
                                                                                                  component_demand,  
                                                                                                  component_localities,                                                                                      
                                                                                                  transfer_service_demand)
            self.update_consumed_amounts(suppliers, initial_suppliers)
            
            if component_demand_after_distribution > 0.0:
                percent_of_met_demand = 1 - (component_demand_after_distribution / component_demand)
                self.set_demand_met_indicator(component_row_id, percent_of_met_demand)
                if component_demand_type == StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value:
                    self.reduce_component_supply(component_row_id, percent_of_met_demand)
                elif component_demand_type == StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value:
                    self.set_met_demand_for_recovery_activities(component_row_id, percent_of_met_demand)
                
                # suppliers = self.reset_suppliers(initial_suppliers)

        return suppliers

    def suppliers_meet_component_demand(self, suppliers, component_demand, component_localities, transfer_service_demand):
        for supplier in suppliers:
            supplier_start_locality, supplier_end_locality, current_supply = supplier['StartLocality'], supplier['EndLocality'], supplier['CurrentSupply']
            supply_needed, path_functionality = self.modify_demand_to_account_for_resource_transfer(supplier_start_locality,
                                                                                   supplier_end_locality,
                                                                                   component_demand,
                                                                                   component_localities,                                                                                   
                                                                                   transfer_service_demand)
            # TODO: REFACTOR THIS, CAN BE DONE BETTER - PATH FUNCTIONALITY INTRODUCED TO AVOID SUPPLY_NEEDED = IN SCENARIOS WHEN THERE IS NO PATH BETWEEN TWO LOCALITIES
            if supply_needed < current_supply:
                current_supply -= supply_needed
                component_demand = 0
                supplier = self.update_supplier_resource_amount(supplier, current_supply)
                break
            elif path_functionality > 0:
                component_demand -= current_supply * path_functionality
                current_supply = 0
                supplier = self.update_supplier_resource_amount(supplier, current_supply)

        return component_demand, suppliers

    def update_supplier_resource_amount(self, supplier: dict, current_supply: float) -> None:
        supplier['CurrentSupply'] = current_supply
        return supplier
    
    def update_consumed_amounts(self, suppliers: dict, initial_suppliers: dict) -> None:
        for supplier, initial_supplier in zip(suppliers, initial_suppliers):
            supplier['ConsumedAmount'] += initial_supplier['CurrentSupply'] - supplier['CurrentSupply']
    
    def update_suppliers_based_on_consumption(self, suppliers: list):
        for supplier in suppliers:
            self.components[supplier['ComponentRowID']].update_supply_based_on_consumption(self.resource_name, supplier['ConsumedAmount'])

    def set_demand_met_indicator(self, component_row_id: int, percent_of_met_demand: float):
        self.system_matrix.set_demand_met_indicator(component_row_id, percent_of_met_demand)

    def reduce_component_supply(self, component_row_id: int, percent_of_met_demand: float):
        self.components[component_row_id].update_supply_based_on_unmet_demand(percent_of_met_demand)

    def set_met_demand_for_recovery_activities(self, component_row_id: int, percent_of_met_demand: float):
        self.components[
            component_row_id - self.system_matrix.RECOVERY_DEMAND_ROW_OFFSET].set_met_demand_for_recovery_activities(
            self.resource_name, percent_of_met_demand)

    def reset_supplier_order(self, suppliers: list) -> list:
        suppliers[-1], suppliers[:-1] = suppliers[0], suppliers[1:]
        return suppliers
    
    def deepcopy(self, input: list):
        """
        Method to deepcopy a dict or a list. Alternative to copy.deepcopy as it is too expensive.

        Copied from System class! Consider moving to a separate module.
        """
        return json.loads(json.dumps(input))

    def reset_suppliers(self, initial_suppliers: list) -> list:
        return self.deepcopy(initial_suppliers)

    def get_demand(self, component_row_id: int) -> float:
        return self.system_matrix.get_demand(component_row_id)

    def get_transfer_service_demand(self, component_row_id: int, demand_type: str) -> float:
        """
        Method assumes that the transfer service demand is the same as the demand for the utility resource.
        """
        resource_name = self.resource_name
        
        if demand_type == StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value:
            component_row_id -= self.system_matrix.RECOVERY_DEMAND_ROW_OFFSET
        return self.components[component_row_id].get_current_resource_amount(
                                                                            SupplyOrDemand.DEMAND.value, 
                                                                            demand_type, resource_name)       

    def modify_demand_to_account_for_resource_transfer(self, supplier_start_locality: int, supplier_end_locality: int,
                                                       component_demand: float, component_localities: list[int],
                                                       transfer_service_demand: float) -> float:
        locality_pairs = self.get_locality_pairs(supplier_start_locality, supplier_end_locality, component_localities)
        
        best_path_functionality = self.get_best_path_functionality(locality_pairs, transfer_service_demand)        

        if best_path_functionality > 0:
            return component_demand / best_path_functionality, best_path_functionality
        else:
            return math.inf, best_path_functionality

    def get_locality_pairs(self, supplier_start_locality: int, supplier_end_locality: int, component_localities: list) -> list:
        """
        Finds non-duplicate locality pairs between supplier and component.
        """
        locality_pairs = [[supplier_start_locality, component_localities[0]], [supplier_start_locality, component_localities[1]], 
                            [supplier_end_locality, component_localities[0]], [supplier_end_locality, component_localities[1]]]
        locality_pairs.sort()
        return list(i for i,_ in itertools.groupby(locality_pairs))
               
    def get_best_path_functionality(self, locality_pairs: list, transfer_service_demand: float) -> float:
        best_path_functionality = 0.0
        for start_locality, end_locality in locality_pairs:
            current_path_functionality = self.get_path_functionality(start_locality, end_locality, transfer_service_demand)
            if current_path_functionality > best_path_functionality:
                best_path_functionality = current_path_functionality 
        return best_path_functionality
    
    def get_path_functionality(self, start_locality, end_locality, transfer_service_demand):
        """
        | Method calculates path functionality by comparing the transfer service supply
        of the optimal path with the demand.
        """   
        if start_locality == end_locality:            
            return 1.0
        else:
            optimal_transfer_supply, optimal_path = self.get_optimal_path(start_locality, end_locality)
            return [1.0 if optimal_transfer_supply > transfer_service_demand else 0.0][0]

    def get_optimal_path(self, start_locality: int, end_locality: int) -> float:
        """
        Method outputs the supply capacity and the localities of the optimal path between two localities.
        If transfer services are not needed to transfer the resource, transfer service distribution model
        should not be assigned (stay None) and the method will return math.inf as the optimal path supply capacity.
        Works only when start and end locality are different. If they are the same, method get_path_functionality returns the appropriate values.
        """
        if self.transfer_service_distribution_model:
            return self.transfer_service_distribution_model.get_optimal_path(start_locality, end_locality)
        else:
            return math.inf, None
        
    def get_scope(self, scope='All') -> list:
        """
        Get the scope of the Re-CoDeS Resilience Calculator to get total supply and demand.

        Scope can be 'All' or 'Locality X', where X is the locality number.

        This method works only if you have the system matrix in the distribution model.
        """
        if scope == 'All':
            return list(range(self.system_matrix.matrix.shape[0]))
        elif "Locality" in scope:
            locality_id = int(scope[-1])
            component_rows_in_locality = np.where(np.logical_or(self.system_matrix.matrix[:, self.system_matrix.START_LOCALITY_COL_ID] == locality_id, 
                                                  self.system_matrix.matrix[:, self.system_matrix.END_LOCALITY_COL_ID] == locality_id))
            return component_rows_in_locality
        else:
            raise ValueError('Scope of the Resilience Calculator not well defined: All or Locality X.')
    
    def get_total_supply(self, scope='All') -> float:
        components_to_include = self.get_scope(scope)
        return np.sum(self.system_matrix.matrix[components_to_include, self.system_matrix.SUPPLY_COL_ID])

    def get_total_demand(self, scope='All') -> float:
        components_to_include = self.get_scope(scope)
        return np.sum(self.system_matrix.matrix[components_to_include, self.system_matrix.DEMAND_COL_ID])

    def get_total_consumption(self, scope='All') -> float:
        components_to_include = self.get_scope(scope)
        return np.sum(np.multiply(self.system_matrix.matrix[components_to_include, self.system_matrix.DEMAND_COL_ID],
                                  self.system_matrix.matrix[components_to_include, self.system_matrix.DEMAND_MET_COL_ID]))


