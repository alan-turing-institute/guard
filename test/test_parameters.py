from guard import parameters
import pytest


# Ensure custom keys are assigned correctly and don't affect the defaults
def test_custom_parameter(default_parameters, custom_parameters):
    default = default_parameters
    n_military_techs = 10
    ethnocide_max = 500
    custom = custom_parameters(n_military_techs=n_military_techs,
                               ethnocide_max=ethnocide_max)

    print(default)
    print(parameters._default_parameters.items())
    assert default.n_military_techs == parameters._default_parameters[
        'n_military_techs']
    assert custom.n_military_techs == n_military_techs
    assert default.n_military_techs != custom.n_military_techs

    assert default.ethnocide_max == parameters._default_parameters[
            'ethnocide_max']
    assert custom.ethnocide_max == ethnocide_max
    assert default.ethnocide_max != custom.ethnocide_max


# Ensure an exception is raised when trying define an invalid parameter
def test_invalid_key(custom_parameters):
    with pytest.raises(parameters.ParameterKeyException):
        custom_parameters(bad_key='test')
