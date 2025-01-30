from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand
import numpy as np

class SingleResourceSystemMatrixCreator():
    """
    Class to create the system matrix for a single resource used by the utility distribution model.
    """
    
    components: list[Component]
    matrix: np.ndarray
    NUM_COLUMN_SETS = 5  # start_locality/end_locality/supply/demand/demand_met
    ROWS_PER_COMPONENT = 2  # operation demand/recovery demand

    def __init__(self, components: list[Component], resource_name: str):
        self.components = components
        self.resource_name = resource_name
        self.RECOVERY_DEMAND_ROW_OFFSET = len(components)
        self.set_system_matrix_column_ids()
        self.initialize_system_matrix()

    def set_system_matrix_column_ids(self):
        self.START_LOCALITY_COL_ID = 0
        self.END_LOCALITY_COL_ID = 1
        self.SUPPLY_COL_ID = 2
        self.DEMAND_COL_ID = 3
        self.DEMAND_MET_COL_ID = 4

    def initialize_system_matrix(self):
        self.matrix = np.zeros((self.calculate_num_rows_in_system_matrix(),
                                self.calculate_num_columns_in_system_matrix()))

    def calculate_num_rows_in_system_matrix(self):
        return len(self.components) * self.ROWS_PER_COMPONENT

    def calculate_num_columns_in_system_matrix(self):
        return self.NUM_COLUMN_SETS

    def fill_system_matrix(self):
        for row, component in enumerate(self.components):
            self.fill_operation_demand_row(row, component)
            self.fill_recovery_demand_row(row, component)

    def fill_operation_demand_row(self, row: int, component: Component):
        self.matrix[row, :] = np.asarray(self.get_component_properties(component, [
            [SupplyOrDemand.SUPPLY.value, StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value],
            [SupplyOrDemand.DEMAND.value,
             StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]]))

    def fill_recovery_demand_row(self, row: int, component: Component):
        self.matrix[row + self.RECOVERY_DEMAND_ROW_OFFSET, :] = np.asarray(self.get_component_properties(component, [
            [SupplyOrDemand.DEMAND.value,
             StandardiReCoDeSComponent.DemandTypes.RECOVERY_DEMAND.value]]))

    def get_component_properties(self, component: Component, types: list):
        component_properties = np.zeros(self.NUM_COLUMN_SETS)
        for supply_or_demand, type in types:
            value = self.get_current_resource_amount(component, supply_or_demand, type)
            if supply_or_demand == SupplyOrDemand.SUPPLY.value:
                component_properties[self.SUPPLY_COL_ID] = value
            elif supply_or_demand == SupplyOrDemand.DEMAND.value:
                component_properties[self.DEMAND_COL_ID] = value
        component_properties[self.DEMAND_MET_COL_ID] = self.get_initial_demand_met_indicator()
        component_properties[self.START_LOCALITY_COL_ID] = component.get_locality()[0]
        component_properties[self.END_LOCALITY_COL_ID] = component.get_locality()[-1]
        return component_properties

    def get_current_resource_amount(self, component: Component, supply_or_demand: str, type: str):
        return component.get_current_resource_amount(supply_or_demand, type, self.resource_name)     

    def get_initial_demand_met_indicator(self) -> float:
        return 1.0

    def set_demand_met_indicator(self, component_row_id: int, percent_of_met_demand: float):
        self.matrix[component_row_id, self.DEMAND_MET_COL_ID] = percent_of_met_demand

    def get_demand(self, component_row_id: int) -> None:
        return self.matrix[component_row_id, self.DEMAND_COL_ID]

    def update_components(self, components: list[Component]) -> None:
        self.components = components