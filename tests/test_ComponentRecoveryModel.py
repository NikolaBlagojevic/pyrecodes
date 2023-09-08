
import pytest
import math
import copy
import numpy as np
from pyrecodes import Relation
from pyrecodes import ComponentRecoveryModel
from pyrecodes import Resource

class TestComponentRecoveryActivity:

    @pytest.fixture
    def recovery_activity(self):
        return ComponentRecoveryModel.ConcreteRecoveryActivity('DummyActivity')

    def test_init(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        assert recovery_activity.name == 'DummyActivity'
        assert recovery_activity.level == 0.0
        assert recovery_activity.time_steps == []
        assert recovery_activity.demand_met == {}
        assert recovery_activity.demand == {}
        assert recovery_activity.preceding_activities_finished == False

    def test_set_name(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        assert recovery_activity.name == 'DummyActivity'
        recovery_activity.set_name('AnotherDummyActivity')
        assert recovery_activity.name == 'AnotherDummyActivity'

    def test_set_level(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        assert recovery_activity.level == 0.0
        recovery_activity.set_level(0.4)
        assert recovery_activity.level == 0.4

    def test_set_too_high_level(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        with pytest.raises(ValueError):
            recovery_activity.set_level(1.5)

    def test_set_negative_level(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        with pytest.raises(ValueError):
            recovery_activity.set_level(-1.5)

    def test_deterministic_sample_duration(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        distribution = {'Deterministic': {'Value': 5}}
        deterministic_sample = recovery_activity.sample_duration(distribution)
        assert math.isclose(deterministic_sample, 5)

    def test_lognormal_sample_duration(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        distribution = {'Lognormal': {'Median': 2, 'Dispersion': 1}}
        lognormal_samples = [recovery_activity.sample_duration(distribution) for _ in range(100000)]
        assert math.isclose(np.median(lognormal_samples), 2, abs_tol=0.05) and math.isclose(
            np.std(np.log(lognormal_samples)), 1, abs_tol=0.01)

    def test_set_deterministic_duration(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        distribution = {'Deterministic': {'Value': 5}}
        recovery_activity.set_duration(distribution)
        assert math.isclose(recovery_activity.duration, 5) and math.isclose(recovery_activity.rate, 1 / 5)

    def test_set_negative_duration(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        distribution = {'Deterministic': {'Value': -5}}
        with pytest.raises(ValueError):
            recovery_activity.set_duration(distribution)

    def test_set_empty_preceding_activities(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        preceding_activities = []
        recovery_activity.set_preceding_activities(preceding_activities)
        assert recovery_activity.preceding_activities == []

    def test_set_two_preceding_activities(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        preceding_activities = ['Activity 1', 'Acitivity 2']
        recovery_activity.set_preceding_activities(preceding_activities)
        assert recovery_activity.preceding_activities == ['Activity 1', 'Acitivity 2']

    def test_set_preceding_activities_twice(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        preceding_activities = ['Activity 1', 'Activity 2']
        recovery_activity.set_preceding_activities(preceding_activities)
        recovery_activity.set_preceding_activities(preceding_activities)
        assert recovery_activity.preceding_activities == ['Activity 1', 'Activity 2']

    def test_initial_preceding_activities_finished(self,
                                                   recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        assert recovery_activity.preceding_activities_finished == False

    def test_set_preceding_activities_finished(self,
                                               recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        recovery_activity.set_preceding_activities_finished(True)
        assert recovery_activity.preceding_activities_finished == True

    def test_set_demand(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        demand = [{'Resource': 'Resource 1', 'Amount': 5}, {'Resource': 'Resource 2', 'Amount': 3}]
        recovery_activity.set_demand(demand)
        assert all([recovery_activity.demand['Resource 1'].initial_amount == 5,
                    recovery_activity.demand['Resource 1'].current_amount == 5,
                    recovery_activity.demand['Resource 2'].initial_amount == 3,
                    recovery_activity.demand['Resource 2'].current_amount == 3])

    def test_set_demand_met(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        demand = [{'Resource': 'Resource 1', 'Amount': 5}, {'Resource': 'Resource 2', 'Amount': 3}]
        recovery_activity.set_demand(demand)
        recovery_activity.set_demand_met('Resource 1', 0.5)
        assert recovery_activity.demand_met['Resource 1'] == 0.5
        recovery_activity.set_demand_met('Resource 2', 0.9)
        assert recovery_activity.demand_met['Resource 2'] == 0.9

    def test_set_invalid_demand_met(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        demand = [{'Resource': 'Resource 1', 'Amount': 5}]
        recovery_activity.set_demand(demand)
        with pytest.raises(ValueError):
            recovery_activity.set_demand_met('Resource 1', -0.5)

    def test_get_demand(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        demand = [{'Resource': 'Resource 1', 'Amount': 5}, {'Resource': 'Resource 2', 'Amount': 3}]
        recovery_activity.set_demand(demand)
        demand = recovery_activity.get_demand()
        assert all([demand['Resource 1'].initial_amount == 5,
                    demand['Resource 1'].current_amount == 5,
                    demand['Resource 2'].initial_amount == 3,
                    demand['Resource 2'].current_amount == 3])

    def test_recover_without_set_duration(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        with pytest.raises(AttributeError):
            recovery_activity.recover(0)

    def test_recover_demand_not_met(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        recovery_activity.set_duration({'Deterministic': {'Value': 5}})
        demand = [{'Resource': 'Resource 1', 'Amount': 5}]
        recovery_activity.set_demand(demand)
        recovery_activity.set_demand_met('Resource', 0.0)
        recovery_activity.recover(0)
        assert recovery_activity.level == 0 and recovery_activity.time_steps == []

    def test_recover_full_demand_met(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
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

    def test_recover_partial_demand_met(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
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

    def test_effect_of_unmet_demand_on_activity(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        assert recovery_activity.effect_of_unmet_demand_on_activity() == 1.0
        demand = [{'Resource': 'Resource 1', 'Amount': 5}, {'Resource': 'Resource 2', 'Amount': 3}]
        recovery_activity.set_demand(demand)
        recovery_activity.set_demand_met('Resource 1', 0.5)
        recovery_activity.set_demand_met('Resource 2', 0.9)
        assert recovery_activity.effect_of_unmet_demand_on_activity() == 0.5
        recovery_activity.set_demand_met('Resource 1', 0.2)
        recovery_activity.set_demand_met('Resource 2', 0.1)
        assert recovery_activity.effect_of_unmet_demand_on_activity() == 0.1

    def test_activity_finished_false(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        recovery_activity.set_duration({'Deterministic': {'Value': 5}})
        for time_step in range(4):
            recovery_activity.recover(time_step)
        assert recovery_activity.activity_finished() == False

    def test_activity_finished_true(self, recovery_activity: ComponentRecoveryModel.ConcreteRecoveryActivity):
        recovery_activity.set_duration({'Deterministic': {'Value': 5}})
        for time_step in range(5):
            recovery_activity.recover(time_step)
        assert recovery_activity.activity_finished() == True

class TestComponentLevelRecoveryActivitiesModel_SingleActivity:

    RECOVERY_MODEL_PARAMETERS = {"Type": "ComponentLevelRecoveryActivitiesModel",
                                 "Parameters": {"Repair": {"Duration": {"Deterministic": {"Value": 10}},
                                                           "Demand": [{"Resource": "RepairCrew", "Amount": 10}], }},
                                 "DamageFunctionalityRelation": {"Type": "ReverseLinear"}}

    @pytest.fixture()
    def recovery_model(self):
        target_recovery_model = getattr(ComponentRecoveryModel,
                                        self.RECOVERY_MODEL_PARAMETERS['Type'])
        return target_recovery_model(self.RECOVERY_MODEL_PARAMETERS)
    
    def test_init(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.REPAIR_ACTIVITY_NAME == 'Repair'
        assert len(recovery_model.recovery_activities) == 1
        assert isinstance(recovery_model.recovery_activities['Repair'], ComponentRecoveryModel.ConcreteRecoveryActivity)
        assert recovery_model.recovery_activities['Repair'].name == 'Repair'
        assert recovery_model.recovery_activities['Repair'].duration == 10
        assert recovery_model.recovery_activities['Repair'].rate == 1/10
        assert isinstance(recovery_model.recovery_activities['Repair'].demand, dict)
        assert isinstance(recovery_model.recovery_activities['Repair'].demand['RepairCrew'], Resource.Resource)
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == 10
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].current_amount == 10

    def test_set_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.3
        recovery_model.set_initial_damage_level(damage_level)
        assert math.isclose(recovery_model.get_damage_level(), damage_level)

    def test_set_damage_level_error_negative(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = -0.3
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(damage_level)

    def test_set_damage_level_error_above_one(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 1.3
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(damage_level)
    
    def test_set_initial_repair_activity_state(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.recovery_activities['Repair'].level == 1.0
        recovery_model.set_initial_repair_activity_state(0.3)
        assert recovery_model.recovery_activities['Repair'].level == 0.7
        assert recovery_model.recovery_activities['Repair'].rate == 0.3/10      

    def test_set_damage_functionality(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_damage_functionality(self.RECOVERY_MODEL_PARAMETERS['DamageFunctionalityRelation'])
        damage_functionality_type = self.RECOVERY_MODEL_PARAMETERS['DamageFunctionalityRelation']['Type']
        assert isinstance(recovery_model.damage_to_functionality_relation, getattr(Relation, damage_functionality_type))

    def test_recover_once(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.6
        recovery_model.set_initial_damage_level(damage_level)
        recovery_model.recover(0)
        assert math.isclose(recovery_model.get_damage_level(),
                            0.6 - 0.6 / 10) and recovery_model.recovery_activities['Repair'].time_steps == [0]

    def test_recover_partially(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.6
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(6):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0.6 - 6 * 0.6 / 10,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(6))

    def test_recover_fully(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.6
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(10):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))

    def test_recover_fully_partial_demand_met(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.6
        partial_demand_met = 0.1
        recovery_model.set_initial_damage_level(damage_level)
        recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] = partial_demand_met
        for time_step in range(100):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(100))

    def test_recover_partially_partial_demand_met(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.6
        partial_demand_met = 0.1
        recovery_model.set_initial_damage_level(damage_level)
        recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] = partial_demand_met
        for time_step in range(10):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0.6 * 0.9,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))

    def test_recover_fully_full_damage(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 1.0
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(10):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))

    def test_overrecover(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.6
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(20):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))

    def test_check_preceding_activities(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.check_preceding_activities()
        assert recovery_model.recovery_activities['Repair'].preceding_activities_finished == True

    def test_preceding_activities_finished(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.preceding_activities_finished(recovery_model.recovery_activities['Repair']) == True

    def test_get_functionality_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.4
        recovery_model.set_initial_damage_level(damage_level)
        assert math.isclose(recovery_model.get_functionality_level(), 0.6)

    def test_get_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 0.4
        recovery_model.set_initial_damage_level(damage_level)
        assert math.isclose(recovery_model.get_damage_level(), 0.4)
        
    def test_get_demand_no_damage(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        demand = recovery_model.get_demand()
        assert demand == {}
    
    def test_get_demand_with_damage(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_initial_damage_level(0.1)
        demand = recovery_model.get_demand()
        assert demand['RepairCrew'].current_amount == 10 and demand['RepairCrew'].initial_amount == 10

    def test_set_activities_demand_to_met(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_activities_demand_to_met()
        assert recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] == 1.0
    
    def test_set_met_demand_for_recovery_activities(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_met_demand_for_recovery_activities('RepairCrew', 0.5)
        assert recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] == 0.5

    def test_set_wrong_unmet_demand_for_recovery_activities(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        with pytest.raises(ValueError):
            recovery_model.set_met_demand_for_recovery_activities('Inspectors', 0.5)
    
    def test_find_recovery_activity_that_demands_the_resource(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_activity = recovery_model.find_recovery_activity_that_demands_the_resource('RepairCrew')
        assert recovery_activity.name == 'Repair'
        with pytest.raises(ValueError):
            recovery_model.find_recovery_activity_that_demands_the_resource('SomeResource')

class TestComponentLevelRecoveryActivitiesModel_MultipleActivities:
    RECOVERY_MODEL_PARAMETERS = {"Type": "ComponentLevelRecoveryActivitiesModel",
                                 "Parameters": {
                                     "RapidInspection": {
                                         "Duration": {"Lognormal": {"Median": 1, "Dispersion": 0.0}},
                                         "Demand": [{"Resource": "FirstResponderEngineer", "Amount": 0.1}],
                                         "PrecedingActivities": []
                                     },
                                     "ContractorMobilization": {
                                         "Duration": {"Lognormal": {"Median": 1, "Dispersion": 0.0}},
                                         "Demand": [{"Resource": "Contractor", "Amount": 1}],
                                         "PrecedingActivities": ["RapidInspection"]
                                     },
                                     "Repair": {
                                         "Duration": {"Lognormal": {"Median": 10, "Dispersion": 0.0}},
                                         "Demand": [{"Resource": "RepairCrew", "Amount": 10}],
                                         "PrecedingActivities": ["RapidInspection", "ContractorMobilization"]
                                     }
                                 },
                                 "DamageFunctionalityRelation": {
                                     "Type": "ReverseLinear"
                                 }
                                 }

    @pytest.fixture
    def recovery_model(self):
        target_recovery_model = getattr(ComponentRecoveryModel, self.RECOVERY_MODEL_PARAMETERS['Type'])
        return target_recovery_model(self.RECOVERY_MODEL_PARAMETERS)

    def test_set_init(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.REPAIR_ACTIVITY_NAME == 'Repair'
        assert len(recovery_model.recovery_activities) == 3
        assert isinstance(recovery_model.recovery_activities['RapidInspection'], ComponentRecoveryModel.ConcreteRecoveryActivity)
        assert isinstance(recovery_model.recovery_activities['ContractorMobilization'], ComponentRecoveryModel.ConcreteRecoveryActivity)
        assert isinstance(recovery_model.recovery_activities['Repair'], ComponentRecoveryModel.ConcreteRecoveryActivity)
        assert recovery_model.recovery_activities['RapidInspection'].name == 'RapidInspection'
        assert recovery_model.recovery_activities['RapidInspection'].duration == 1
        assert recovery_model.recovery_activities['RapidInspection'].rate == 1
        assert recovery_model.recovery_activities['ContractorMobilization'].name == 'ContractorMobilization'
        assert recovery_model.recovery_activities['ContractorMobilization'].duration == 1
        assert recovery_model.recovery_activities['ContractorMobilization'].rate == 1
        assert recovery_model.recovery_activities['Repair'].name == 'Repair'
        assert math.isclose(recovery_model.recovery_activities['Repair'].duration, 10)
        assert math.isclose(recovery_model.recovery_activities['Repair'].rate, 1/10)
        assert isinstance(recovery_model.recovery_activities['RapidInspection'].demand, dict)
        assert len(recovery_model.recovery_activities['RapidInspection'].demand) == 1
        assert isinstance(recovery_model.recovery_activities['RapidInspection'].demand['FirstResponderEngineer'], Resource.Resource)
        assert recovery_model.recovery_activities['RapidInspection'].demand['FirstResponderEngineer'].initial_amount == 0.1
        assert recovery_model.recovery_activities['RapidInspection'].demand['FirstResponderEngineer'].current_amount == 0.1
        assert isinstance(recovery_model.recovery_activities['ContractorMobilization'].demand, dict)
        assert isinstance(recovery_model.recovery_activities['ContractorMobilization'].demand['Contractor'], Resource.Resource)
        assert recovery_model.recovery_activities['ContractorMobilization'].demand['Contractor'].initial_amount == 1
        assert recovery_model.recovery_activities['ContractorMobilization'].demand['Contractor'].current_amount == 1
        assert len(recovery_model.recovery_activities['ContractorMobilization'].demand) == 1
        assert isinstance(recovery_model.recovery_activities['Repair'].demand, dict)
        assert isinstance(recovery_model.recovery_activities['Repair'].demand['RepairCrew'], Resource.Resource)
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == 10
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].current_amount == 10
        assert len(recovery_model.recovery_activities['Repair'].demand) == 1

    def test_set_initial_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        damage_level = 1.0
        recovery_model.set_parameters(self.RECOVERY_MODEL_PARAMETERS['Parameters'])
        recovery_model.set_initial_damage_level(damage_level)
        for recovery_activity_name, recovery_activity in recovery_model.recovery_activities.items():
            if recovery_activity_name == recovery_model.REPAIR_ACTIVITY_NAME:
                assert recovery_activity.level == 1 - damage_level
            else:
                assert recovery_activity.level == 0.0

    def test_set_wrong_initial_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(1.5)

    def test_check_preceding_activities(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.check_preceding_activities()
        target_bools = [True, True, True]
        for target_bool, recovery_activity in zip(target_bools, recovery_model.recovery_activities.values()):
            assert recovery_activity.preceding_activities_finished == target_bool

        recovery_model.set_initial_damage_level(0.5)
        recovery_model.check_preceding_activities()
        target_bools = [True, False, False]
        for target_bool, recovery_activity in zip(target_bools, recovery_model.recovery_activities.values()):
            assert recovery_activity.preceding_activities_finished == target_bool

        recovery_model.recovery_activities['RapidInspection'].level = 1.0
        recovery_model.check_preceding_activities()
        target_bools = [True, True, False]
        for target_bool, recovery_activity in zip(target_bools, recovery_model.recovery_activities.values()):
            assert recovery_activity.preceding_activities_finished == target_bool
    
    def test_preceding_activities_finished(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        for recovery_activity in recovery_model.recovery_activities.values():
            assert recovery_model.preceding_activities_finished(recovery_activity) == True

        recovery_model.set_initial_damage_level(1.0)
        target_bools = [True, False, False]
        for target_bool, recovery_activity in zip(target_bools, recovery_model.recovery_activities.values()):
            assert recovery_model.preceding_activities_finished(recovery_activity) == target_bool

        recovery_model.recovery_activities['RapidInspection'].level = 1.0
        target_bools = [True, True, False]
        for target_bool, recovery_activity in zip(target_bools, recovery_model.recovery_activities.values()):
            assert recovery_model.preceding_activities_finished(recovery_activity) == target_bool
    
    def test_get_functionality_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.get_functionality_level() == 1.0
        recovery_model.set_initial_damage_level(1.0)
        assert recovery_model.get_functionality_level() == 0.0
        recovery_model.set_initial_damage_level(0.6)
        assert recovery_model.get_functionality_level() == 0.4

    def test_get_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.get_damage_level() == 0.0
        recovery_model.set_initial_damage_level(1.0)
        assert recovery_model.get_damage_level() == 1.0
        recovery_model.set_initial_damage_level(0.6)
        assert recovery_model.get_damage_level() == 0.6   

    def test_get_demand(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.get_demand() == {}

        recovery_model.set_initial_damage_level(0.1)
        current_demand = recovery_model.get_demand()
        assert len(current_demand) == 1
        assert current_demand['FirstResponderEngineer'].initial_amount == 0.1
        assert current_demand['FirstResponderEngineer'].current_amount == 0.1

        recovery_model.recovery_activities['RapidInspection'].level = 1.0
        current_demand = recovery_model.get_demand()
        assert len(current_demand) == 1
        assert current_demand['Contractor'].initial_amount == 1
        assert current_demand['Contractor'].current_amount == 1

        recovery_model.recovery_activities['ContractorMobilization'].level = 1.0
        current_demand = recovery_model.get_demand()
        assert len(current_demand) == 1
        assert current_demand['RepairCrew'].initial_amount == 10
        assert current_demand['RepairCrew'].current_amount == 10

        recovery_model.recovery_activities['Repair'].level = 1.0
        assert recovery_model.get_demand() == {}

    def test_set_activities_demand_to_met(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert all([list(recovery_activity.demand_met.values())[0] == 1.0 for recovery_activity in
                              recovery_model.recovery_activities.values()])
        recovery_model.recovery_activities['RapidInspection'].demand_met['FirstResponderEngineer'] = 0.3
        recovery_model.set_activities_demand_to_met()
        assert all([list(recovery_activity.demand_met.values())[0] == 1.0 for recovery_activity in
                              recovery_model.recovery_activities.values()])

    def test_set_met_demand_for_recovery_activities(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert all([list(recovery_activity.demand_met.values())[0] == 1.0 for recovery_activity in
                              recovery_model.recovery_activities.values()])
        recovery_model.set_met_demand_for_recovery_activities('FirstResponderEngineer', 0.5)
        assert recovery_model.recovery_activities['RapidInspection'].demand_met['FirstResponderEngineer'] == 0.5
        assert recovery_model.recovery_activities['ContractorMobilization'].demand_met['Contractor'] == 1.0
        assert recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] == 1.0
        recovery_model.set_met_demand_for_recovery_activities('Contractor', 0.6)
        assert recovery_model.recovery_activities['ContractorMobilization'].demand_met['Contractor'] == 0.6
        recovery_model.set_met_demand_for_recovery_activities('RepairCrew', 0.4)
        assert recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] == 0.4

    def test_find_recovery_activity_that_demands_the_resource(self,
                                                              recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_activity = recovery_model.find_recovery_activity_that_demands_the_resource('Contractor')
        assert recovery_activity.name == 'ContractorMobilization'
        recovery_activity = recovery_model.find_recovery_activity_that_demands_the_resource('RepairCrew')
        assert recovery_activity.name == 'Repair'

    def test_recover_no_damage(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        for time_step in range(10):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == []
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == []
        assert recovery_model.recovery_activities['Repair'].time_steps == []
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert recovery_model.recovery_activities['Repair'].level == 1.0

    def test_recover_once(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_initial_damage_level(0.01)
        recovery_model.recover(time_step=1)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [1]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == []
        assert recovery_model.recovery_activities['Repair'].time_steps == []
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 0.0
        assert recovery_model.recovery_activities['Repair'].level == 0.99

    def test_recover_partially(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_initial_damage_level(1.0)
        for time_step in range(5):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1]
        assert recovery_model.recovery_activities['Repair'].time_steps == [2, 3, 4]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 0.3)

    def test_recover_full(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_initial_damage_level(1.0)
        for time_step in range(12):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1]
        assert recovery_model.recovery_activities['Repair'].time_steps == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 1.0)

    def test_recover_partial_demand_met(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_initial_damage_level(1.0)
        recovery_model.recovery_activities['ContractorMobilization'].demand_met['Contractor'] = 0.5
        for time_step in range(13):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1, 2]
        assert recovery_model.recovery_activities['Repair'].time_steps == [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 1.0)

class TestNoRecoveryActivityComponentRecoveryModel:

    RECOVERY_MODEL_PARAMETERS = {"Type": "NoRecoveryActivityModel",
                                 "Parameters": {},
                                 "DamageFunctionalityRelation": {
                                     "Type": "Constant"
                                 }
                                 }

    @pytest.fixture()
    def recovery_model(self):
        return ComponentRecoveryModel.NoRecoveryActivityModel(self.RECOVERY_MODEL_PARAMETERS)  
    
    def test_init(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert len(recovery_model.recovery_activities) == 0        

    def test_set_initial_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_initial_damage_level(0.0)
        assert recovery_model.get_damage_level() == 0.0

    def test_set_nonzero_initial_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(0.5)

    def test_get_functionality_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.get_functionality_level() == 1.0

    def test_get_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.get_damage_level() == 0.0

    def test_get_demand(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert recovery_model.get_demand() == {}

class TestInfrastructureInterfaceRecoveryModel:

    RECOVERY_MODEL_PARAMETERS = {"Type": "InfrastructureInterfaceRecoveryModel",
                                "Parameters": {},
                                "DamageFunctionalityRelation": ""}
    
    STEP_DICT = {'StepLimits': [0.2, 0.4, 1.0],
                 'StepValues': [0.1, 0.6, 1.0],
                 'RestoredIn': [{'Deterministic': {'Value': 10}},
                                {'Deterministic': {'Value': 20}},
                                {'Deterministic': {'Value': 50}}]}

    @pytest.fixture()
    def recovery_model(self):
        return ComponentRecoveryModel.InfrastructureInterfaceRecoveryModel(self.RECOVERY_MODEL_PARAMETERS)
    
    def test_init(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        assert len(recovery_model.recovery_activities) == 1
        assert recovery_model.recovery_activities['Recovery'].time_steps == []
        assert recovery_model.recovery_activities['Recovery'].level == 1.0
        assert recovery_model.recovery_activities['Recovery'].duration == 0.0
        assert recovery_model.recovery_activities['Recovery'].rate == math.inf
        assert isinstance(recovery_model.damage_to_functionality_relation, Relation.MultipleStep)

    def test_set_initial_damage_level(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_initial_damage_level(0.0)
        assert recovery_model.get_damage_level() == 1.0
        assert recovery_model.recovery_activities['Recovery'].level == 0.0
    
    def test_set_parameters(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_parameters(self.STEP_DICT)
        assert recovery_model.damage_to_functionality_relation.step_limits == self.STEP_DICT['StepLimits']
        assert recovery_model.damage_to_functionality_relation.step_values == self.STEP_DICT['StepValues']
        assert recovery_model.recovery_activities['Recovery'].duration == 50
        assert math.isclose(recovery_model.recovery_activities['Recovery'].rate, 1/50)
    
    def test_recover_no_steps_defined(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.recover(0)
        assert recovery_model.recovery_activities['Recovery'].time_steps == []
        assert recovery_model.recovery_activities['Recovery'].level == 1.0
        recovery_model.set_initial_damage_level(1.0)
        recovery_model.recover(1)
        recovery_model.recover(2)
        assert recovery_model.recovery_activities['Recovery'].time_steps == [1]
    
    def test_recover_steps_defined(self, recovery_model: ComponentRecoveryModel.RecoveryModel):
        recovery_model.set_parameters(self.STEP_DICT)
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


