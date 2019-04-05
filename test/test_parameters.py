from guard import default_parameters, generate_parameters
from guard.parameters import _default_parameters, ParameterKeyException
import pytest


# Ensure custom keys are assigned correctly and don't affect the defaults
def test_custom_parameter():
    default = default_parameters
    n_military_techs = 10
    ethnocide_max = 500
    custom = generate_parameters(n_military_techs=n_military_techs,
                                 ethnocide_max=ethnocide_max)

    assert default.n_military_techs == _default_parameters[
        'n_military_techs']
    assert custom.n_military_techs == n_military_techs
    assert default.n_military_techs != custom.n_military_techs

    assert default.ethnocide_max == _default_parameters[
            'ethnocide_max']
    assert custom.ethnocide_max == ethnocide_max
    assert default.ethnocide_max != custom.ethnocide_max


# Ensure an exception is raised when trying define an invalid parameter
def test_invalid_key():
    with pytest.raises(ParameterKeyException):
        generate_parameters(bad_key='test')
