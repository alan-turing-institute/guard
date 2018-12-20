from collections import namedtuple

_default_parameters = { \
        # Number of ultrasocietal traits
        'n_ultrasocietal_traits':10, \
        # Number of military technologies
        'n_military_techs':10, \
        # Attack power due to ultrasoceital traits coefficient (beta in Turchin et. al 2013)
        'ultrasocietal_attack_coefficient':1, \
        # Defence due to elevation coefficient (gamma in Turchin et. al 2013)
        'elevation_defence_coefficient':4, \
        # Minimum probability of ethnocide (with no military technologies) (epsilon_min in Turchin et. al 2013)
        'ethnocide_min':0.05, \
        # Maximum probability of ethnocide (with all military technologies) (epsilon_max in Turchin et. al 2013)
        'ethnocide_max':1, \
        # Defence from ethnocide due to elevation coefficient (gamma_1 in Turchin et. al 2013)
        'ethnocide_elevation_coefficient':1, \
        # Base disintegration probability (delta_0 in Turchin et. al 2013)
        'disintegration_base':0.05, \
        # Disintegration due to polity size coefficient (delta_s in Turchin et. al 2013)
        'disintegration_size_cofficient':0.05, \
        # Protection from disintegration due to ultrasocietal traits coefficient (delta_a in Turchin et. al 2013)
        'disintegration_ultrasocietal_trait_coefficient':2, \
        # Mutation to an ultrasocietal trait probability (mu_01 in Turchin et. al 2013)
        'mutation_to_ultrasocietal':0.0001, \
        # Mutation away from an ultrasocietal trait probability (mu_10 in Turchin et. al 2013)
        'mutation_from_ultrasocietal':0.002}

_Parameters = namedtuple('Parameters', _default_parameters.keys())

# Generate a parameter set from the default set with any adjustments provided
# keyword arguments
def generate(**kwargs):
    parameters = _default_parameters
    # Override defaults
    for key, value in kwargs.items():
        if key in parameters:
            parameters[key] = value

    return _Parameters(*parameters.values())

default_parameters = generate()

# Number of ultrasocietal traits
N_ULTRASOCIETAL_TRAITS = 10
# Number of military technologies
N_MILITARY_TECHS = 10

# Attack power due to ultrasoceital traits coefficient (beta in Turchin et. al 2013)
ULTRASOCIETAL_ATTACK_COEFFICIENT = 1
# Defence due to elevation coefficient (gamma in Turchin et. al 2013)
ELEVATION_DEFENCE_COEFFICIENT = 4

# Minimum probability of ethnocide (with no military technologies) (epsilon_min in Turchin et. al 2013)
ETHNOCIDE_MIN = 0.05
# Maximum probability of ethnocide (with all military technologies) (epsilon_max in Turchin et. al 2013)
ETHNOCIDE_MAX = 1
# Defence from ethnocide due to elevation coefficient (gamma_1 in Turchin et. al 2013)
ETHNOCIDE_ELEVATION_COEFFICIENT = 1

# Base disintegration probability (delta_0 in Turchin et. al 2013)
DISINTEGRATION_BASE = 0.05
# Disintegration due to polity size coefficient (delta_s in Turchin et. al 2013)
DISINTEGRATION_SIZE_COEFFICIENT = 0.05
# Protection from disintegration due to ultrasocietal traits coefficient (delta_a in Turchin et. al 2013)
DISINTEGRATION_ULTRASOCIETAL_TRAIT_COEFFICIENT = 2

# Mutation to an ultrasocietal trait probability (mu_01 in Turchin et. al 2013)
MUTATION_TO_ULTRASOCIETAL = 0.0001
# Mutation away from an ultrasocietal trait probability (mu_10 in Turchin et. al 2013)
MUTATION_FROM_ULTRASOCIETAL = 0.002
