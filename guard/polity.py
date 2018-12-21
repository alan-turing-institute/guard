from . import community

# Polity class
class Polity(object):
    def __init__(self,communities):
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

    # Transfer a polity to the polity from another
    def transfer_community(self,community):
        community.polity.remove_community(community)
        self.add_community(community)

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
    def attack_power(self, params):
        power = 0
        for community in self.communities:
            power += community.total_ultrasocietal_traits()
        power *= params.ultrasocietal_attack_coefficient
        power += 1.
        return power

    # Determine the probability that the polity with disintegrate
    def disintegrate_probability(self, params):
        # Determine probability
        probability = params.disintegration_base
        probability += params.disintegration_size_coefficient * self.size()
        probability -= params.disintegration_ultrasocietal_trait_coefficient * \
                self.mean_ultrasocietal_traits()

        # Ensure probability is in the range [0,1]
        if probability < 0:
            probability = 0
        elif probability > 1:
            probability =1

        return probability

    # Attempt cultural shift on all communities
    def cultural_shift(self, params):
        for community in self.communities:
            community.cultural_shift(params)
