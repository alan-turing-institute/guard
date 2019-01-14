from collections import namedtuple

# Default parameters taken from Turchin et al. 2013 supporting information
_default_parameters = { \
        # Number of ultrasocietal traits
        'n_ultrasocietal_traits':10, \
        # Number of military technologies
        'n_military_techs':5, \
        # Attack power due to ultrasoceital traits coefficient (beta in Turchin et al. 2013)
        'ultrasocietal_attack_coefficient':1, \
        # Defence due to elevation coefficient (gamma in Turchin et al. 2013)
        'elevation_defence_coefficient':4, \
        # Probability of military technology spreading (sigma in Turchin et al. 2013, unspecified)
        'military_tech_spread_probability':0.25, \
        # Minimum probability of ethnocide (with no military technologies) (epsilon_min in Turchin et al. 2013)
        'ethnocide_min':0.05, \
        # Maximum probability of ethnocide (with all military technologies) (epsilon_max in Turchin et al. 2013)
        #'ethnocide_max':1, \
        # Value from the APL code
        'ethnocide_max':2, \
        # Defence from ethnocide due to elevation coefficient (gamma_1 in Turchin et al. 2013)
        'ethnocide_elevation_coefficient':1, \
        # Base disintegration probability (delta_0 in Turchin et al. 2013)
        'disintegration_base':0.05, \
        # Disintegration due to polity size coefficient (delta_s in Turchin et al. 2013)
        'disintegration_size_coefficient':0.05, \
        # Protection from disintegration due to ultrasocietal traits coefficient (delta_a in Turchin et al. 2013)
        'disintegration_ultrasocietal_trait_coefficient':2, \
        # Mutation to an ultrasocietal trait probability (mu_01 in Turchin et al. 2013)
        'mutation_to_ultrasocietal':0.0001, \
        # Mutation away from an ultrasocietal trait probability (mu_10 in Turchin et al. 2013)
        'mutation_from_ultrasocietal':0.002, \
        # Base sea attack distance (d_sea from Turchin et al. 2013 supporting information)
        'base_sea_attack_distance':1, \
        # Sea attack increment per time step (Delta from Turchin et al. 2013 Supporting information)
        #'sea_attack_increment':0.025}
        # Value from the APL code
        'sea_attack_increment':0.0025}

# Paramteres named tuple constructor
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

# A default set of parameters as a named tuple
defaults = generate()
