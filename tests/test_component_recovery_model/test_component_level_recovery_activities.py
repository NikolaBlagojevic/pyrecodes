import pytest
import math
from test_component_recovery_model_inputs import RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY, RECOVERY_MODEL_PARAMETERS_MULTIPLE_ACTIVITIES, RECOVERY_TIME_STEPS_DENSE, RECOVERY_TIME_STEPS_SPARSE
from pyrecodes.component_recovery_model.component_level_recovery_activities_model import ComponentLevelRecoveryActivitiesModel
from pyrecodes.component_recovery_model.abstract_recovery_model import AbstractRecoveryModel
from pyrecodes.component_recovery_model.concrete_recovery_activity import ConcreteRecoveryActivity
from pyrecodes.resource.resource import Resource
from pyrecodes.relation import relation

class TestComponentLevelRecoveryActivitiesModel_SingleActivity:    

    @pytest.fixture()
    def recovery_model(self):
        return ComponentLevelRecoveryActivitiesModel(RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY)
    
    def test_init(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.REPAIR_ACTIVITY_NAME == 'Repair'
        assert len(recovery_model.recovery_activities) == 1
        assert isinstance(recovery_model.recovery_activities['Repair'], ConcreteRecoveryActivity)
        assert recovery_model.recovery_activities['Repair'].name == 'Repair'
        assert recovery_model.recovery_activities['Repair'].duration == 10
        assert recovery_model.recovery_activities['Repair'].rate == 1/10
        assert isinstance(recovery_model.recovery_activities['Repair'].demand, dict)
        assert isinstance(recovery_model.recovery_activities['Repair'].demand['RepairCrew'], Resource)
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == 10
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].current_amount == 10

    def test_set_parameters(self, recovery_model: AbstractRecoveryModel):
        parameters = {"Repair": {"Duration": {"Deterministic": {"Value": 5}},
                                 "Demand": [{"Resource": "RepairCrew", "Amount": 5}]}
                      }
        recovery_model.set_parameters(parameters)
        assert recovery_model.recovery_activities['Repair'].duration == 5
        assert recovery_model.recovery_activities['Repair'].rate == 1/5
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == 5
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].current_amount == 5

    def test_set_damage_level(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.3
        recovery_model.set_initial_damage_level(damage_level)
        assert math.isclose(recovery_model.get_damage_level(), damage_level)

    def test_set_damage_level_error_negative(self, recovery_model: AbstractRecoveryModel):
        damage_level = -0.3
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(damage_level)

    def test_set_damage_level_error_above_one(self, recovery_model: AbstractRecoveryModel):
        damage_level = 1.3
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(damage_level)
    
    def test_set_initial_repair_activity_state(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.recovery_activities['Repair'].level == 1.0
        recovery_model.set_initial_repair_activity_state(0.3)
        assert recovery_model.recovery_activities['Repair'].level == 0.7
        assert recovery_model.recovery_activities['Repair'].rate == 0.3/10      

    def test_set_damage_functionality(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_damage_functionality(RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY['DamageFunctionalityRelation'])
        damage_functionality_type = RECOVERY_MODEL_PARAMETERS_SINGLE_ACTIVITY['DamageFunctionalityRelation']['Type']
        assert isinstance(recovery_model.damage_to_functionality_relation, getattr(relation, damage_functionality_type))

    def test_recover_once(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        recovery_model.set_initial_damage_level(damage_level)
        recovery_model.recover(0)
        assert math.isclose(recovery_model.get_damage_level(),
                            0.6 - 0.6 / 10) and recovery_model.recovery_activities['Repair'].time_steps == [0]

    def test_recover_partially(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(6):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0.6 - 6 * 0.6 / 10,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(6))

    def test_recover_fully(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(10):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))

    def test_recover_fully_partial_demand_met(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        partial_demand_met = 0.1
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        recovery_model.set_initial_damage_level(damage_level)
        recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] = partial_demand_met
        for time_step in range(100):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(100))

    def test_recover_partially_partial_demand_met(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        partial_demand_met = 0.1
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        recovery_model.set_initial_damage_level(damage_level)
        recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] = partial_demand_met
        for time_step in range(10):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0.6 * 0.9,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))

    def test_recover_fully_full_damage(self, recovery_model: AbstractRecoveryModel):
        damage_level = 1.0
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(10):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))

    def test_overrecover(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(20):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))
        
    def test_recover_once_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(damage_level)
        recovery_model.recover(0)
        assert math.isclose(recovery_model.get_damage_level(),
                            0.6 - 0.6 / 10) and recovery_model.recovery_activities['Repair'].time_steps == [0]
        
        recovery_model.recover(1)
        assert math.isclose(recovery_model.get_damage_level(),
                            0.6 - 0.6 / 10) and recovery_model.recovery_activities['Repair'].time_steps == [0]
        
        recovery_model.recover(2)
        assert math.isclose(recovery_model.get_damage_level(),
                            0.6 - 0.6 / 10) and recovery_model.recovery_activities['Repair'].time_steps == [0]
        
        recovery_model.recover(5)
        assert math.isclose(recovery_model.get_damage_level(),
                            0.6 - 6 * 0.6 / 10) and recovery_model.recovery_activities['Repair'].time_steps == [0, 1, 2, 3, 4, 5]
        
    def test_recover_partially_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(8):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0.6 - 6 * 0.6 / 10,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(6))
        
    def test_recover_fully_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(11):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))
        
    def test_recover_partially_partial_demand_met_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.6
        partial_demand_met = 0.1
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(damage_level)
        recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] = partial_demand_met
        for time_step in range(9):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0.6-0.006*6,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(6))
        
    def test_recover_fully_full_damage_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        damage_level = 1.0
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(damage_level)
        for time_step in range(11):
            recovery_model.recover(time_step)
        assert math.isclose(recovery_model.get_damage_level(), 0,
                            abs_tol=1e-10) and recovery_model.recovery_activities['Repair'].time_steps == list(range(10))

    def test_check_preceding_activities(self, recovery_model: AbstractRecoveryModel):
        recovery_model.check_preceding_activities()
        assert recovery_model.recovery_activities['Repair'].preceding_activities_finished == True

    def test_preceding_activities_finished(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.preceding_activities_finished(recovery_model.recovery_activities['Repair']) == True

    def test_get_functionality_level(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.4
        recovery_model.set_initial_damage_level(damage_level)
        assert math.isclose(recovery_model.get_functionality_level(), 0.6)

    def test_get_damage_level(self, recovery_model: AbstractRecoveryModel):
        damage_level = 0.4
        recovery_model.set_initial_damage_level(damage_level)
        assert math.isclose(recovery_model.get_damage_level(), 0.4)
        
    def test_get_demand_no_damage(self, recovery_model: AbstractRecoveryModel):
        demand = recovery_model.get_demand()
        assert demand == {}
    
    def test_get_demand_with_damage(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_initial_damage_level(0.1)
        demand = recovery_model.get_demand()
        assert demand['RepairCrew'].current_amount == 10 and demand['RepairCrew'].initial_amount == 10

    def test_set_activities_demand_to_met(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_activities_demand_to_met()
        assert recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] == 1.0
    
    def test_set_met_demand_for_recovery_activities(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_met_demand_for_recovery_activities('RepairCrew', 0.5)
        assert recovery_model.recovery_activities['Repair'].demand_met['RepairCrew'] == 0.5

    def test_set_wrong_unmet_demand_for_recovery_activities(self, recovery_model: AbstractRecoveryModel):
        with pytest.raises(ValueError):
            recovery_model.set_met_demand_for_recovery_activities('Inspectors', 0.5)
    
    def test_find_recovery_activity_that_demands_the_resource(self, recovery_model: AbstractRecoveryModel):
        recovery_activity = recovery_model.find_recovery_activity_that_demands_the_resource('RepairCrew')
        assert recovery_activity.name == 'Repair'
        with pytest.raises(ValueError):
            recovery_model.find_recovery_activity_that_demands_the_resource('SomeResource')

class TestComponentLevelRecoveryActivitiesModel_MultipleActivities:
    
    @pytest.fixture
    def recovery_model(self):
        recovery_model = ComponentLevelRecoveryActivitiesModel(RECOVERY_MODEL_PARAMETERS_MULTIPLE_ACTIVITIES)
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_DENSE)
        return recovery_model

    def test_set_init(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.REPAIR_ACTIVITY_NAME == 'Repair'
        assert len(recovery_model.recovery_activities) == 3
        assert isinstance(recovery_model.recovery_activities['RapidInspection'], ConcreteRecoveryActivity)
        assert isinstance(recovery_model.recovery_activities['ContractorMobilization'], ConcreteRecoveryActivity)
        assert isinstance(recovery_model.recovery_activities['Repair'], ConcreteRecoveryActivity)
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
        assert isinstance(recovery_model.recovery_activities['RapidInspection'].demand['FirstResponderEngineer'], Resource)
        assert recovery_model.recovery_activities['RapidInspection'].demand['FirstResponderEngineer'].initial_amount == 0.1
        assert recovery_model.recovery_activities['RapidInspection'].demand['FirstResponderEngineer'].current_amount == 0.1
        assert isinstance(recovery_model.recovery_activities['ContractorMobilization'].demand, dict)
        assert isinstance(recovery_model.recovery_activities['ContractorMobilization'].demand['Contractor'], Resource)
        assert recovery_model.recovery_activities['ContractorMobilization'].demand['Contractor'].initial_amount == 1
        assert recovery_model.recovery_activities['ContractorMobilization'].demand['Contractor'].current_amount == 1
        assert len(recovery_model.recovery_activities['ContractorMobilization'].demand) == 1
        assert isinstance(recovery_model.recovery_activities['Repair'].demand, dict)
        assert isinstance(recovery_model.recovery_activities['Repair'].demand['RepairCrew'], Resource)
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == 10
        assert recovery_model.recovery_activities['Repair'].demand['RepairCrew'].current_amount == 10
        assert len(recovery_model.recovery_activities['Repair'].demand) == 1

    def test_set_parameters(self, recovery_model: AbstractRecoveryModel):
        # Tested with init
        pass

    def test_set_initial_damage_level(self, recovery_model: AbstractRecoveryModel):
        damage_level = 1.0
        recovery_model.set_initial_damage_level(damage_level)
        for recovery_activity_name, recovery_activity in recovery_model.recovery_activities.items():
            if recovery_activity_name == recovery_model.REPAIR_ACTIVITY_NAME:
                assert recovery_activity.level == 1 - damage_level
            else:
                assert recovery_activity.level == 0.0

    def test_set_wrong_initial_damage_level(self, recovery_model: AbstractRecoveryModel):
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(1.5)

        damage_level = - 0.2
        with pytest.raises(ValueError):
            recovery_model.set_initial_damage_level(damage_level)

    def test_set_initial_repair_acitvity_state(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_initial_repair_activity_state(0.3)
        assert recovery_model.recovery_activities['Repair'].level == 0.7
        assert math.isclose(recovery_model.recovery_activities['Repair'].rate, 0.3/10)

        recovery_model.set_initial_repair_activity_state(0.5)
        assert recovery_model.recovery_activities['Repair'].level == 0.5
        assert math.isclose(recovery_model.recovery_activities['Repair'].rate, 0.5/10)

    def test_check_preceding_activities(self, recovery_model: AbstractRecoveryModel):
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
    
    def test_preceding_activities_finished(self, recovery_model: AbstractRecoveryModel):
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
    
    def test_get_functionality_level(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.get_functionality_level() == 1.0
        recovery_model.set_initial_damage_level(1.0)
        assert recovery_model.get_functionality_level() == 0.0
        recovery_model.set_initial_damage_level(0.6)
        assert recovery_model.get_functionality_level() == 0.4

    def test_get_damage_level(self, recovery_model: AbstractRecoveryModel):
        assert recovery_model.get_damage_level() == 0.0
        recovery_model.set_initial_damage_level(1.0)
        assert recovery_model.get_damage_level() == 1.0
        recovery_model.set_initial_damage_level(0.6)
        assert recovery_model.get_damage_level() == 0.6   

    def test_get_demand(self, recovery_model: AbstractRecoveryModel):
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

    def test_set_activities_demand_to_met(self, recovery_model: AbstractRecoveryModel):
        assert all([list(recovery_activity.demand_met.values())[0] == 1.0 for recovery_activity in
                              recovery_model.recovery_activities.values()])
        recovery_model.recovery_activities['RapidInspection'].demand_met['FirstResponderEngineer'] = 0.3
        recovery_model.set_activities_demand_to_met()
        assert all([list(recovery_activity.demand_met.values())[0] == 1.0 for recovery_activity in
                              recovery_model.recovery_activities.values()])

    def test_set_met_demand_for_recovery_activities(self, recovery_model: AbstractRecoveryModel):
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
                                                              recovery_model: AbstractRecoveryModel):
        recovery_activity = recovery_model.find_recovery_activity_that_demands_the_resource('Contractor')
        assert recovery_activity.name == 'ContractorMobilization'
        recovery_activity = recovery_model.find_recovery_activity_that_demands_the_resource('RepairCrew')
        assert recovery_activity.name == 'Repair'

    def test_recover_no_damage(self, recovery_model: AbstractRecoveryModel):
        for time_step in range(10):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == []
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == []
        assert recovery_model.recovery_activities['Repair'].time_steps == []
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert recovery_model.recovery_activities['Repair'].level == 1.0

    def test_recover_once_dense_time_steps(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_initial_damage_level(0.01)
        recovery_model.recover(time_step=1)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [1]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == []
        assert recovery_model.recovery_activities['Repair'].time_steps == []
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 0.0
        assert recovery_model.recovery_activities['Repair'].level == 0.99

    def test_recover_once_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(0.01)
        recovery_model.recover(time_step=1)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == []
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == []
        assert recovery_model.recovery_activities['Repair'].time_steps == []
        assert recovery_model.recovery_activities['RapidInspection'].level == 0.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 0.0
        assert recovery_model.recovery_activities['Repair'].level == 0.99

        recovery_model.recover(time_step=0)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == []
        assert recovery_model.recovery_activities['Repair'].time_steps == []
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 0.0
        assert recovery_model.recovery_activities['Repair'].level == 0.99

    def test_recover_partially_dense_time_steps(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_initial_damage_level(1.0)
        for time_step in range(5):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1]
        assert recovery_model.recovery_activities['Repair'].time_steps == [2, 3, 4]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 0.3)

    def test_recover_partially_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(1.0)
        for time_step in range(5):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == []
        assert recovery_model.recovery_activities['Repair'].time_steps == []
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 0.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 0.0)

        recovery_model.recover(5)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1]
        assert recovery_model.recovery_activities['Repair'].time_steps == [2, 3, 4, 5]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 0.4)

    def test_recover_full_dense_time_steps(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_initial_damage_level(1.0)
        for time_step in range(12):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1]
        assert recovery_model.recovery_activities['Repair'].time_steps == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 1.0)

    def test_recover_full_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(1.0)
        for time_step in range(12):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1]
        assert recovery_model.recovery_activities['Repair'].time_steps == [2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 0.9)

        for time_step in range(12, 16):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1]
        assert recovery_model.recovery_activities['Repair'].time_steps == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 1.0)

    def test_recover_partial_demand_met_dense_time_steps(self, recovery_model: AbstractRecoveryModel):
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

    def test_recover_partial_demand_met_sparse_time_steps(self, recovery_model: AbstractRecoveryModel):
        recovery_model.set_recovery_time_steps(RECOVERY_TIME_STEPS_SPARSE)
        recovery_model.set_initial_damage_level(1.0)
        recovery_model.recovery_activities['ContractorMobilization'].demand_met['Contractor'] = 0.5
        for time_step in range(3):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == []
        assert recovery_model.recovery_activities['Repair'].time_steps == []
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 0.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 0.0)

        for time_step in range(3, 13):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1, 2]
        assert recovery_model.recovery_activities['Repair'].time_steps == [3, 4, 5, 6, 7, 8, 9, 10]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 0.8)

        for time_step in range(13, 16):
            recovery_model.recover(time_step)
        assert recovery_model.recovery_activities['RapidInspection'].time_steps == [0]
        assert recovery_model.recovery_activities['ContractorMobilization'].time_steps == [1, 2]
        assert recovery_model.recovery_activities['Repair'].time_steps == [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        assert recovery_model.recovery_activities['RapidInspection'].level == 1.0
        assert recovery_model.recovery_activities['ContractorMobilization'].level == 1.0
        assert math.isclose(recovery_model.recovery_activities['Repair'].level, 1.0)