from enum import Enum, auto
from numpy.random import random
from . import parameters

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

        self.neighbours = [None]*4

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
        return self.attack_power() + \
                parameters.ELEVATION_DEFENSE_COEFFICIENT * self.elevation

    # Local cultural shift (mutation of ultrasocietal traits vector)
    def cultural_shift(self):
        for index,trait in enumerate(self.ultrasocietal_traits):
            if trait == False:
                # Chance to develop an ultrasocietal trait
                if random() < parameters.MUTATION_TO_ULTRASOCIETAL:
                    self.ultrasocietal_traits[index] = True
            else:
                # Chance to loose an ultrasocietal trait
                if random() < parameters.MUTATION_FROM_ULTRASOCIETAL:
                    self.ultrasocietal_traits[index] = False
