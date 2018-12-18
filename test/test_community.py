from . import context
from guard import community

# Test the community class
class TestCommunity(object):
    community = community.Community()

    def test_total_ultrasocietal_traits(self):
        self.community.ultrasocietal_traits = [True]*4 + [False]*6
        assert self.community.total_ultrasocietal_traits() == 4

    def test_total_military_techs(self):
        self.community.military_techs = [False]*3 + [True]*7
        assert self.community.total_military_techs() == 7
