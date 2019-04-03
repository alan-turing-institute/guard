import pytest
from guard import parameters, world, terrain


@pytest.fixture(scope='session')
def default_parameters():
    return parameters.defaults


@pytest.fixture
def custom_parameters():
    def _custom_parameters(**kwargs):
        return parameters.generate(**kwargs)
    return _custom_parameters


@pytest.fixture(scope='class')
def world_5x5(default_parameters):
    map_ = world.World(5, 5, params=default_parameters)
    map_.create_flat_agricultural_world()
    return map_


@pytest.fixture
def generate_world():
    def _generate_world(xdim, ydim, params=parameters.defaults):
        map_ = world.World(xdim, ydim, params=params)
        map_.create_flat_agricultural_world()
        return map_
    return _generate_world


@pytest.fixture
def generate_world_with_sea():
    def _generate_world(xdim, ydim, sea_tiles):
        map_ = world.World(xdim, ydim)
        map_.create_flat_agricultural_world()

        for coordinate in sea_tiles:
            x, y = coordinate
            map_.index(x, y).terrain = terrain.sea

        map_.set_littoral_tiles()
        map_.set_littoral_neighbours()
        return map_
    return _generate_world
