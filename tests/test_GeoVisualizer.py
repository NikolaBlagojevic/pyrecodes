import pytest
import pandas as pd
from pyrecodes import SystemCreator
from pyrecodes import ComponentLibraryCreator
from pyrecodes import System
from pyrecodes import GeoVisualizer
from pyrecodes import Plotter
from pyrecodes import main

class TestConcreteGeoVisualizer:

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        system = main.create_system(input_dict)
        return system
    
    @pytest.fixture
    def geo_visualizer(self, system: System.System):
        return GeoVisualizer.ConcreteGeoVisualizer(system.components)
    
    def test_init(self, geo_visualizer: GeoVisualizer.ConcreteGeoVisualizer, system: System.System):
        assert geo_visualizer.components == system.components
        assert isinstance(geo_visualizer.buildings_geodataframe, pd.DataFrame)
        assert isinstance(geo_visualizer.state_dict, dict)
        assert isinstance(geo_visualizer.plotter, Plotter.Plotter)        

    def test_set_component_state_dict(self, geo_visualizer: GeoVisualizer.ConcreteGeoVisualizer):
        assert geo_visualizer.state_dict['Waiting'] == {'Color': 'black', 'ID': 0}
        assert geo_visualizer.state_dict['CleanUp'] == {'Color': 'yellow', 'ID': 5}
        assert geo_visualizer.state_dict['Functional'] == {'Color': 'green', 'ID': 11}

    def test_get_component_current_state(self, geo_visualizer, system):
        system.components[1].functional = [0, 20, 21, 22, 23, 24, 25]
        system.components[1].recovery_model.recovery_activities['RapidInspection'].time_steps = [1]
        system.components[1].recovery_model.recovery_activities['CleanUp'].time_steps = [2, 3, 4]
        system.components[1].recovery_model.recovery_activities['Permitting'].time_steps = [4, 5, 6]
        system.components[1].recovery_model.recovery_activities['Repair'].time_steps = list(range(15, 20))
        assert geo_visualizer.get_component_current_state(system.components[1], 0) == ['Functional']
        assert geo_visualizer.get_component_current_state(system.components[1], 20) == ['Functional']
        assert geo_visualizer.get_component_current_state(system.components[1], 19) == ['Repair']
        assert geo_visualizer.get_component_current_state(system.components[1], 1) == ['RapidInspection']
        assert geo_visualizer.get_component_current_state(system.components[1], 2) == ['CleanUp']
        assert geo_visualizer.get_component_current_state(system.components[1], 4) == ['CleanUp', 'Permitting']
        assert geo_visualizer.get_component_current_state(system.components[1], 10) == ['Waiting']

    def test_component_is_in_state(self, geo_visualizer, system: System.System):
        system.components[1].functional = [0, 20, 21, 22, 23, 24, 25]
        system.components[1].recovery_model.recovery_activities['RapidInspection'].time_steps = [1]
        system.components[1].recovery_model.recovery_activities['Repair'].time_steps = list(range(15, 20))
        assert geo_visualizer.component_is_in_state(system.components[1], 'Functional', 0) == True
        assert geo_visualizer.component_is_in_state(system.components[1], 'Functional', 20) == True
        assert geo_visualizer.component_is_in_state(system.components[1], 'Functional', 19) == False
        assert geo_visualizer.component_is_in_state(system.components[1], 'RapidInspection', 1) == True
        assert geo_visualizer.component_is_in_state(system.components[1], 'RapidInspection', 2) == False
        assert geo_visualizer.component_is_in_state(system.components[1], 'Repair', 2) == False
        assert geo_visualizer.component_is_in_state(system.components[1], 'Repair', 15) == True





