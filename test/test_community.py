from guard import community, terrain, default_parameters, generate_parameters
import pytest


@pytest.fixture
def basic_community():
    def _basic_community(params=default_parameters):
        return community.Community(params)
    return _basic_community


@pytest.fixture
def advanced_community():
    tile = community.Community(default_parameters)
    tile.military_techs = [True]*default_parameters.n_military_techs
    return tile


# Test the community class
class TestCommunity(object):
    def test_total_ultrasocietal_traits(self, basic_community):
        traits = 4
        tile = basic_community()
        tile.ultrasocietal_traits = [True]*traits + [False]*(
            default_parameters.n_ultrasocietal_traits-traits)
        assert tile.total_ultrasocietal_traits() == traits

    def test_total_military_techs(self,  basic_community):
        techs = 7
        tile = basic_community()
        tile.military_techs = (
            [False]*(default_parameters.n_military_techs-techs) + [True]*techs
            )
        assert tile.total_military_techs() == techs

    def test_steppe_community(self):
        tile = community.Community(default_parameters,
                                   landscape=terrain.steppe)

        assert (
            tile.total_military_techs() == default_parameters.n_military_techs
            )


# Test cultural shift
class TestCulturalShift(object):
    def test_shift_to_true(self,  basic_community):
        params = generate_parameters(mutation_to_ultrasocietal=1,
                                     mutation_from_ultrasocietal=1)
        tile = basic_community(params)

        tile.cultural_shift(params)
        assert (
            tile.total_ultrasocietal_traits() == params.n_ultrasocietal_traits
            )

    def test_shift_to_false(self, basic_community):
        params = generate_parameters(mutation_to_ultrasocietal=1,
                                     mutation_from_ultrasocietal=1)
        tile = basic_community(params)
        tile.ultrasocietal_traits = [True]*params.n_ultrasocietal_traits

        tile.cultural_shift(params)
        assert tile.total_ultrasocietal_traits() == 0


# Test military technology diffusion
class TestMilitaryTechDifussion(object):
    # Test a case of certain diffusion
    def test_tech_diffusion(self, basic_community, advanced_community):
        params = generate_parameters(military_tech_spread_probability=1)
        advanced = advanced_community
        basic = basic_community()

        advanced.diffuse_military_tech(basic, params)
        assert basic.total_military_techs() == 1
