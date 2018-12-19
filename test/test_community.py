from . import context
from guard import community, parameters
import pytest

@pytest.fixture
def basic_community():
    return community.Community()

# Test the community class
class TestCommunity(object):
    community = community.Community()

    def test_total_ultrasocietal_traits(self,basic_community):
        traits = 4
        tile = basic_community
        tile.ultrasocietal_traits = [True]*traits + [False]*(parameters.N_ULTRASOCIETAL_TRAITS-traits)
        assert tile.total_ultrasocietal_traits() == traits

    def test_total_military_techs(self,basic_community):
        techs = 7
        tile = basic_community
        tile.military_techs = [False]*(parameters.N_MILITARY_TECHS-techs) + [True]*techs
        assert tile.total_military_techs() == techs

# Test cultural shift
class TestCulturalShift(object):
    # Set mutation to always occur
    parameters.MUTATION_TO_ULTRASOCIETAL = 1
    parameters.MUTATION_FROM_ULTRASOCIETAL = 1

    def test_shift_to_true(self, basic_community):
        tile = basic_community

        tile.cultural_shift()
        assert tile.total_ultrasocietal_traits() == parameters.N_ULTRASOCIETAL_TRAITS

    def test_shift_to_false(self, basic_community):
        tile = basic_community
        tile.ultrasocietal_traits = [True]*parameters.N_ULTRASOCIETAL_TRAITS

        tile.cultural_shift()
        assert tile.total_ultrasocietal_traits() == 0

