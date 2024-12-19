import pytest
import math
from pyrecodes.component.component import Component
from pyrecodes.component.infrastructure_interface import InfrastructureInterface
from pyrecodes.relation import relation
from test_component_inputs import COMPONENT_NAME, INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY, SUPPLY_DICT_SIMPLE, SUPPLY_DICT_COMPLICATED

class TestInfrastructureInterface():

    @pytest.fixture
    def component(self) -> Component:
        return InfrastructureInterface()

    def test_set_supply_dynamics_simple(self, component):
        component.construct(COMPONENT_NAME, INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY)
        component.set_supply_dynamics(SUPPLY_DICT_SIMPLE['TestInterface'])
        assert component.supply['Supply']['SupplyInterfaceResource1'].initial_amount == 200
        assert component.recovery_model.recovery_activities[component.recovery_model.RECOVERY_ACTIVITY_NAME].duration == 50
        assert isinstance(component.recovery_model.damage_to_functionality_relation, relation.MultipleStep)
        assert component.recovery_model.damage_to_functionality_relation.step_values == [0.0, 0.5, 1]
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[1], 0.4)
        assert component.recovery_model.damage_to_functionality_relation.step_limits[2] == 1
    
    def test_set_supply_dynamics_complicated(self, component):
        component.construct(COMPONENT_NAME, INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY)
        component.set_supply_dynamics(SUPPLY_DICT_COMPLICATED['TestInterface'])
        assert component.supply['Supply']['SupplyInterfaceResource1'].initial_amount == 600
        assert component.recovery_model.recovery_activities[component.recovery_model.RECOVERY_ACTIVITY_NAME].duration == 200
        assert isinstance(component.recovery_model.damage_to_functionality_relation, relation.MultipleStep)
        assert component.recovery_model.damage_to_functionality_relation.step_values == [1/6, 1/12, 0, 1/3, 5/6, 1.0]
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[0], 0)
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[1], 0.1)
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[2], 0.25)
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[3], 0.4)
        assert math.isclose(component.recovery_model.damage_to_functionality_relation.step_limits[4], 0.75)
        assert component.recovery_model.damage_to_functionality_relation.step_limits[-1] == 1

    def test_add_initial_zero_supply(self, component):
        component.construct(COMPONENT_NAME, INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY)
        step_limits = [0, 0.5, 1.0]
        step_values = [0.5, 0.6, 0.7]
        corrected_step_limits, corrected_step_values = component.add_initial_zero_supply(step_limits, step_values)
        assert corrected_step_limits == [0, 0.5, 1.0]
        assert corrected_step_values == [0.5, 0.6, 0.7]

        step_limits = [0.5, 1.0]
        step_values = [0.5, 0.7]
        corrected_step_limits, corrected_step_values = component.add_initial_zero_supply(step_limits, step_values)
        assert corrected_step_limits == [0, 0.5, 1.0]
        assert corrected_step_values == [0, 0.5, 0.7]

    def test_get_restoration_times(self, component):
        component.construct(COMPONENT_NAME, INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY)
        restoration_times = component.get_restoration_times(SUPPLY_DICT_SIMPLE['TestInterface'])
        assert all([math.isclose(target_time, real_time) for target_time, real_time in zip(restoration_times, [20, 50])])

        restoration_times = component.get_restoration_times(SUPPLY_DICT_COMPLICATED['TestInterface'])
        assert all([math.isclose(target_time, real_time) for target_time, real_time in zip(restoration_times, [0, 20, 50, 80, 150, 200])])
    
    def test_supply_dynamics_values(self, component):
        component.construct(COMPONENT_NAME, INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY)
        component.set_supply_dynamics(SUPPLY_DICT_COMPLICATED['TestInterface'])
        component.supply['Supply']['SupplyInterfaceResource1'].component_functionality_to_amount = relation.Linear()
        assert component.supply['Supply']['SupplyInterfaceResource1'].initial_amount == 600
        component.set_initial_damage_level(1.0)
        component.update(0)
        assert component.supply['Supply']['SupplyInterfaceResource1'].current_amount == 100
        recovery_time_step_ranges = [1, 5, 20, 21, 35, 50, 60, 85, 130, 180, 200, 500]
        target_supply_amounts = [100, 100, 50, 50, 50, 0, 200, 200, 500, 500, 600]
        for i, recovery_time_step_upper_bound in enumerate(recovery_time_step_ranges[1:]):
            recovery_time_step_lower_bound = recovery_time_step_ranges[i]
            for time_step in range(recovery_time_step_lower_bound, recovery_time_step_upper_bound):
                component.recover(time_step)
                component.update(time_step)
            assert math.isclose(component.supply['Supply']['SupplyInterfaceResource1'].current_amount,
                                target_supply_amounts[i])
