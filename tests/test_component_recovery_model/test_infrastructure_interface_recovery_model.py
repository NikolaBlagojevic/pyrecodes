import pytest
import math
from test_component_recovery_model_inputs import RECOVERY_MODEL_PARAMETERS_INFRASTRUCTURE_INTERFACE, STEP_DICT
from pyrecodes.component_recovery_model.infrastructure_interface_recovery_model import InfrastructureInterfaceRecoveryModel
from pyrecodes.component_recovery_model.abstract_recovery_model import AbstractRecoveryModel
from pyrecodes.relation import relation

class TestInfrastructureInterfaceRecoveryModel:

    @pytest.fixture()
    def recovery_model(self):
        return InfrastructureInterfaceRecoveryModel(RECOVERY_MODEL_PARAMETERS_INFRASTRUCTURE_INTERFACE)
    
    def test_init(self, recovery_model: AbstractRecoveryModel):
        assert len(recovery_model.recovery_activities) == 1
        assert recovery_model.recovery_activities['Recovery'].time_steps == []
        assert recovery_model.recovery_activities['Recovery'].level == 1.0
        assert recovery_model.recovery_activities['Recovery'].duration == 0.0
        assert recovery_model.recovery_activities['Recovery'].rate == math.inf
        assert isinstance(recovery_model.damage_to_functionality_relation, relation.MultipleStep)

    def test_set_initial_damage_level(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_initial_damage_level(0.0)
        assert recovery_model.get_damage_level() == 1.0
        assert recovery_model.recovery_activities['Recovery'].level == 0.0
    
    def test_set_parameters(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_parameters(STEP_DICT)
        assert recovery_model.damage_to_functionality_relation.step_limits == STEP_DICT['StepLimits']
        assert recovery_model.damage_to_functionality_relation.step_values == STEP_DICT['StepValues']
        assert recovery_model.recovery_activities['Recovery'].duration == 50
        assert math.isclose(recovery_model.recovery_activities['Recovery'].rate, 1/50)
    
    def test_recover_no_steps_defined(self, recovery_model: AbstractRecoveryModel):
        recovery_model.recover(0)
        assert recovery_model.recovery_activities['Recovery'].time_steps == []
        assert recovery_model.recovery_activities['Recovery'].level == 1.0
        recovery_model.set_initial_damage_level(1.0)
        recovery_model.recover(1)
        recovery_model.recover(2)
        assert recovery_model.recovery_activities['Recovery'].time_steps == [1]
    
    def test_recover_steps_defined(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_parameters(STEP_DICT)
        recovery_model.set_initial_damage_level(1.0)
        recovery_model.recover(1)
        recovery_model.recover(2)
        assert recovery_model.recovery_activities['Recovery'].time_steps == [1, 2]
        assert math.isclose(recovery_model.recovery_activities['Recovery'].level, 0.04)
        assert recovery_model.get_functionality_level() == 0.0
        
        for time_step in range(3, 12):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['Recovery'].time_steps == list(range(1, 12))
        assert math.isclose(recovery_model.recovery_activities['Recovery'].level, 0.22)
        assert recovery_model.get_functionality_level() == 0.1

        for time_step in range(12, 22):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['Recovery'].time_steps == list(range(1, 22))
        assert math.isclose(recovery_model.recovery_activities['Recovery'].level, 0.42)
        assert recovery_model.get_functionality_level() == 0.6

        for time_step in range(22, 52):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['Recovery'].time_steps == list(range(1, 51))
        assert math.isclose(recovery_model.recovery_activities['Recovery'].level, 1.0)
        assert recovery_model.get_functionality_level() == 1.0


