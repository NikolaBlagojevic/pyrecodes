import pytest
import numpy as np
import math
from pyrecodes.component_configurator.tier1_interface_configurator import Tier1InterfaceConfigurator
from test_component_configurator_inputs import SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE, INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY, INTERFACE_PARAMETERS_IN_SYSTEM_CONFIGURATION
from pyrecodes.component.infrastructure_interface import InfrastructureInterface



class TestTier1InterfaceConfigurator:

    @pytest.fixture()
    def interface_configurator(self) -> Tier1InterfaceConfigurator:
        return Tier1InterfaceConfigurator(SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE)
    
    @pytest.fixture()
    def interface_component(self):
        interface_component = InfrastructureInterface()
        interface_component.construct('TestInterface', INTERFACE_PARAMETERS_IN_COMPONENT_LIBRARY)
        return interface_component
    
    def test_set_infrastructure_system_parameters(self, interface_configurator, interface_component):
        interface_configurator.set_infrastructure_system_parameters(interface_component, INTERFACE_PARAMETERS_IN_SYSTEM_CONFIGURATION)
        assert interface_component.supply['Supply']['SupplyInterfaceResource1'].initial_amount == 200
        assert interface_component.recovery_model.recovery_activities['Recovery'].duration == 50
        assert np.all([math.isclose(real_value, test_value) for real_value, test_value in zip(interface_component.recovery_model.damage_to_functionality_relation.step_limits, [0.0, 0.4, 1.0])])
        assert np.all([math.isclose(real_value, test_value) for real_value, test_value in zip(interface_component.recovery_model.damage_to_functionality_relation.step_values, [0.0, 0.5, 1.0])])
        assert interface_component.demand['OperationDemand']['DemandInterfaceResource1'].initial_amount == 5