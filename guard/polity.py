"""
Polity Module.
"""


class Polity(object):
    """
    Polity class.

    Args:
        communities (list[Community]): A list of communities which belong to
            the polity.

    Attributes:
        communities (list[Community]): A list of communities which belong to
            the polity.
    """
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

    def add_community(self, community):
        """
        Incorporate a community to the polity.

        Args:
            community (Community): The community to add.

        Notes:
            This routine is not safe as it does not check whether the community
            already belongs to a polity. It is only used in testing.
        """
        community.assign_to_polity(self)
        self.communities.append(community)

    def remove_community(self, community):
        """
        Remove a community from the polity.

        Args:
            community (Community): The community to remove.
        """
        community.assign_to_polity(None)
        self.communities.remove(community)

    def transfer_community(self, community):
        """
        Transfer a community to the polity from another

        Args:
            community (Community): The community to transfwer.
        """
        community.polity.remove_community(community)
        self.add_community(community)

    def disintegrate(self):
        """
        Disintegrate the polity.

        Returns:
            (list[Polity]): A list of new, single-community polities created
                from the distintegration of the polity.
        """
        new_polities = [Polity([tile]) for tile in self.communities]
        self.communities = []
        return new_polities

    def size(self):
        """
        Determine the size of the polity (in communities).

        Returns:
            (int): The number of communities in the polity.
        """
        return len(self.communities)

    def mean_ultrasocietal_traits(self):
        """
        Calculate the mean number of ultrasocietal traits of the communities of
        this polity.

        Returns:
            (float): The number number of ultrasocietal traits.
        """
        return sum(
            [community.total_ultrasocietal_traits()
             for community in self.communities]
            ) / self.size()

    def attack_power(self, params):
        """
        Calculate the polities attack power.

        Args:
            params (Parameters): The simulation parameter set.

        Returns:
            (float): The attack power.

        Notes:
            The attack power is the mean number of ultrasocietal traits in the
            communities of the polity, multiplied by the size of the polity.
            Here the size of the polity is omitted in the mean and
            multiplication to save calculation time.
        """
        power = sum([community.total_ultrasocietal_traits()
                     for community in self.communities])
        power *= params.ultrasocietal_attack_coefficient
        power += 1.
        return power

    def disintegrate_probability(self, params):
        """
        Determine the probability that the polity with disintegrate.

        Args:
            params (Parameters): The simulation parameter set.

        Returns:
            (float): The disintegration probability.
        """
        probability = (params.disintegration_size_coefficient * self.size() -
                       params.disintegration_ultrasocietal_trait_coefficient *
                       self.mean_ultrasocietal_traits())
        if probability < 0:
            return params.disintegration_base
        else:
            return min(params.disintegration_base + probability, 1)

    def cultural_shift(self, params):
        """
        Attempt cultural shift on all communities.

        Args:
            params (Parameters): The simulation parameter set.
        """
        for community in self.communities:
            community.cultural_shift(params)
