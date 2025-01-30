import pytest
from test_component_recovery_model_inputs import RECOVERY_MODEL_PARAMETERS_NO_ACTIVITY
from pyrecodes.component_recovery_model.no_recovery_activity_model import NoRecoveryActivityModel
from pyrecodes.component_recovery_model.abstract_recovery_model import AbstractRecoveryModel

class TestNoRecoveryActivityComponentRecoveryModel:

    @pytest.fixture()
    def recovery_model(self):
        return NoRecoveryActivityModel(RECOVERY_MODEL_PARAMETERS_NO_ACTIVITY)  
    
    def test_init(self, recovery_model: AbstractRecoveryModel):
        assert len(recovery_model.recovery_activities) == 0        

    def test_set_initial_damage_level(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_initial_damage_level(0.0)
        assert recovery_model.get_damage_level() == 0.0

    def test_set_nonzero_initial_damage_level(self, recovery_model: AbstractRecoveryModel):
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(0.5)

    def test_get_functionality_level(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.get_functionality_level() == 1.0

    def test_get_damage_level(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.get_damage_level() == 0.0

    def test_get_demand(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.get_demand() == {}
