from . import context
from . fixtures import default_parameters
from guard import world, community
from numpy import sqrt
import pytest

@pytest.fixture
def generate_world():
    def _generate_world(xdim,ydim):
        map_ = world.World(xdim,ydim)
        map_.create_flat_agricultural_world()
        return map_
    return _generate_world

@pytest.fixture
def generate_world_with_sea():
    def _generate_world(xdim,ydim,sea_tiles):
        map_ = world.World(xdim,ydim)
        map_.create_flat_agricultural_world()

        for coordinate in sea_tiles:
            x,y = coordinate
            map_.index(x,y).terrain = community.Terrain.sea

        map_.set_littoral_tiles()
        map_.set_littoral_neighbours()
        return map_
    return _generate_world

# Test the assignment of neighbours
class TestNeighbours(object):
    # Ensure neighbours are correct in a 2x2 world
    def test_neighbours_2x2(self, generate_world):
        map_ = generate_world(xdim=2,ydim=2)

        # Define correct neighbours
        neighbours_00 = {'left':None, 'right':map_.index(1,0), 'up':map_.index(0,1), 'down':None}
        neighbours_01 = {'left':None, 'right':map_.index(1,1), 'up':None, 'down':map_.index(0,0)}
        neighbours_10 = {'left':map_.index(0,0), 'right':None, 'up':map_.index(1,1), 'down':None}
        neighbours_11 = {'left':map_.index(0,1), 'right':None, 'up':None, 'down':map_.index(1,0)}

        assert map_.index(0,0).neighbours == neighbours_00
        assert map_.index(0,1).neighbours == neighbours_01
        assert map_.index(1,0).neighbours == neighbours_10
        assert map_.index(1,1).neighbours == neighbours_11

    # Ensure neighbours are correct in a 3x3 world
    def test_neighbours_3x3(self, generate_world):
        map_ = generate_world(xdim=3,ydim=3)

        # Define correct neighbours
        neighbours_11 = {'left':map_.index(0,1), 'right':map_.index(2,1), \
                'up':map_.index(1,2), 'down':map_.index(1,0)}

        assert map_.index(1,1).neighbours == neighbours_11

# Test the assignment of littoral neighbours
class TestLittoralNeighbours(object):
    # Ensure the littoral flag is applied correctly
    def test_littoral_assignment(self, generate_world_with_sea):
        map_ = generate_world_with_sea(xdim=3, ydim=3, \
                sea_tiles=[(0,0), (1,2), (2,2)])
        # Tiles next to sea at (0,0)
        assert map_.index(1,0).littoral == True
        assert map_.index(0,1).littoral == True

        # Tiles next to sea at (2,3) and (3,3)
        assert map_.index(0,2).littoral == True
        assert map_.index(1,1).littoral == True
        assert map_.index(2,1).littoral == True

        # Tiles not next to any sea
        assert map_.index(2,0).littoral == False

    # Ensure littoral neighbours are correct
    def test_littoral_neighbours(self, generate_world_with_sea):
        map_ = generate_world_with_sea(xdim=3, ydim=3, \
                sea_tiles = [(0,2), (2,0), (2,1), (2,2)])

        # Ensure littoral tiles have themselves as littoral neighbours
        assert community.LittoralNeighbour(map_.index(0,1), 0) in map_.index(0,1).littoral_neighbours
        assert community.LittoralNeighbour(map_.index(1,0), 0) in map_.index(1,0).littoral_neighbours
        assert community.LittoralNeighbour(map_.index(1,1), 0) in map_.index(1,1).littoral_neighbours
        assert community.LittoralNeighbour(map_.index(1,2), 0) in map_.index(1,2).littoral_neighbours

        # Ensure littoral neighbours on the same sea are correct
        assert community.LittoralNeighbour(map_.index(1,0), 1) in map_.index(1,1).littoral_neighbours
        assert community.LittoralNeighbour(map_.index(1,0), 2) in map_.index(1,2).littoral_neighbours

        assert community.LittoralNeighbour(map_.index(1,1), 1) in map_.index(1,2).littoral_neighbours
        assert community.LittoralNeighbour(map_.index(1,1), 1) in map_.index(1,0).littoral_neighbours

        assert community.LittoralNeighbour(map_.index(1,2), 1) in map_.index(1,1).littoral_neighbours
        assert community.LittoralNeighbour(map_.index(1,2), 2) in map_.index(1,0).littoral_neighbours

        assert community.LittoralNeighbour(map_.index(0,1), sqrt(2)) in map_.index(1,2).littoral_neighbours

        assert community.LittoralNeighbour(map_.index(1,2), sqrt(2)) in map_.index(0,1).littoral_neighbours

        # Ensure littoral neighbours with no sea connection are correct
        assert community.LittoralNeighbour(map_.index(0,1), 1) in map_.index(1,1).littoral_neighbours
        assert community.LittoralNeighbour(map_.index(0,1), sqrt(2)) in map_.index(1,0).littoral_neighbours

        assert community.LittoralNeighbour(map_.index(1,0), sqrt(2)) in map_.index(0,1).littoral_neighbours

        assert community.LittoralNeighbour(map_.index(1,1), 1) in map_.index(0,1).littoral_neighbours

    def test_littoral_neighbour_range(self, default_parameters, generate_world):
        params = default_parameters
        map_ = generate_world(xdim=5,ydim=5)
        nsteps = 10

        assert map_.sea_attack_distance() == params.base_sea_attack_distance

        for i in range(nsteps):
            map_.step()

        assert map_.sea_attack_distance() == params.base_sea_attack_distance + \
                params.sea_attack_increment * (nsteps)

    def test_listtoral_neighbours_in_range(self, generate_world_with_sea):
        map_ = generate_world_with_sea(xdim=5, ydim=5, \
                sea_tiles = [(2,1), (2,2), (2,3), (2,4), (0,4), (1,4), (3,4), (4,4)])

        tile = map_.index(2,0)
        huge_distance = 1000

        # Only the tile itself should be at range 0
        in_range = tile.littoral_neighbours_in_range(0)
        assert len(in_range) == 1
        assert community.LittoralNeighbour(tile,0) in in_range

        # No more neighbours at range 1
        in_range = tile.littoral_neighbours_in_range(0)
        assert len(in_range) == 1

        # Two more neighbours at sqrt(2)
        in_range = tile.littoral_neighbours_in_range(2)
        assert len(in_range) == 3
        assert community.LittoralNeighbour(tile,0) in in_range
        assert community.LittoralNeighbour(map_.index(1,1),sqrt(2)) in in_range
        assert community.LittoralNeighbour(map_.index(3,1),sqrt(2)) in in_range

        # Two more neighbours at sqrt(5)
        in_range = tile.littoral_neighbours_in_range(3)
        assert len(in_range) == 5
        assert community.LittoralNeighbour(tile,0) in in_range
        assert community.LittoralNeighbour(map_.index(1,1),sqrt(2)) in in_range
        assert community.LittoralNeighbour(map_.index(3,1),sqrt(2)) in in_range
        assert community.LittoralNeighbour(map_.index(1,2),sqrt(5)) in in_range
        assert community.LittoralNeighbour(map_.index(3,2),sqrt(5)) in in_range

        # Two more neighbours at sqrt(10)
        in_range = tile.littoral_neighbours_in_range(3.6)
        assert len(in_range) == 7
        assert community.LittoralNeighbour(tile,0) in in_range
        assert community.LittoralNeighbour(map_.index(1,1),sqrt(2)) in in_range
        assert community.LittoralNeighbour(map_.index(3,1),sqrt(2)) in in_range
        assert community.LittoralNeighbour(map_.index(1,2),sqrt(5)) in in_range
        assert community.LittoralNeighbour(map_.index(3,2),sqrt(5)) in in_range
        assert community.LittoralNeighbour(map_.index(1,3),sqrt(10)) in in_range
        assert community.LittoralNeighbour(map_.index(3,3),sqrt(10)) in in_range

        # All nine neighbours at sqrt(13)
        in_range = tile.littoral_neighbours_in_range(huge_distance)
        assert len(in_range) == 9
        assert community.LittoralNeighbour(tile,0) in in_range
        assert community.LittoralNeighbour(map_.index(1,1),sqrt(2)) in in_range
        assert community.LittoralNeighbour(map_.index(3,1),sqrt(2)) in in_range
        assert community.LittoralNeighbour(map_.index(1,2),sqrt(5)) in in_range
        assert community.LittoralNeighbour(map_.index(3,2),sqrt(5)) in in_range
        assert community.LittoralNeighbour(map_.index(1,3),sqrt(10)) in in_range
        assert community.LittoralNeighbour(map_.index(3,3),sqrt(10)) in in_range
        assert community.LittoralNeighbour(map_.index(0,3),sqrt(13)) in in_range
        assert community.LittoralNeighbour(map_.index(4,3),sqrt(13)) in in_range


def test_destruction_of_empty_polities(default_parameters, generate_world):
    params = default_parameters
    dimension = 5
    initial_polities = dimension**2
    map_ = generate_world(xdim=dimension,ydim=dimension)

    attacker = map_.polities[0].communities[0]
    # Initiate an attack guaranteed to succeed
    attacker.attack(attacker.neighbours['up'], params, probability=1)
    map_.prune_empty_polities()

    assert len(map_.polities) == initial_polities - 1

def test_step(generate_world):
    map_ = generate_world(xdim=5,ydim=5)
    map_.step()

def test_step_increment(generate_world):
    map_ = generate_world(xdim=5,ydim=5)
    nsteps = 10

    for i in range(nsteps):
        map_.step()

    assert map_.step_number == nsteps

def test_community_activation(generate_world):
    map_ = world.World(from_file=context.project_dir+'/test/data/test_activation.yml')

    assert len([tile for tile in map_.tiles if tile.active == True]) == 1

    map_.step = 900
    map_.activate()
    assert len([tile for tile in map_.tiles if tile.active == True]) == 2

    map_.step = 1100
    map_.activate()
    assert len([tile for tile in map_.tiles if tile.active == True]) == 3

def test_yaml_parsing():
    map_ = world.World(from_file=context.project_dir+'/data/old_world.yml')

    example_tile = map_.index(29,89)
    assert example_tile.terrain == community.Terrain.steppe
    assert example_tile.elevation == 98

    assert map_.total_tiles == 13915
    assert map_.number_of_polities() == 2647

    assert map_.xdim == 115
    assert map_.ydim == 121

    map_.step()
