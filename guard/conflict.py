from . import community, parameters
from numpy.random import random, randint

# Determine the probability of a successful attack
def success_probability(attacker, defender):
    power_attacker = attacker.attack_power()
    power_defender = defender.defence_power()

    success = (power_attacker - power_defender) / (power_attacker + power_defender)
    # Ensure probability is in the range [0,1]
    if success < 0:
        success = 0

    return success

# Determine the probability of ethnocide
def ethnocide_probability(attacker, defender):
    probability = parameters.ETHNOCIDE_MIN
    probability += (parameters.ETHNOCIDE_MAX - parameters.ETHNOCIDE_MIN) * \
            attacker.total_military_techs() / parameters.N_MILITARY_TECHS
    probability -= parameters.ETHNOCIDE_ELEVATION_COEFFICIENT * defender.elevation

    #Ensure probability is in the range [0,1]
    if probability < 0:
        probability = 0
    elif probability > 1:
        probability = 1

    return probability

# Conduct an attack
def attack(attacker, defender, probability=None):
    if probability == None:
        probability = success_probability(attacker, defender)
    # Determine whether attack was successful
    if probability > random():
        # Transfer defending community to attacker's polity
        attacker.polity.transfer_community(defender)

        # Attempt ethnocide
        if ethnocide_probability(attacker, defender):
            defender.ultrasocietal_traits = attacker.ultrasocietal_traits

# Attempt to attack a random neighbour
def attempt_attack(attacker):
    direction = community.DIRECTIONS[randint(4)]
    defender = attacker.neighbour[direction]

    if defender is not None:
        if defender.terrain is community.Terrain.agriculture:
            attack(attacker, attacker.neighbour[direction])
