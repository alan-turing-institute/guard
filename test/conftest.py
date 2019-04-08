import pytest
from guard import World, Community, terrain, daterange, default_parameters


@pytest.fixture(scope='class')
def world_5x5():
    communities = [Community(default_parameters) for i in range(25)]
    world = World(5, 5, communities, default_parameters)
    return world


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


@pytest.fixture(scope='class')
def generate_world():
    def _generate_world(xdim, ydim, params=default_parameters):
        communities = [
            Community(params) for i in range(xdim*ydim)
            ]
        world = World(xdim, ydim, communities, params)
        return world
    return _generate_world


@pytest.fixture
def generate_world_with_sea():
    def _generate_world(xdim, ydim, sea_tiles):
        communities = [
            Community(default_parameters) for i in range(xdim*ydim)
            ]
        for coordinate in sea_tiles:
            x, y = coordinate
            communities[x + y*xdim] = Community(
                default_parameters,
                landscape=terrain.sea
                )

        world = World(xdim, ydim, communities, default_parameters)
        return world
    return _generate_world


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)
