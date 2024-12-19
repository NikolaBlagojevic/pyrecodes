import pytest
import math
import numpy as np
from pyrecodes.component_recovery_model.concrete_recovery_activity import ConcreteRecoveryActivity

class TestConcreteRecoveryActivity:

    @pytest.fixture
    def recovery_activity(self):
        return ConcreteRecoveryActivity('DummyActivity')

    def test_init(self, recovery_activity: ConcreteRecoveryActivity):
        assert recovery_activity.name == 'DummyActivity'
        assert recovery_activity.level == 0.0
        assert recovery_activity.time_steps == []
        assert recovery_activity.demand_met == {}
        assert recovery_activity.demand == {}
        assert recovery_activity.preceding_activities_finished == False

    def test_set_name(self, recovery_activity: ConcreteRecoveryActivity):
        assert recovery_activity.name == 'DummyActivity'
        recovery_activity.set_name('AnotherDummyActivity')
        assert recovery_activity.name == 'AnotherDummyActivity'

    def test_set_level(self, recovery_activity: ConcreteRecoveryActivity):
        assert recovery_activity.level == 0.0
        recovery_activity.set_level(0.4)
        assert recovery_activity.level == 0.4

    def test_set_too_high_level(self, recovery_activity: ConcreteRecoveryActivity):
        with pytest.raises(ValueError):
            recovery_activity.set_level(1.5)

    def test_set_negative_level(self, recovery_activity: ConcreteRecoveryActivity):
        with pytest.raises(ValueError):
            recovery_activity.set_level(-1.5)

    def test_deterministic_sample_duration(self, recovery_activity: ConcreteRecoveryActivity):
        distribution = {'Deterministic': {'Value': 5}}
        deterministic_sample = recovery_activity.sample_duration(distribution)
        assert math.isclose(deterministic_sample, 5)

    def test_lognormal_sample_duration(self, recovery_activity: ConcreteRecoveryActivity):
        distribution = {'Lognormal': {'Median': 2, 'Dispersion': 1}}
        lognormal_samples = [recovery_activity.sample_duration(distribution) for _ in range(100000)]
        assert math.isclose(np.median(lognormal_samples), 2, abs_tol=0.05) and math.isclose(
            np.std(np.log(lognormal_samples)), 1, abs_tol=0.01)

    def test_set_deterministic_duration(self, recovery_activity: ConcreteRecoveryActivity):
        distribution = {'Deterministic': {'Value': 5}}
        recovery_activity.set_duration(distribution)
        assert math.isclose(recovery_activity.duration, 5) and math.isclose(recovery_activity.rate, 1 / 5)

    def test_set_negative_duration(self, recovery_activity: ConcreteRecoveryActivity):
        distribution = {'Deterministic': {'Value': -5}}
        with pytest.raises(ValueError):
            recovery_activity.set_duration(distribution)

    def test_set_empty_preceding_activities(self, recovery_activity: ConcreteRecoveryActivity):
        preceding_activities = []
        recovery_activity.set_preceding_activities(preceding_activities)
        assert recovery_activity.preceding_activities == []

    def test_set_two_preceding_activities(self, recovery_activity: ConcreteRecoveryActivity):
        preceding_activities = ['Activity 1', 'Acitivity 2']
        recovery_activity.set_preceding_activities(preceding_activities)
        assert recovery_activity.preceding_activities == ['Activity 1', 'Acitivity 2']

    def test_set_preceding_activities_twice(self, recovery_activity: ConcreteRecoveryActivity):
        preceding_activities = ['Activity 1', 'Activity 2']
        recovery_activity.set_preceding_activities(preceding_activities)
        recovery_activity.set_preceding_activities(preceding_activities)
        assert recovery_activity.preceding_activities == ['Activity 1', 'Activity 2']

    def test_initial_preceding_activities_finished(self,
                                                   recovery_activity: ConcreteRecoveryActivity):
        assert recovery_activity.preceding_activities_finished == False

    def test_set_preceding_activities_finished(self,
                                               recovery_activity: ConcreteRecoveryActivity):
        recovery_activity.set_preceding_activities_finished(True)
        assert recovery_activity.preceding_activities_finished == True

    def test_set_demand(self, recovery_activity: ConcreteRecoveryActivity):
        demand = [{'Resource': 'Resource 1', 'Amount': 5}, {'Resource': 'Resource 2', 'Amount': 3}]
        recovery_activity.set_demand(demand)
        assert all([recovery_activity.demand['Resource 1'].initial_amount == 5,
                    recovery_activity.demand['Resource 1'].current_amount == 5,
                    recovery_activity.demand['Resource 2'].initial_amount == 3,
                    recovery_activity.demand['Resource 2'].current_amount == 3])

    def test_set_demand_met(self, recovery_activity: ConcreteRecoveryActivity):
        demand = [{'Resource': 'Resource 1', 'Amount': 5}, {'Resource': 'Resource 2', 'Amount': 3}]
        recovery_activity.set_demand(demand)
        recovery_activity.set_demand_met('Resource 1', 0.5)
        assert recovery_activity.demand_met['Resource 1'] == 0.5
        recovery_activity.set_demand_met('Resource 2', 0.9)
        assert recovery_activity.demand_met['Resource 2'] == 0.9

    def test_set_invalid_demand_met(self, recovery_activity: ConcreteRecoveryActivity):
        demand = [{'Resource': 'Resource 1', 'Amount': 5}]
        recovery_activity.set_demand(demand)
        with pytest.raises(ValueError):
            recovery_activity.set_demand_met('Resource 1', -0.5)

    def test_get_demand(self, recovery_activity: ConcreteRecoveryActivity):
        demand = [{'Resource': 'Resource 1', 'Amount': 5}, {'Resource': 'Resource 2', 'Amount': 3}]
        recovery_activity.set_demand(demand)
        demand = recovery_activity.get_demand()
        assert all([demand['Resource 1'].initial_amount == 5,
                    demand['Resource 1'].current_amount == 5,
                    demand['Resource 2'].initial_amount == 3,
                    demand['Resource 2'].current_amount == 3])

    def test_recover_without_set_duration(self, recovery_activity: ConcreteRecoveryActivity):
        with pytest.raises(AttributeError):
            recovery_activity.recover(0)

    def test_recover_demand_not_met(self, recovery_activity: ConcreteRecoveryActivity):
        recovery_activity.set_duration({'Deterministic': {'Value': 5}})
        demand = [{'Resource': 'Resource 1', 'Amount': 5}]
        recovery_activity.set_demand(demand)
        recovery_activity.set_demand_met('Resource', 0.0)
        recovery_activity.recover(0)
        assert recovery_activity.level == 0 and recovery_activity.time_steps == []

    def test_recover_full_demand_met(self, recovery_activity: ConcreteRecoveryActivity):
        recovery_activity.set_duration({'Deterministic': {'Value': 5}})
        demand = [{'Resource': 'Resource 1', 'Amount': 5}]
        recovery_activity.set_demand(demand)
        recovery_activity.set_demand_met('Resource 1', 1.0)
        for time_step in range(3):
            recovery_activity.recover(time_step)
        assert math.isclose(recovery_activity.level, 0.6)
        assert recovery_activity.time_steps == [0, 1, 2]
        for time_step in range(3, 5):
            recovery_activity.recover(time_step)
        assert recovery_activity.level == 1.0
        assert recovery_activity.time_steps == [0, 1, 2, 3, 4]
        for time_step in range(5, 10):
            recovery_activity.recover(time_step)
        assert recovery_activity.level == 1.0
        assert recovery_activity.time_steps == [0, 1, 2, 3, 4]

    def test_recover_partial_demand_met(self, recovery_activity: ConcreteRecoveryActivity):
        recovery_activity.set_duration({'Deterministic': {'Value': 5}})
        demand = [{'Resource': 'Resource 1', 'Amount': 5}]
        recovery_activity.set_demand(demand)
        recovery_activity.set_demand_met('Resource 1', 0.5)
        for time_step in range(3):
            recovery_activity.recover(time_step)
        assert math.isclose(recovery_activity.level, 0.3)
        assert recovery_activity.time_steps == [0, 1, 2]
        for time_step in range(3, 5):
            recovery_activity.recover(time_step)
        assert math.isclose(recovery_activity.level, 0.5)
        assert recovery_activity.time_steps == [0, 1, 2, 3, 4]
        for time_step in range(5, 10):
            recovery_activity.recover(time_step)
        assert math.isclose(recovery_activity.level, 1.0)
        assert recovery_activity.time_steps == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_effect_of_unmet_demand_on_activity(self, recovery_activity: ConcreteRecoveryActivity):
        assert recovery_activity.effect_of_unmet_demand_on_activity() == 1.0
        demand = [{'Resource': 'Resource 1', 'Amount': 5}, {'Resource': 'Resource 2', 'Amount': 3}]
        recovery_activity.set_demand(demand)
        recovery_activity.set_demand_met('Resource 1', 0.5)
        recovery_activity.set_demand_met('Resource 2', 0.9)
        assert recovery_activity.effect_of_unmet_demand_on_activity() == 0.5
        recovery_activity.set_demand_met('Resource 1', 0.2)
        recovery_activity.set_demand_met('Resource 2', 0.1)
        assert recovery_activity.effect_of_unmet_demand_on_activity() == 0.1

    def test_activity_finished_false(self, recovery_activity: ConcreteRecoveryActivity):
        recovery_activity.set_duration({'Deterministic': {'Value': 5}})
        for time_step in range(4):
            recovery_activity.recover(time_step)
        assert recovery_activity.activity_finished() == False

    def test_activity_finished_true(self, recovery_activity: ConcreteRecoveryActivity):
        recovery_activity.set_duration({'Deterministic': {'Value': 5}})
        for time_step in range(5):
            recovery_activity.recover(time_step)
        assert recovery_activity.activity_finished() == True