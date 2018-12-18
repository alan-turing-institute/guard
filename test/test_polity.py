from . import context
from guard import community, polity, parameters

# Test the polity class
class TestPolity(object):
    # Set of communities for testing
    communities = [community.Community() for i in range(10)]
    state = polity.Polity(communities)

    # Example numbers of ultrasocietal traits per community
    traits = [3, 4, 6, 3, 8, 3, 2, 2, 8, 6]
    mean_traits = sum(traits)/len(traits)

    # Add a new community to the polity
    def test_add_community(self):
        self.state.add_community(community.Community())
        assert self.state.size() == 11

    # Ensure new community points to the polity
    def test_new_community(self):
        assert self.state.communities[-1].polity is self.state

    # Remove a community from the polity
    def test_remove_community(self):
        self.state.remove_community(self.state.communities[0])
        assert self.state.size() == 10

    # Determine the mean number of ultrasocietal traits of communities
    # in the polity
    def test_mean_ultrasocietal_traits(self):
        set_ultrasocietal_traits(self.state,self.traits)
        assert self.mean_traits == self.state.mean_ultrasocietal_traits()

    # Calculate the attack power of the polity
    def test_attack_power(self):
        set_ultrasocietal_traits(self.state,self.traits)
        attack_power = parameters.ULTRASOCIETAL_ATTACK_COEFFICIENT* \
                sum(self.traits) + 1.
        assert attack_power == self.state.attack_power()

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
    def test_negative_disintegration_probability(self):
        size = 10
        traits = [parameters.N_ULTRASOCIETAL_TRAITS]*size
        mean_traits = sum(traits)/len(traits)

        communities = [community.Community() for i in range(size)]
        state = polity.Polity(communities)
        set_ultrasocietal_traits(state,traits)

        probability = self.disintegration_probability(size,mean_traits)
        assert probability == state.disintegrate_probability() == 0

    # Ensure the maximum probability is 1
    def test_large_disintegration_probability(self):
        size = 100
        traits = [0]*size
        mean_traits = sum(traits)/len(traits)

        communities = [community.Community() for i in range(size)]
        state = polity.Polity(communities)
        set_ultrasocietal_traits(state,traits)

        probability = self.disintegration_probability(size,mean_traits)
        assert probability == state.disintegrate_probability() == 1

    # Calculate the probability for an intermediate case where the
    # probability is neither 1 nor 0
    def test_intermediate_disintegration_probability(self):
        size = 50
        traits = [1]*size
        mean_traits = sum(traits)/len(traits)

        communities = [community.Community() for i in range(size)]
        state = polity.Polity(communities)
        set_ultrasocietal_traits(state,traits)

        probability = self.disintegration_probability(size,mean_traits)
        assert all([probability > 0, probability < 1, probability == state.disintegrate_probability()])

# Tests for communities which require them to be members of a polity
class TestCommunitiesInPolity(object):
    # Set of communities for testing
    communities = [community.Community() for i in range(10)]
    state = polity.Polity(communities)

    # Example numbers of ultrasocietal traits per community
    traits = [3, 4, 6, 3, 8, 3, 2, 2, 8, 6]
    mean_traits = sum(traits)/len(traits)

    # Ensure all communities point to the polity
    def test_community_assignment(self):
        assert [community.polity for community in self.state.communities] == \
                [self.state]*len(self.state.communities)

    # Calculate attack power from a community object
    def test_community_attack_power(self):
        set_ultrasocietal_traits(self.state,self.traits)
        assert self.state.communities[0].attack_power() == self.state.attack_power()

    # Calculate the defensive power of a community
    def test_community_defence_power(self):
        elevation = 50
        index = 4

        self.state.communities[index].elevation = elevation
        defence_power = self.state.attack_power() + \
                parameters.ELEVATION_DEFENSE_COEFFICIENT * elevation

        assert defence_power == self.state.communities[index].defence_power()

# Assign the example ultrasocietal traits to polity
def set_ultrasocietal_traits(polity,traits):
    for i,number in enumerate(traits):
        polity.communities[i].ultrasocietal_traits = [True]*number + \
                [False]*(parameters.N_ULTRASOCIETAL_TRAITS-number)
