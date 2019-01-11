from . import context
from .fixtures import default_parameters, custom_parameters
from guard import community, parameters
import pytest

@pytest.fixture
def basic_community():
    def _basic_community(params=parameters.defaults):
        return community.Community(params)
    return _basic_community

@pytest.fixture
def advanced_community():
    tile = community.Community(parameters.defaults)
    tile.military_techs = [True]*parameters.defaults.n_military_techs
    return tile

# Test the community class
class TestCommunity(object):
    def test_total_ultrasocietal_traits(self, default_parameters, basic_community):
        params = default_parameters
        traits = 4
        tile = basic_community()
        tile.ultrasocietal_traits = [True]*traits + [False]*(params.n_ultrasocietal_traits-traits)
        assert tile.total_ultrasocietal_traits() == traits

    def test_total_military_techs(self, default_parameters, basic_community):
        params = default_parameters
        techs = 7
        tile = basic_community()
        tile.military_techs = [False]*(params.n_military_techs-techs) + [True]*techs
        assert tile.total_military_techs() == techs

    def test_steppe_community(self, default_parameters):
        params = default_parameters
        tile = community.Community(params, terrain=community.Terrain.steppe)

        assert tile.total_military_techs() == params.n_military_techs

# Test cultural shift
class TestCulturalShift(object):
    def test_shift_to_true(self, custom_parameters, basic_community):
        params = custom_parameters(mutation_to_ultrasocietal=1, \
                mutation_from_ultrasocietal=1)
        tile = basic_community(params)

        tile.cultural_shift(params)
        assert tile.total_ultrasocietal_traits() == params.n_ultrasocietal_traits

    def test_shift_to_false(self, custom_parameters, basic_community):
        params = custom_parameters(mutation_to_ultrasocietal=1, \
                mutation_from_ultrasocietal=1)
        tile = basic_community(params)
        tile.ultrasocietal_traits = [True]*params.n_ultrasocietal_traits

        tile.cultural_shift(params)
        assert tile.total_ultrasocietal_traits() == 0

# Test military technology diffusion
class TestMilitaryTechDifussion(object):
    # Test a case of certain diffusion
    def test_tech_diffusion(self, default_parameters, basic_community, advanced_community):
        params = default_parameters
        advanced = advanced_community
        basic = basic_community()

        advanced.diffuse_military_tech(basic, params)
        assert basic.total_military_techs() == 1
