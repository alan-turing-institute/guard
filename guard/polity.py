# Polity class
class Polity(object):
    def __init__(self, communities):
        self.communities = communities
        for community in communities:
            community.assign_to_polity(self)

    def __str__(self):
        string = "Polity:\n"
        string += "\tNumber of communities: {0}\n".format(self.size())
        string += "\tMean ultrasocietal traits: {0}\n".format(
                self.mean_ultrasocietal_traits())
        string += "\tCommunities:\n"
        for community in self.communities:
            community_string = str(community).split("\n")
            for line in community_string:
                string += "\t\t"+line+"\n"

        return string

    # Incorporate a community to the polity
    def add_community(self, community):
        community.assign_to_polity(self)
        self.communities.append(community)

    # Remove a community from the polity
    def remove_community(self, community):
        community.assign_to_polity(None)
        self.communities.remove(community)

    # Transfer a polity to the polity from another
    def transfer_community(self, community):
        community.polity.remove_community(community)
        self.add_community(community)

    # Disintegrate the polity returning a list of new polities, one for each
    # community
    def disintegrate(self):
        new_polities = [Polity([tile]) for tile in self.communities]
        self.communities = []
        return new_polities

    # Determine the size of the polity (in communities)
    def size(self):
        return len(self.communities)

    # Calculate the mean number of ultrasocietal traits of the communities of
    # this polity
    def mean_ultrasocietal_traits(self):
        return sum(
            [community.total_ultrasocietal_traits()
             for community in self.communities]
            ) / self.size()

    # Calculate the polities attack power
    # The attack power is the mean number of ultrasocietal traits in the
    # communities of the polity, multiplied by the size of the polity. Here
    # the size of the polity is omitted in the mean and multiplication to
    # save calculation time.
    def attack_power(self, params):
        power = sum([community.total_ultrasocietal_traits()
                     for community in self.communities])
        power *= params.ultrasocietal_attack_coefficient
        power += 1.
        return power

    # Determine the probability that the polity with disintegrate
    def disintegrate_probability(self, params):
        probability = (params.disintegration_size_coefficient * self.size() -
                       params.disintegration_ultrasocietal_trait_coefficient *
                       self.mean_ultrasocietal_traits())
        if probability < 0:
            return params.disintegration_base
        else:
            return min(params.disintegration_base + probability, 1)

    # Attempt cultural shift on all communities
    def cultural_shift(self, params):
        for community in self.communities:
            community.cultural_shift(params)
