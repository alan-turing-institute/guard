from . import context
from . fixtures import default_parameters
from guard import world
import pytest

@pytest.fixture
def generate_world():
    def _generate_world(xdim,ydim):
        map_ = world.World(xdim,ydim)
        map_.create_flat_agricultural_world()
        return map_
    return _generate_world

# Test the assignment of neighbours
class TestNeighbours(object):
    # Ensure neighbours are correct in a 2x2 world
    def test_neighbours_2x2(self,generate_world):
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
    def test_neighbours_3x3(self,generate_world):
        map_ = generate_world(xdim=3,ydim=3)

        # Define correct neighbours
        neighbours_11 = {'left':map_.index(0,1), 'right':map_.index(2,1), \
                'up':map_.index(1,2), 'down':map_.index(1,0)}

        assert map_.index(1,1).neighbours == neighbours_11

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

