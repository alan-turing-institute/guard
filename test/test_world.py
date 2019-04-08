from guard import (World, terrain, generate_parameters,
                   default_parameters, period)
from guard.world import MissingYamlKey
from guard.community import LittoralNeighbour
from numpy import sqrt
import os
import pytest

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


# Test the assignment of neighbours
class TestNeighbours(object):
    # Ensure neighbours are correct in a 2x2 world
    def test_neighbours_2x2(self, generate_world):
        world = generate_world(xdim=2, ydim=2)

        # Define correct neighbours
        neighbours_00 = {'left': None, 'right': world.index(1, 0),
                         'up': world.index(0, 1), 'down': None}
        neighbours_01 = {'left': None, 'right': world.index(1, 1),
                         'up': None, 'down': world.index(0, 0)}
        neighbours_10 = {'left': world.index(0, 0), 'right': None,
                         'up': world.index(1, 1), 'down': None}
        neighbours_11 = {'left': world.index(0, 1), 'right': None,
                         'up': None, 'down': world.index(1, 0)}

        assert world.index(0, 0).neighbours == neighbours_00
        assert world.index(0, 1).neighbours == neighbours_01
        assert world.index(1, 0).neighbours == neighbours_10
        assert world.index(1, 1).neighbours == neighbours_11

    # Ensure neighbours are correct in a 3x3 world
    def test_neighbours_3x3(self, generate_world):
        world = generate_world(xdim=3, ydim=3)

        # Define correct neighbours
        neighbours_11 = {'left': world.index(0, 1), 'right': world.index(2, 1),
                         'up': world.index(1, 2), 'down': world.index(1, 0)}

        assert world.index(1, 1).neighbours == neighbours_11


# Test the assignment of littoral neighbours
class TestLittoralNeighbours(object):
    # Ensure the littoral flag is applied correctly
    def test_littoral_assignment(self, generate_world_with_sea):
        world = generate_world_with_sea(xdim=3, ydim=3,
                                        sea_tiles=[(0, 0), (1, 2), (2, 2)])
        # Tiles next to sea at (0,0)
        assert world.index(1, 0).littoral is True
        assert world.index(0, 1).littoral is True

        # Tiles next to sea at (2,3) and (3,3)
        assert world.index(0, 2).littoral is True
        assert world.index(1, 1).littoral is True
        assert world.index(2, 1).littoral is True

        # Tiles not next to any sea
        assert world.index(2, 0).littoral is False

    # Ensure littoral neighbours are correct
    def test_littoral_neighbours(self, generate_world_with_sea):
        world = generate_world_with_sea(
            xdim=3, ydim=3,
            sea_tiles=[(0, 2), (2, 0), (2, 1), (2, 2)]
            )

        # Ensure littoral tiles have themselves as littoral neighbours
        assert LittoralNeighbour(
            world.index(0, 1), 0
            ) in world.index(0, 1).littoral_neighbours
        assert LittoralNeighbour(
            world.index(1, 0), 0
            ) in world.index(1, 0).littoral_neighbours
        assert LittoralNeighbour(
            world.index(1, 1), 0
            ) in world.index(1, 1).littoral_neighbours
        assert LittoralNeighbour(
            world.index(1, 2), 0
            ) in world.index(1, 2).littoral_neighbours

        # Ensure littoral neighbours on the same sea are correct
        assert LittoralNeighbour(
            world.index(1, 0), 1
            ) in world.index(1, 1).littoral_neighbours
        assert LittoralNeighbour(
            world.index(1, 0), 2
            ) in world.index(1, 2).littoral_neighbours

        assert LittoralNeighbour(
            world.index(1, 1), 1
            ) in world.index(1, 2).littoral_neighbours
        assert LittoralNeighbour(
            world.index(1, 1), 1
            ) in world.index(1, 0).littoral_neighbours

        assert LittoralNeighbour(
            world.index(1, 2), 1
            ) in world.index(1, 1).littoral_neighbours
        assert LittoralNeighbour(
            world.index(1, 2), 2
            ) in world.index(1, 0).littoral_neighbours

        assert LittoralNeighbour(
            world.index(0, 1), sqrt(2)
            ) in world.index(1, 2).littoral_neighbours

        assert LittoralNeighbour(
            world.index(1, 2), sqrt(2)
            ) in world.index(0, 1).littoral_neighbours

        # Ensure littoral neighbours with no sea connection are correct
        assert LittoralNeighbour(
            world.index(0, 1), 1
            ) in world.index(1, 1).littoral_neighbours
        assert LittoralNeighbour(
            world.index(0, 1), sqrt(2)
            ) in world.index(1, 0).littoral_neighbours

        assert LittoralNeighbour(
            world.index(1, 0), sqrt(2)
            ) in world.index(0, 1).littoral_neighbours

        assert LittoralNeighbour(
            world.index(1, 1), 1
            ) in world.index(0, 1).littoral_neighbours

    def test_littoral_neighbour_range(self, generate_world):
        world = generate_world(xdim=5, ydim=5)
        nsteps = 10

        assert (world.sea_attack_distance()
                == default_parameters.base_sea_attack_distance)

        for i in range(nsteps):
            world.step()

        assert world.sea_attack_distance() == (
            default_parameters.base_sea_attack_distance
            + default_parameters.sea_attack_increment
            * (nsteps)
            )

    def test_listtoral_neighbours_in_range(self, generate_world_with_sea):
        world = generate_world_with_sea(
            xdim=5, ydim=5,
            sea_tiles=[(2, 1), (2, 2), (2, 3), (2, 4),
                       (0, 4), (1, 4), (3, 4), (4, 4)]
            )

        tile = world.index(2, 0)
        huge_distance = 1000

        # Only the tile itself should be at range 0
        in_range = tile.littoral_neighbours_in_range(0)
        assert len(in_range) == 1
        assert LittoralNeighbour(tile, 0) in in_range

        # No more neighbours at range 1
        in_range = tile.littoral_neighbours_in_range(0)
        assert len(in_range) == 1

        # Two more neighbours at sqrt(2)
        in_range = tile.littoral_neighbours_in_range(2)
        assert len(in_range) == 3
        assert LittoralNeighbour(tile, 0) in in_range
        assert LittoralNeighbour(
            world.index(1, 1), sqrt(2)) in in_range
        assert LittoralNeighbour(
            world.index(3, 1), sqrt(2)) in in_range

        # Two more neighbours at sqrt(5)
        in_range = tile.littoral_neighbours_in_range(3)
        assert len(in_range) == 5
        assert LittoralNeighbour(tile, 0) in in_range
        assert LittoralNeighbour(
            world.index(1, 1), sqrt(2)) in in_range
        assert LittoralNeighbour(
            world.index(3, 1), sqrt(2)) in in_range
        assert LittoralNeighbour(
            world.index(1, 2), sqrt(5)) in in_range
        assert LittoralNeighbour(
            world.index(3, 2), sqrt(5)) in in_range

        # Two more neighbours at sqrt(10)
        in_range = tile.littoral_neighbours_in_range(3.6)
        assert len(in_range) == 7
        assert LittoralNeighbour(tile, 0) in in_range
        assert LittoralNeighbour(
            world.index(1, 1), sqrt(2)) in in_range
        assert LittoralNeighbour(
            world.index(3, 1), sqrt(2)) in in_range
        assert LittoralNeighbour(
            world.index(1, 2), sqrt(5)) in in_range
        assert LittoralNeighbour(
            world.index(3, 2), sqrt(5)) in in_range
        assert LittoralNeighbour(
            world.index(1, 3), sqrt(10)) in in_range
        assert LittoralNeighbour(
            world.index(3, 3), sqrt(10)) in in_range

        # All nine neighbours at sqrt(13)
        in_range = tile.littoral_neighbours_in_range(huge_distance)
        assert len(in_range) == 9
        assert LittoralNeighbour(tile, 0) in in_range
        assert LittoralNeighbour(
            world.index(1, 1), sqrt(2)) in in_range
        assert LittoralNeighbour(
            world.index(3, 1), sqrt(2)) in in_range
        assert LittoralNeighbour(
            world.index(1, 2), sqrt(5)) in in_range
        assert LittoralNeighbour(
            world.index(3, 2), sqrt(5)) in in_range
        assert LittoralNeighbour(
            world.index(1, 3), sqrt(10)) in in_range
        assert LittoralNeighbour(
            world.index(3, 3), sqrt(10)) in in_range
        assert LittoralNeighbour(
            world.index(0, 3), sqrt(13)) in in_range
        assert LittoralNeighbour(
            world.index(4, 3), sqrt(13)) in in_range


def test_destruction_of_empty_polities(generate_world):
    dimension = 5
    initial_polities = dimension**2
    world = generate_world(xdim=dimension, ydim=dimension)
    sea_attack = False

    attacker = world.polities[0].communities[0]
    # Initiate an attack guaranteed to succeed
    attacker.attack(attacker.neighbours['up'], default_parameters, sea_attack,
                    probability=1)
    world.prune_empty_polities()

    assert len(world.polities) == initial_polities - 1


@pytest.fixture(scope='class')
def world_disintegration(generate_world):
    dimension = 5
    params = generate_parameters(disintegration_base=1000)
    return generate_world(xdim=dimension, ydim=dimension, params=params)


@pytest.mark.incremental
class TestDisintegration():
    def test_disintegration_1(self, world_disintegration):
        world = world_disintegration
        for tile in world.tiles[1:4]:
            world.polities[0].transfer_community(tile)
        world.prune_empty_polities()

        for tile in world.tiles[5:]:
            world.polities[1].transfer_community(tile)
        world.prune_empty_polities()

        assert world.number_of_polities() == 2

    def test_disintegration_2(self, world_disintegration):
        world = world_disintegration
        world.disintegration()
        assert world.number_of_polities() == 25

    def test_disintegration_3(self, world_disintegration):
        world = world_disintegration
        assert all([state.size() == 1 for state in world.polities])


def test_step_increment(generate_world):
    world = generate_world(xdim=5, ydim=5)
    nsteps = 10

    for i in range(nsteps):
        world.step()

    assert world.step_number == nsteps


@pytest.fixture(scope='class')
def world_activation():
    return World.from_file(project_dir+'/test/data/test_activation.yml')


@pytest.mark.parametrize('step, number_active', [(0, 1), (900, 2), (1100, 3)])
def test_community_activation(world_activation, step, number_active):
    world_activation.step_number = step
    assert len(
        [tile for tile in world_activation.tiles
            if tile.is_active(world_activation.step_number) is True]
        ) == number_active


@pytest.mark.incremental
class TestReset():
    def test_initial(self, world_5x5):
        assert world_5x5.number_of_polities() == 25

    def test_community_transfer(self, world_5x5):
        world_5x5.polities[0].transfer_community(world_5x5.tiles[-1])
        world_5x5.prune_empty_polities()
        assert world_5x5.number_of_polities() == 24

    def test_reset(self, world_5x5):
        world_5x5.reset()
        assert world_5x5.number_of_polities() == 25


@pytest.mark.parametrize('yaml_file', ['missing_xdim.yml',
                                       'missing_ydim.yml',
                                       'missing_communities.yml'])
def test_missing_keys(yaml_file):
    with pytest.raises(MissingYamlKey):
        World.from_file(project_dir+'/test/data/'+yaml_file)


@pytest.fixture(scope='module')
def yaml_world():
    return World.from_file(project_dir+'/test/data/test_map_5x5.yml')


class TestYamlParsing():
    def test_total_tiles(self, yaml_world):
        assert yaml_world.total_tiles == 25

    def test_number_of_polities(self, yaml_world):
        assert yaml_world.number_of_polities() == 22

    @pytest.mark.parametrize('dimension, value', [('xdim', 5),
                                                  ('ydim', 5)])
    def test_dimensions(self, yaml_world, dimension, value):
        assert yaml_world.__getattribute__(dimension) == value

    @pytest.mark.parametrize('coordinate, value', [
        ((4, 4), terrain.steppe),
        ((3, 4), terrain.desert),
        ((4, 0), terrain.sea),
        ((1, 0), terrain.agriculture)
        ])
    def test_terrain(self, yaml_world, coordinate, value):
        assert yaml_world.index(*coordinate).terrain == value

    @pytest.mark.parametrize('coordinate, elevation', [((2, 2), 5),
                                                       ((3, 1), 3),
                                                       ((3, 0), 1)])
    def test_elevation(self, yaml_world, coordinate, elevation):
        assert yaml_world.index(*coordinate).elevation == elevation

    @pytest.mark.parametrize('coordinate, period', [((1, 0), period.agri1),
                                                    ((2, 0), period.agri2),
                                                    ((4, 1), period.agri3)])
    def test_active_from(self, yaml_world, coordinate, period):
        assert yaml_world.index(*coordinate).period == period
