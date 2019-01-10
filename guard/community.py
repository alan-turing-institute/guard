from collections import namedtuple
from enum import Enum, auto
from numpy.random import random, randint, choice
from .parameters import defaults

DIRECTIONS = ('left','right','up','down')

# Terrain types enum
class Terrain(Enum):
    agriculture = auto()
    desert = auto()
    sea = auto()
    steppe = auto()

# Agricultural periods
class Period(Enum):
    # Agricultural from 1500BCE (the beginning)
    agri1 = auto()
    # Agricultural from 300CE
    agri2 = auto()
    # Agricultural from 700CE
    agri3 = auto()

# Littoral neighbour named tuple
LittoralNeighbour = namedtuple('LittoralNeighbour', ['neighbour', 'distance'])

# Community (tile) class
class Community(object):
    def __init__(self, params, terrain=Terrain.agriculture, elevation=0,
            active_from=Period.agri1):
        self.terrain = terrain
        self.elevation = elevation
        self.active_from = active_from

        if self.active_from == Period.agri1:
            self.active = True
        else:
            self.active = False

        self.ultrasocietal_traits = [False]*params.n_ultrasocietal_traits
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
        string += "\tTotal ultrasocietal traits: {0}\n".format(self.total_ultrasocietal_traits())
        string += "\tTotal military technologies: {0}\n".format(self.total_military_techs())

        return string

    # Total number of ultrasocietal traits
    def total_ultrasocietal_traits(self):
        return sum(self.ultrasocietal_traits)

    # Total number of military techs
    def total_military_techs(self):
        return sum(self.military_techs)

    # Assign community to a polity
    def assign_to_polity(self, polity):
        self.polity = polity

    # Filter the littoral neighbours list to only include neighbours within
    # a given distance
    def littoral_neighbours_in_range(self, distance):
        return list(filter(lambda neighbour: neighbour.distance <= distance, self.littoral_neighbours))

    # Determine the power of an attack from this community (equal to
    # the polities attack power)
    def attack_power(self, params):
        return self.polity.attack_power(params)

    # Determine the power of this community in defending
    def defence_power(self, params):
        return self.polity.attack_power(params) + \
                params.elevation_defence_coefficient * self.elevation

    # Determine the probability of a successful attack
    def success_probability(self, target, params):
        power_attacker = self.attack_power(params)
        power_defender = target.defence_power(params)

        success = (power_attacker - power_defender) / (power_attacker + power_defender)
        # Ensure probability is in the range [0,1]
        if success < 0:
            success = 0

        return success

    # Determine the probability of ethnocide
    def ethnocide_probability(self, target, params):
        probability = params.ethnocide_min
        probability += (params.ethnocide_max - params.ethnocide_min) * \
                self.total_military_techs() / params.n_military_techs
        probability -= params.ethnocide_elevation_coefficient * target.elevation

        #Ensure probability is in the range [0,1]
        if probability < 0:
            probability = 0
        elif probability > 1:
            probability = 1

        return probability

    # Conduct an attack
    def attack(self, target, params, probability=None):
        if probability == None:
            probability = self.success_probability(target, params)
        # Determine whether attack was successful
        if probability > random():
            # Transfer defending community to attacker's polity
            self.polity.transfer_community(target)

            # Attempt ethnocide
            if self.ethnocide_probability(target, params):
                target.ultrasocietal_traits = self.ultrasocietal_traits

    # Attempt to attack a random neighbour
    def attempt_attack(self, params, sea_attack_distance):
        direction = choice(DIRECTIONS)
        target = self.neighbours[direction]

        proceed = True

        # Don't attack or spread technology to an empty neighbour
        # It is important to replicate Turchin's results that communities attack
        # each neighbour with a probability of 1/4
        if target is None:
            return

        if target.terrain is Terrain.sea:
            # Sea attack
            # Find a littoral neighbour within range
            target = choice(self.littoral_neighbours_in_range(sea_attack_distance))
        elif target.terrain is not Terrain.agriculture:
            # Don't attack or spread technology to a non-agricultural cell
            return

        # Ensure target is active (agricultural at the current time), otherwise
        # don't attack or spread technology
        if not target.active:
            return

        # Don't attack a neighbour in the same polity, but do spread technology
        if target.polity is self.polity:
            proceed = False

        # Conduct an attack if there is no reason not to
        if proceed:
            self.attack(target, params)

        # Attempt to diffuse military technology regardless of whether the attack
        # proceeded or was successful
        self.diffuse_military_tech(target, params)

    # Local cultural shift (mutation of ultrasocietal traits vector)
    def cultural_shift(self, params):
        for index,trait in enumerate(self.ultrasocietal_traits):
            if trait == False:
                # Chance to develop an ultrasocietal trait
                if params.mutation_to_ultrasocietal > random():
                    self.ultrasocietal_traits[index] = True
            else:
                # Chance to loose an ultrasocietal trait
                if params.mutation_from_ultrasocietal > random():
                    self.ultrasocietal_traits[index] = False

    # Attempt to spread military technology
    def diffuse_military_tech(self, target, params):
        # Select a tech to share
        selected_tech = randint(params.n_military_techs)
        if self.military_techs[selected_tech] == True:
            # Share this tech with the target
            target.military_techs[selected_tech] = True
