import pytest
from test_component_recovery_model_inputs import RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY, RECOVERY_TIME_STEPS_DENSE, RECOVERY_TIME_STEPS_SPARSE
from pyrecodes.component_recovery_model.abstract_recovery_model import AbstractRecoveryModel
from pyrecodes.relation import relation

class TestAbstractRecoveryModel:
    
    @pytest.fixture
    def recovery_model(self):
        return AbstractRecoveryModel(RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY)

    def test_init(self, recovery_model):
        assert recovery_model.recovery_activities == {}

    def test_set_damage_functionality(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_damage_functionality(RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY['DamageFunctionalityRelation'])
        damage_functionality_type = RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY['DamageFunctionalityRelation']['Type']
        assert isinstance(recovery_model.damage_to_functionality_relation, getattr(relation, damage_functionality_type))

        recovery_model.set_damage_functionality({})
        assert isinstance(recovery_model.damage_to_functionality_relation, relation.Constant)

    def test_set_recovery_time_steps(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        assert recovery_model.recovery_time_steps == RECOVERY_TIME_STEPS_DENSE

        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        assert recovery_model.recovery_time_steps == RECOVERY_TIME_STEPS_SPARSE

    def test_get_time_step_length(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        assert recovery_model.get_time_step_length(0) == (0, 1)
        assert recovery_model.get_time_step_length(1) == (1, 2)       
        assert recovery_model.get_time_step_length(10) == (10, 11)

        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        assert recovery_model.get_time_step_length(0) == (0, 1)
        assert recovery_model.get_time_step_length(5) == (1, 6)
        assert recovery_model.get_time_step_length(100) == (96, 101)
        assert recovery_model.get_time_step_length(495) == (491, 496)

        recovery_model.set_recovery_time_steps([4, 8, 12, 15, 22, 40])
        assert recovery_model.get_time_step_length(4) == (4, 5)
        assert recovery_model.get_time_step_length(8) == (5, 9)
        assert recovery_model.get_time_step_length(12) == (9, 13)
        assert recovery_model.get_time_step_length(15) == (13, 16)
        assert recovery_model.get_time_step_length(22) == (16, 23)
        assert recovery_model.get_time_step_length(40) == (23, 41)
        

       

 
