import pytest
from guard import world, terrain, daterange, community, default_parameters


@pytest.fixture(scope='class')
def world_5x5():
    communities = [community.Community(default_parameters) for i in range(25)]
    map_ = world.World(5, 5, communities, default_parameters)
    return map_


@pytest.fixture(scope='session')
def daterange_0_100AD():
    return daterange.DateRange(0, 100)


@pytest.fixture(scope='session')
def dateranges_5_centuries():
    return [
        daterange.DateRange(start_year, end_year)
        for (start_year, end_year) in [
            (0, 100),
            (100, 200),
            (200, 300),
            (300, 400),
            (400, 500)
            ]
        ]


@pytest.fixture
def generate_world():
    def _generate_world(xdim, ydim, params=default_parameters):
        communities = [
            community.Community(params) for i in range(xdim*ydim)
            ]
        map_ = world.World(xdim, ydim, communities, params)
        return map_
    return _generate_world


@pytest.fixture
def generate_world_with_sea():
    def _generate_world(xdim, ydim, sea_tiles):
        communities = [
            community.Community(default_parameters) for i in range(xdim*ydim)
            ]
        for coordinate in sea_tiles:
            x, y = coordinate
            communities[x + y*xdim] = community.Community(
                default_parameters,
                landscape=terrain.sea
                )

        map_ = world.World(xdim, ydim, communities, default_parameters)
        return map_
    return _generate_world
