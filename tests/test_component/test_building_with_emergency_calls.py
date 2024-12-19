from pyrecodes.component.component import Component
from pyrecodes.component.building_with_emergency_calls import BuildingWithEmergencyCalls
from test_component_inputs import COMPONENT_NAME, COMPONENT_PARAMETERS, RECOVERY_TIME_STEPS_DENSE, RECOVERY_TIME_STEPS_SPARSE
import pytest
import math


class TestBuildingWithEmergencyCalls():

    @pytest.fixture
    def component(self) -> Component:
        return BuildingWithEmergencyCalls()
    
    @pytest.fixture
    def COMPONENT_PARAMETERS(self):
        COMPONENT_PARAMETERS['ComponentClass'] = 'BuidlingStockUnitWithEmergencyCalls'
        COMPONENT_PARAMETERS['OperationDemand']['Communication'] = {'Amount': 1.0, 
                                                                    'FunctionalityToAmountRelation': 'Linear',
                                                                    'PostDisasterIncreaseDueToEmergencyCalls': 'True'}
        return COMPONENT_PARAMETERS

    def test_update_communication_demand(self, component, COMPONENT_PARAMETERS):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        initial_communication_demand = component.demand['OperationDemand']['Communication'].current_amount
        time_steps = [0, 1, 5, 10, 50]
        target_communication_demands = [initial_communication_demand,
                                        initial_communication_demand * component.COMMUNICATION_DEMAND_MULTIPLIER,
                                        initial_communication_demand * component.COMMUNICATION_DEMAND_MULTIPLIER * math.exp(
                                            component.COMMUNICATION_DEMAND_EXP_DECREASE_COEFF * 4),
                                        initial_communication_demand,
                                        initial_communication_demand]
        for time_step, target_communication_demand in zip(time_steps, target_communication_demands):
            component.update_communication_demand(time_step)
            assert math.isclose(target_communication_demand,
                                component.demand['OperationDemand']['Communication'].current_amount)

    def test_modify_emergency_calls(self, component, COMPONENT_PARAMETERS):
        component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        initial_communication_demand = component.demand['OperationDemand']['Communication'].current_amount
        component.COMMUNICATION_RESOURCE_NAME = 'Communication'
        time_steps = [1, 3, 50]
        target_communication_demands = [initial_communication_demand * component.COMMUNICATION_DEMAND_MULTIPLIER,
                                        initial_communication_demand * component.COMMUNICATION_DEMAND_MULTIPLIER * math.exp(
                                            component.COMMUNICATION_DEMAND_EXP_DECREASE_COEFF * 2),
                                        initial_communication_demand]
        for time_step, target_communication_demand in zip(time_steps, target_communication_demands):
            communication_demand = component.modify_emergency_calls_demand(initial_communication_demand, time_step)
            assert math.isclose(communication_demand, target_communication_demand)
    
    def test_check_if_demand_increase_considered(self, component, COMPONENT_PARAMETERS):
        component.check_if_demand_increase_considered('DemandResource1', COMPONENT_PARAMETERS['OperationDemand']['DemandResource1'])
        assert component.COMMUNICATION_RESOURCE_NAME == ''

        component.check_if_demand_increase_considered('SupplyResource1', COMPONENT_PARAMETERS['Supply']['SupplyResource1'])
        assert component.COMMUNICATION_RESOURCE_NAME == ''

        component.check_if_demand_increase_considered('Communication', COMPONENT_PARAMETERS['OperationDemand']['Communication'])
        assert component.COMMUNICATION_RESOURCE_NAME == 'Communication'