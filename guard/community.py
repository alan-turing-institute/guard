from enum import Enum, auto
from numpy.random import random, randint
from .parameters import defaults

DIRECTIONS = ('left','right','up','down')

# Terrain types enum
class Terrain(Enum):
    agriculture = auto()
    desert = auto()
    sea = auto()
    steppe = auto()

# Community (tile) class
class Community(object):
    def __init__(self, params, terrain=Terrain.agriculture, elevation=0):
        self.terrain = terrain
        self.elevation = elevation

        self.ultrasocietal_traits = [False]*params.n_ultrasocietal_traits
        self.military_techs = [False]*params.n_military_techs

        self.neighbours = dict.fromkeys(DIRECTIONS)

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
    def attempt_attack(self, params):
        direction = DIRECTIONS[randint(4)]
        target = self.neighbours[direction]

        # Don't attack an empty neighbour
        # It is important to replicate Turchin's results that communities attack
        # each neighbour with a probability of 1/4
        if target is None:
            return

        # Don't attack a neighbour in the same polity
        if target.polity is self.polity:
            return

        if target.terrain is Terrain.agriculture:
            self.attack(target, params)

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
    def diffuse_military_tech(self, params):
        # Only agriculture tiles can spread technology
        if self.terrain is not Terrain.agriculture:
            return

        # Select a tech to share
        selected_tech = randint(params.n_military_techs)
        if self.military_techs[selected_tech] == True:
            # Choose random direction to spread tech
            spread_direction = DIRECTIONS[randint(4)]

            # Check if neighbour has this tech
            if self.neighbours[spread_direction].military_techs[selected_tech] == False:
                self.neighbours[spread_direction].military_techs[selected_tech] = True
