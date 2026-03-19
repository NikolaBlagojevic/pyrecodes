"""
Session-scoped system templates. Each template is created once per test session.
Individual test fixtures deepcopy from these to get isolated, mutable instances
without paying the full create_system() cost on every test.
"""
import copy
import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file

FOLDER = './tests/test_inputs'


@pytest.fixture(scope='session')
def three_localities_system_template():
    input_dict = read_json_file(f'{FOLDER}/test_inputs_ThreeLocalitiesCommunity_Main.json')
    return main.create_system(FOLDER, input_dict)


@pytest.fixture(scope='session')
def virtual_community_system_template():
    input_dict = read_json_file(f'{FOLDER}/test_inputs_VirtualCommunity_Main.json')
    return main.create_system(FOLDER, input_dict)


@pytest.fixture(scope='session')
def three_localities_rewet_system_template():
    input_dict = read_json_file(f'{FOLDER}/test_inputs_ThreeLocalitiesCommunityREWET_Main.json')
    return main.create_system(FOLDER, input_dict)


def make_system(template):
    """Return a deep copy of a session-scoped system template."""
    return copy.deepcopy(template)
