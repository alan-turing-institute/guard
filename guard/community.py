from enum import Enum, auto
from numpy.random import random, randint
from . import parameters

DIRECTIONS = ('left','right','up','down')

# Terrain types enum
class Terrain(Enum):
    agriculture = auto()
    desert = auto()
    sea = auto()
    steppe = auto()

# Community (tile) class
class Community(object):
    def __init__(self,terrain=Terrain.agriculture,elevation=0):
        self.terrain = terrain
        self.elevation = elevation

        self.ultrasocietal_traits = [False]*parameters.N_ULTRASOCIETAL_TRAITS
        self.military_techs = [False]*parameters.N_MILITARY_TECHS

        self.neighbours = dict.fromkeys(DIRECTIONS)

        self.polity = None

    # Total number of ultrasocietal traits
    def total_ultrasocietal_traits(self):
        return sum(self.ultrasocietal_traits)

    # Total number of military techs
    def total_military_techs(self):
        return sum(self.military_techs)

    # Assign community to a polity
    def assign_to_polity(self,polity):
        self.polity = polity

    # Determine the power of an attack from this community (equal to
    # the polities attack power)
    def attack_power(self):
        return self.polity.attack_power()

    # Determine the power of this community in defending
    def defence_power(self):
        return self.polity.attack_power() + \
                parameters.ELEVATION_DEFENSE_COEFFICIENT * self.elevation

    # Determine the probability of a successful attack
    def success_probability(self, target):
        power_attacker = self.attack_power()
        power_defender = target.defence_power()

        success = (power_attacker - power_defender) / (power_attacker + power_defender)
        # Ensure probability is in the range [0,1]
        if success < 0:
            success = 0

        return success

    # Determine the probability of ethnocide
    def ethnocide_probability(self,target):
        probability = parameters.ETHNOCIDE_MIN
        probability += (parameters.ETHNOCIDE_MAX - parameters.ETHNOCIDE_MIN) * \
                self.total_military_techs() / parameters.N_MILITARY_TECHS
        probability -= parameters.ETHNOCIDE_ELEVATION_COEFFICIENT * target.elevation

        #Ensure probability is in the range [0,1]
        if probability < 0:
            probability = 0
        elif probability > 1:
            probability = 1

        return probability

    # Conduct an attack
    def attack(self, target, probability=None):
        if probability == None:
            probability = self.success_probability(target)
        # Determine whether attack was successful
        if probability > random():
            # Transfer defending community to attacker's polity
            self.polity.transfer_community(target)

            # Attempt ethnocide
            if self.ethnocide_probability(target):
                target.ultrasocietal_traits = self.ultrasocietal_traits

    # Attempt to attack a random neighbour
    def attempt_attack(self):
        direction = DIRECTIONS[randint(4)]
        target = self.neighbours[direction]

        if target is not None:
            if target.terrain is Terrain.agriculture:
                self.attack(target)

    # Local cultural shift (mutation of ultrasocietal traits vector)
    def cultural_shift(self):
        for index,trait in enumerate(self.ultrasocietal_traits):
            if trait == False:
                # Chance to develop an ultrasocietal trait
                if parameters.MUTATION_TO_ULTRASOCIETAL > random():
                    self.ultrasocietal_traits[index] = True
            else:
                # Chance to loose an ultrasocietal trait
                if parameters.MUTATION_FROM_ULTRASOCIETAL > random():
                    self.ultrasocietal_traits[index] = False

    # Attempt to spread military technology
    def diffuse_military_tech(self):
        # Only agriculture tiles can spread technology
        if self.terrain is not Terrain.agriculture:
            return

        # Select a tech to share
        selected_tech = randint(parameters.N_MILITARY_TECHS)
        if self.military_techs[selected_tech] == True:
            # Choose random direction to spread tech
            spread_direction = DIRECTIONS[randint(4)]

            # Check if neighbour has this tech
            if self.neighbours[spread_direction].military_techs[selected_tech] == False:
                self.neighbours[spread_direction].military_techs[selected_tech] = True
