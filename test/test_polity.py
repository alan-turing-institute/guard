from . import context
from guard import community, polity, parameters
import pytest

@pytest.fixture
def polity_10():
    state = polity.Polity([community.Community() for i in range(10)])
    return state

@pytest.fixture
def arbitrary_polity():
    def _arbitrary_polity(size):
        state = polity.Polity([community.Community() for i in range(size)])
        return state
    return _arbitrary_polity

@pytest.fixture
def example_traits():
    traits = [3, 4, 6, 3, 8, 3, 2, 2, 8, 6]
    mean_traits = sum(traits)/len(traits)
    return traits, mean_traits

# Test the polity class
class TestPolity(object):

    # Add a new community to the polity
    def test_add_community(self, polity_10):
        state = polity_10
        state.add_community(community.Community())
        assert state.size() == 11

    # Ensure new community points to the polity
    def test_new_community(self, polity_10):
        state = polity_10
        state.add_community(community.Community())
        assert state.communities[-1].polity is state

    # Remove a community from the polity
    def test_remove_community(self, polity_10):
        state = polity_10
        state.remove_community(state.communities[0])
        assert state.size() == 9

    # Determine the mean number of ultrasocietal traits of communities
    # in the polity
    def test_mean_ultrasocietal_traits(self, polity_10, example_traits):
        state = polity_10
        traits, mean_traits = example_traits
        set_ultrasocietal_traits(state,traits)
        assert mean_traits == state.mean_ultrasocietal_traits()

    # Calculate the attack power of the polity
    def test_attack_power(self, polity_10, example_traits):
        state = polity_10
        traits, mean_traits = example_traits
        set_ultrasocietal_traits(state, traits)
        attack_power = parameters.ULTRASOCIETAL_ATTACK_COEFFICIENT* \
                sum(traits) + 1.
        assert attack_power == state.attack_power()

# Test disintegration method
class TestDisintegration(object):
    # Calculate the disintegration probability
    def disintegration_probability(self,size,mean_traits):
        probability = parameters.DISINTEGRATION_BASE
        probability += parameters.DISINTEGRATION_SIZE_COEFFICIENT*size
        probability -= parameters.DISINTEGRATION_ULTRASOCIETAL_TRAIT_COEFFICIENT * \
                mean_traits

        # Ensure probability is in the range [0,1]
        if probability < 0:
            probability = 0
        elif probability > 1:
            probability = 1

        return probability

    # Ensure the minimum probability is 0
    def test_negative_disintegration_probability(self, polity_10):
        size = 10
        state = polity_10
        traits = [parameters.N_ULTRASOCIETAL_TRAITS]*size
        mean_traits = sum(traits)/len(traits)
        set_ultrasocietal_traits(state,traits)

        probability = self.disintegration_probability(size,mean_traits)
        assert probability == state.disintegrate_probability() == 0

    # Ensure the maximum probability is 1
    def test_large_disintegration_probability(self, arbitrary_polity):
        size = 100
        state = arbitrary_polity(size)
        traits = [0]*size
        mean_traits = sum(traits)/len(traits)
        set_ultrasocietal_traits(state,traits)

        probability = self.disintegration_probability(size,mean_traits)
        assert probability == state.disintegrate_probability() == 1

    # Calculate the probability for an intermediate case where the
    # probability is neither 1 nor 0
    def test_intermediate_disintegration_probability(self, arbitrary_polity):
        size = 50
        state = arbitrary_polity(size)
        traits = [1]*size
        mean_traits = sum(traits)/len(traits)
        set_ultrasocietal_traits(state,traits)

        probability = self.disintegration_probability(size,mean_traits)
        assert all([probability > 0, probability < 1, probability == state.disintegrate_probability()])

# Tests for communities which require them to be members of a polity
class TestCommunitiesInPolity(object):
    # Ensure all communities point to the polity
    def test_community_assignment(self, polity_10):
        state = polity_10
        assert [community.polity for community in state.communities] == \
                [state]*len(state.communities)

    # Calculate attack power from a community object
    def test_community_attack_power(self, polity_10, example_traits):
        state = polity_10
        traits, _ = example_traits
        set_ultrasocietal_traits(state,traits)
        assert state.communities[0].attack_power() == state.attack_power()

    # Calculate the defensive power of a community
    def test_community_defence_power(self, polity_10, example_traits):
        state = polity_10
        traits, _ = example_traits
        set_ultrasocietal_traits(state,traits)
        elevation = 50
        index = 4
        state.communities[index].elevation = elevation

        defence_power = state.attack_power() + \
                parameters.ELEVATION_DEFENSE_COEFFICIENT * elevation
        assert defence_power == state.communities[index].defence_power()

# Test attempting cultural shift on all communities in a polity
class TestCulturalShift(object):
    # Set cultural shift probabilities to unity
    parameters.MUTATION_TO_ULTRASOCIETAL = 1
    parameters.MUTATION_FROM_ULTRASOCIETAL = 1

    def test_shift_to_true(self, polity_10):
        state = polity_10
        state.cultural_shift()
        assert state.mean_ultrasocietal_traits() == parameters.N_ULTRASOCIETAL_TRAITS

    def test_shift_to_false(self, polity_10):
        state = polity_10
        for tile in state.communities:
            tile.ultrasocietal_traits = [True]*parameters.N_ULTRASOCIETAL_TRAITS
        state.cultural_shift()
        assert state.mean_ultrasocietal_traits() == 0

# Test transfering of a community from one polity to another
def test_transfer(arbitrary_polity):
    size_a = 10
    state_a = arbitrary_polity(size_a)
    size_b = 5
    state_b = arbitrary_polity(size_b)

    # Give the ceded community some characteristic trait
    ceded_community = state_b.communities[3]
    ceded_community.elevation = 12

    # Transfer the ceded community to state a from state b
    state_a.transfer_community(ceded_community)

    assert all([ceded_community in state_a.communities, \
            ceded_community not in state_b.communities, \
            state_a.size() == 11, state_b.size() == 4, \
            state_a.communities[-1].elevation == 12])

# Assign the example ultrasocietal traits to polity
def set_ultrasocietal_traits(polity,traits):
    for i,number in enumerate(traits):
        polity.communities[i].ultrasocietal_traits = [True]*number + \
                [False]*(parameters.N_ULTRASOCIETAL_TRAITS-number)
