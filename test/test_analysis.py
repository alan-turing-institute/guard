from . import context
from . fixtures import default_parameters, generate_world
from guard import world, analysis
import numpy as np

def test_imperial_density_summation(generate_world):
    map_ = world.World(from_file=context.project_dir+'/test/data/test_imperial_density.yml')
    imperial_density = analysis.ImperialDensity(map_)

    # Ensure imperial density is zero with no large polities
    imperial_density.sample()
    assert np.all(imperial_density.imperial_density == np.zeros([map_.xdim,map_.ydim]))

    # Create a large (size >= 10) polity by adding communities in coordinates 
    # (0:2,0:4) to the polity at(4,4)
    test_density = np.zeros([5,5])
    test_density[4][4] = 1.
    for x in range(2):
        for y in range(5):
            map_.index(4,4).polity.add_community(map_.index(x,y))
            test_density[x,y] = 1.
    imperial_density.sample()
    assert np.all(imperial_density.imperial_density == test_density)

    # Test one more iteration with the same polities
    imperial_density.sample()
    assert np.all(imperial_density.imperial_density == 2.0*test_density)

class TestDateRange(object):
    def test_label(self):
        date_range = analysis.DateRange(-5,5)

        assert str(date_range) == '5BC-5AD'

    def test_equivalence(self):
        date_range = analysis.DateRange(-5,5)
        date_range2 = analysis.DateRange(-5,5)

        assert date_range == date_range2
        assert date_range == '5BC-5AD'

    def test_hash(self):
        date_range = analysis.DateRange(0,500)
        test_dict = {date_range: 'test'}

        assert test_dict['0-500AD'] == 'test'

def test_population_data(generate_world):
    map_ = world.World(from_file=context.project_dir+'/test/data/test_imperial_density.yml')
    cities = analysis.CitiesPopulation(map_, context.project_dir+'/test/data/test_cities.yml')

    assert cities.population['0-500AD'][0,0] == 42000
    assert cities.population['1000BC-0'][0,0] == 42000
    assert cities.population['1400AD-1500AD'][2,4] == 400000
