from . import context
from guard import world
import pytest

@pytest.fixture
def simple_2x2_world():
    map_ = world.World(xdim=2,ydim=2)
    map_.create_flat_agricultural_world()

    return map_

@pytest.fixture
def simple_3x3_world():
    map_ = world.World(xdim=3,ydim=3)
    map_.create_flat_agricultural_world()

    return map_

# Test the assignment of neighbours
class TestNeighbours(object):
    # Ensure neighbours are correct in a 2x2 world
    def test_neighbours_2x2(self,simple_2x2_world):
        map_ = simple_2x2_world

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
    def test_neighbours_3x3(self,simple_3x3_world):
        map_ = simple_3x3_world

        # Define correct neighbours
        neighbours_11 = {'left':map_.index(0,1), 'right':map_.index(2,1), \
                'up':map_.index(1,2), 'down':map_.index(1,0)}

        assert map_.index(1,1).neighbours == neighbours_11
