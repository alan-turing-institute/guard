from . import context
from .fixtures import default_parameters
from guard import community, polity, parameters
import pytest

# Create a strong polity, large with all ultrasocietal traits
@pytest.fixture
def strong_polity():
    state_size = 20
    state = polity.Polity([community.Community(parameters.defaults) for i in range(state_size)])
    for tile in state.communities:
        tile.ultrasocietal_traits = [True]*parameters.defaults.n_ultrasocietal_traits
    return state

# Create a Mediocre polity
@pytest.fixture
def mediocre_polity():
    state_size = 5
    state = polity.Polity([community.Community(parameters.defaults) for i in range(state_size)])
    return state

# Create a weak polity, small with no ultrasocietal traits
@pytest.fixture
def weak_polity():
    state_size = 1
    state = polity.Polity([community.Community(parameters.defaults) for i in range(state_size)])
    return state

# Test success probability calculation
class TestSuccessProbability(object):
    # Ensure minimum of attack success probability is 0
    def test_impossible_attack(self, default_parameters, strong_polity, weak_polity):
        params = default_parameters
        attacker = weak_polity.communities[0]
        defender = strong_polity.communities[0]

        probability = attacker.success_probability(defender, params)

        assert probability == 0

    # Calculate the probability of an almost certain victory
    def test_almost_certain_attack(self, default_parameters, strong_polity, weak_polity):
        params = default_parameters
        attacker = strong_polity.communities[0]
        defender = weak_polity.communities[0]

        probability = attacker.success_probability(defender, params)

        assert probability == 0.9900990099009901

# Test attack routine
class TestAttack(object):
    # Test transfer of community after an attack which is certain to succeed
    def test_certain_attack(self, default_parameters, strong_polity, mediocre_polity):
        params = default_parameters
        attacker = strong_polity
        defender = mediocre_polity

        attacking_community = attacker.communities[4]
        defending_community = defender.communities[1]

        attacking_community.attack(target=defending_community, params=params, probability=1)

        assert all([attacker.size() == 21, defender.size() == 4, \
                defending_community in attacker.communities, \
                defending_community not in defender.communities])

# Test ethnocide routine
class TestEthnocide(object):
    # Ensure the ethnocide chance with no military tech or elevation is the base
    def test_base_ethnocide(self, default_parameters, strong_polity, weak_polity):
        params = default_parameters
        attacking_community = strong_polity.communities[0]
        defending_community = weak_polity.communities[0]

        assert attacking_community.ethnocide_probability(defending_community, params) == params.ethnocide_min
