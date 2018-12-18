from . import community
from . import parameters

# Polity class
class Polity(object):
    def __init__(self,communities=[]):
        self.communities = communities
        for community in communities:
            community.assign_to_polity(self)

    # Incorporate a community to the polity
    def add_community(self,community):
        community.assign_to_polity(self)
        self.communities.append(community)

    # Remove a community from the polity
    def remove_community(self,community):
        community.assign_to_polity(None)
        self.communities.remove(community)

    # Determine the size of the polity (in communities)
    def size(self):
        return len(self.communities)

    # Calculate the mean number of ultrasocietal traits of the communities of
    # this polity
    def mean_ultrasocietal_traits(self):
        return sum([community.total_ultrasocietal_traits() for community in self.communities]) / len(self.communities)

    # Calculate the polities attack power
    # The attack power is the mean number of ultrasocietal traits in the
    # communities of the polity, multiplied by the size of the polity. Here
    # the size of the polity is omitted in the mean and multiplication to
    # save calculation time.
    def attack_power(self):
        power = 0
        for community in self.communities:
            power += community.total_ultrasocietal_traits()
        power *= parameters.ULTRASOCIETAL_ATTACK_COEFFICIENT
        power += 1.
        return power

    # Determine the probability that the polity with disintegrate
    def disintegrate_probability(self):
        # Determine probability
        probability = parameters.DISINTEGRATION_BASE
        probability += parameters.DISINTEGRATION_SIZE_COEFFICIENT * self.size()
        probability -= parameters.DISINTEGRATION_ULTRASOCIETAL_TRAIT_COEFFICIENT * \
                self.mean_ultrasocietal_traits()

        # Ensure probability is in the range [0,1]
        probability = max(probability,0)
        probability = min(probability,1)
        return probability

    # Attempt cultural shift on all communities
    def cultural_shift(self):
        for community in self.communities:
            community.cultural_shift()
