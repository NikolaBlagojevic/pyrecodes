import pytest
from pyrecodes.component.r2d_component import R2DPipe, R2DComponent
from test_component_inputs import COMPONENT_NAME, COMPONENT_PARAMETERS

class TestR2DComponent:

    @pytest.fixture
    def r2d_component(self):
        return R2DComponent()
    
    def test_update_r2d_dict(self, r2d_component):
        r2d_component.general_information = {}
        r2d_component.general_information['OperationDemand'] = {}
        r2d_component.general_information['RecoveryDemand'] = {}
        r2d_component.update_r2d_dict()
        assert r2d_component.general_information['OperationDemand'] == {}
        assert r2d_component.general_information['RecoveryDemand'] == {}  

        r2d_component.construct(COMPONENT_NAME, COMPONENT_PARAMETERS)
        r2d_component.update_r2d_dict()
        assert r2d_component.general_information['OperationDemand'] == {'DemandResource1': 1, 'DemandResource2': 5}
        assert r2d_component.general_information['RecoveryDemand'] == {} 

        DUMMY_RESOURCE_DICT = {"DemandResource3": {"Amount": 100,
                                                "FunctionalityToAmountRelation": "Linear",
                                                "UnmetDemandToAmountRelation": "Constant"
                                                                }}
        r2d_component.add_resources('demand', 'RecoveryDemand', DUMMY_RESOURCE_DICT)
        r2d_component.update_r2d_dict()
        assert r2d_component.general_information['OperationDemand'] == {'DemandResource1': 1, 'DemandResource2': 5}
        assert r2d_component.general_information['RecoveryDemand'] == {'DemandResource3': 100}

        r2d_component.demand['OperationDemand']['DemandResource1'].current_amount = 0
        r2d_component.update_r2d_dict()
        assert r2d_component.general_information['OperationDemand'] == {'DemandResource1': 0, 'DemandResource2': 5}
        assert r2d_component.general_information['RecoveryDemand'] == {'DemandResource3': 100}
          
class TestR2DPipe:

    @pytest.fixture
    def r2d_pipe(self):
        return R2DPipe()
    
    def test_init(self, r2d_pipe):
        assert r2d_pipe.damage_information == {'Location': [], 'Type': []}

    def test_update_r2d_dict(self, r2d_pipe):
        r2d_pipe.general_information['Status'] = 'OPEN'        
        r2d_pipe.update_r2d_dict()
        assert r2d_pipe.damage_information == {'Location': [], 'Type': []}
        assert r2d_pipe.general_information['Status'] == 'OPEN'

        r2d_pipe.functionality_level = 0.0
        r2d_pipe.update_r2d_dict()
        assert r2d_pipe.general_information['Status'] == 'CLOSED'

        r2d_pipe.functionality_level = 1.0
        r2d_pipe.update_r2d_dict()
        assert r2d_pipe.general_information['Status'] == 'OPEN'
        assert r2d_pipe.damage_information == {'Location': [], 'Type': []}
        
