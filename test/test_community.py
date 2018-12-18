from . import context
from guard import community
from guard import parameters

# Test the community class
class TestCommunity(object):
    community = community.Community()

    def test_total_ultrasocietal_traits(self):
        self.community.ultrasocietal_traits = [True]*4 + [False]*6
        assert self.community.total_ultrasocietal_traits() == 4

    def test_total_military_techs(self):
        self.community.military_techs = [False]*3 + [True]*7
        assert self.community.total_military_techs() == 7

# Test cultural shift
class TestCulturalShift(object):
    # Set mutation to always occur
    parameters.MUTATION_TO_ULTRASOCIETAL = 1
    parameters.MUTATION_FROM_ULTRASOCIETAL = 1

    def test_shift_to_true(self):
        tile = community.Community()

        tile.cultural_shift()
        assert tile.total_ultrasocietal_traits() == parameters.N_ULTRASOCIETAL_TRAITS

    def test_shift_to_false(self):
        tile = community.Community()
        tile.ultrasocietal_traits = [True]*parameters.N_ULTRASOCIETAL_TRAITS

        tile.cultural_shift()
        assert tile.total_ultrasocietal_traits() == 0

