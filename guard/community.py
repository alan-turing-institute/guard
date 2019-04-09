"""
Community class.
"""
from . import terrain, period
from collections import namedtuple
from numpy.random import random, randint, choice

"""
Names of the four cardinal directions
"""
DIRECTIONS = ('left', 'right', 'up', 'down')

"""
Littoral neighbour named tuple
"""
LittoralNeighbour = namedtuple('LittoralNeighbour', ['neighbour', 'distance'])


class Community(object):
    """
    A community (tile, cell) on the simulation map.

    Args:
        params (Parameters): The set of simulation parameters to use.
        landscape (Terrain, default terrain.agriculture): The terrain of the
            community. The default is agriculutural land.
        elevation (int, default=0): The elevation of the community in metres.
        active_from (Period, default=period.agri1): The period at which the
            community first becomes agricultural. This is only important for
            communities with the terrain.agriculture terain. The default is
            period.agri, which means the community is agriculturally active
            from the begining of the simulation.

    Attributes:
        terrain (Terrain): The terrain of the community.
        elevation (int): The communities elevation in kilometres.
        ultrasocietal_traits (list[bool]): A vector of which ultrasocietal
            traits the community possesses.
        military_techs (list[bool]): A vector of which military technologies
            the community possesses.
        position (tuple[int,int]): The position of the community on its map in
            the format (x,y).
        neighbours (dict): The communities neighbours in the four cardinal
            directions.
        littoral (bool): True if the community is littoral, False otherwise.
        littoral_neighbours (list[LittoralNeighbour]): A list of all of the
            communities littoral neighbours as LittoralNeighbour named tuples.
        polity (Polity): The polity to which the community belongs.

    """
    def __init__(self, params, landscape=terrain.agriculture, elevation=0,
                 active_from=period.agri1):
        self.terrain = landscape
        self.elevation = elevation
        self.period = active_from

        self.ultrasocietal_traits = [False]*params.n_ultrasocietal_traits
        # Steppe communities start with all military technologies
        if landscape == terrain.steppe:
            self.military_techs = [True]*params.n_military_techs
        else:
            self.military_techs = [False]*params.n_military_techs

        self.position = (None, None)
        self.neighbours = dict.fromkeys(DIRECTIONS)
        self.littoral = False
        self.littoral_neighbours = []

        self.polity = None

    def __str__(self):
        string = "Community:\n"
        string += "\tTerrain: {0}\n".format(self.terrain)
        string += "\tElevation: {0}\n".format(self.elevation)
        string += "\tTotal ultrasocietal traits: {0}\n".format(
            self.total_ultrasocietal_traits())
        string += "\tTotal military technologies: {0}\n".format(
            self.total_military_techs())

        return string

    def total_ultrasocietal_traits(self):
        """
        Total number of ultrasocietal traits.

        Returns:
            (int): The total number of ultrasocietal traits.
        """
        return sum(self.ultrasocietal_traits)

    def total_military_techs(self):
        """
        Total number of military technologies.

        Returns:
            (int): The total number of military technologies.
        """
        return sum(self.military_techs)

    def is_active(self, step_number):
        """
        Determine if community is active (in a currently agricultural region).

        Args:
            step_number (int): The current step number.

        Returns:
            (bool): True if the community is active, False otherwise.
        """
        return self.period.is_active(step_number)

    def can_attack(self, step_number):
        """
        Determine if the community can attack.

        Args:
            step_number (int): The current step number.

        Returns:
            (bool): True if the community may attack, False otherwise.
        """
        if self.terrain.polity_forming:
            if self.is_active(step_number):
                return True
        return False

    def assign_to_polity(self, polity):
        """
        Assign community to a polity

        Args:
            polity (Polity): The polity to assign the community to.
        """
        self.polity = polity

    def littoral_neighbours_in_range(self, distance):
        """
        Filter the littoral neighbours list to only include neighbours within a
        given distance.

        Args:
            distance (float): The threshold distance.

        Returns:
            (list[LittoralNeighbour]): A list of all littoral neighours within
                range.
        """
        return [neighbour for neighbour in self.littoral_neighbours
                if neighbour.distance <= distance]

    def attack_power(self, params):
        """
        Determine the power of an attack from this community (equal to the
        polities attack power).

        Args:
            params (Parameters): The simulation parameter set.

        Returns:
            (float): The attack power.
        """
        return self.polity.attack_power(params)

    def defence_power(self, params, sea_attack):
        """
        Determine the power of this community in defending.

        Args:
            params (Parameters): The simulation parameter set.
            sea_attack (bool): Whether the attack is made by sea.

        Returns:
            (float): The defence power.
        """
        power = self.polity.attack_power(params)
        if not sea_attack:
            power += params.elevation_defence_coefficient * self.elevation
        return power

    def success_probability(self, target, params, sea_attack):
        """
        Determine the probability of a success of an attack from this community
        to a target.

        Args:
            target (Community): The community to attack.
            params (Parameters): The simulation parameter set.
            sea_attack (bool): Whether the attack is made by sea.

        Return:
            (float): The probability of success.
        """
        power_attacker = self.attack_power(params)
        power_defender = target.defence_power(params, sea_attack)

        success = (
            (power_attacker - power_defender) /
            (power_attacker + power_defender)
            )
        # Ensure probability is in the range [0,1]
        if success < 0:
            success = 0

        return success

    def ethnocide_probability(self, target, params):
        """
        Determine the probability of ethnocide.

        Args:
            target (Community): The community under attack.
            params (Parameters): The simulation parameter set.

        Return:
            (float): The probability of ethnocide.
        """
        probability = params.ethnocide_min
        probability += (
            (params.ethnocide_max - params.ethnocide_min) *
            self.total_military_techs() / params.n_military_techs
            )
        probability -= (params.ethnocide_elevation_coefficient *
                        target.elevation)

        # Ensure probability is in the range [0,1]
        if probability < 0:
            probability = 0
        elif probability > 1:
            probability = 1

        return probability

    def attack(self, target, params, sea_attack, probability=None):
        """
        Conduct an attack.

        Args:
            target (Community): The community to attack.
            params (Parameters): The simulation parameter set.
            sea_attack (bool): Whether the attack is made by sea.
            probability (float, default=None): Manually set the success
                probability. If None this has no effect. Used for testing.
        """
        if probability is None:
            probability = self.success_probability(target, params, sea_attack)
        # Determine whether attack was successful
        if probability > random():
            # Transfer defending community to attacker's polity
            self.polity.transfer_community(target)

            # Attempt ethnocide
            if self.ethnocide_probability(target, params) > random():
                target.ultrasocietal_traits[:] = self.ultrasocietal_traits

    def attempt_attack(self, params, step_number, sea_attack_distance,
                       callback=None):
        """
        Attempt to attack a random neighbour.

        Args:
            params (Parameters): The simulation parameter set.
            step_number (int): The current simulation step.
            sea_attack_distance (float): The maximum distance for a sea attack
                at this step.
            callback (function, default=None): A callback function to be
                invoked when a successful attack is made. Currently used to
                collect attack frequency.
        """
        direction = choice(DIRECTIONS)
        target = self.neighbours[direction]

        sea_attack = False
        proceed = True

        # Don't attack or spread technology to an empty neighbour
        # It is important to replicate Turchin's results that communities
        # attack each neighbour with a probability of 1/4
        if target is None:
            return

        if target.terrain is terrain.sea:
            # Sea attack
            # Find a littoral neighbour within range
            in_range = self.littoral_neighbours_in_range(sea_attack_distance)
            target = in_range[choice(len(in_range))].neighbour
            sea_attack = True
        elif not target.terrain.polity_forming:
            # Don't attack or spread technology to a non-agricultural cell
            return

        # Ensure target is active (agricultural at the current time), otherwise
        # don't attack or spread technology
        if target.is_active(step_number) is False:
            return

        # Don't attack a neighbour in the same polity, but do spread technology
        if target.polity is self.polity:
            proceed = False

        # Conduct an attack if there is no reason not to
        if proceed:
            self.attack(target, params, sea_attack=sea_attack)
            if callback:
                callback(target)

        # Attempt to diffuse military technology regardless of whether the
        # attack proceeded or was successful
        self.diffuse_military_tech(target, params)

    def cultural_shift(self, params):
        """
        Local cultural shift (mutation of ultrasocietal traits vector).

        Args:
            params (Parameters): The simulation parameter set.
        """
        for index, trait in enumerate(self.ultrasocietal_traits):
            if trait is False:
                # Chance to develop an ultrasocietal trait
                if params.mutation_to_ultrasocietal > random():
                    self.ultrasocietal_traits[index] = True
            else:
                # Chance to loose an ultrasocietal trait
                if params.mutation_from_ultrasocietal > random():
                    self.ultrasocietal_traits[index] = False

    def diffuse_military_tech(self, target, params):
        """
        Attempt to spread military technology.

        Args:
            target (Community): The community to attempt to spread technology
                to.
            params (Parameters): The simulation parameter set.
        """
        # Select a tech to share
        selected_tech = randint(params.n_military_techs)
        if self.military_techs[selected_tech] is True:
            if params.military_tech_spread_probability > random():
                # Share this tech with the target
                target.military_techs[selected_tech] = True
