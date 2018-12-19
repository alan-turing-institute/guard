from . import context
from guard import community, parameters
import pytest

@pytest.fixture
def basic_community():
    return community.Community()

@pytest.fixture
def advanced_community():
    tile = community.Community()
    tile.military_techs = [True]*parameters.N_MILITARY_TECHS
    return tile

# Test the community class
class TestCommunity(object):
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

# Test military technology diffusion
class TestMilitaryTechDifussion(object):
    # Test a case of certain diffusion
    def test_tech_diffusion(self, basic_community, advanced_community):
        advanced = advanced_community
        basic = basic_community

        # Make basic the neighbour of advances in all directions for the
        # purposes of this test
        for direction in ['left','right','up','down']:
            advanced.neighbours[direction] = basic

        advanced.diffuse_military_tech()

        assert basic.total_military_techs() == 1
