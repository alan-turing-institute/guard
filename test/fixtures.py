import pytest
from guard import parameters

@pytest.fixture
def default_parameters():
    return parameters.defaults

@pytest.fixture
def custom_parameters():
    def _custom_parameters(**kwargs):
        return parameters.generate(**kwargs)
    return _custom_parameters
