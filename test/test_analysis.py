from guard import world, analysis
import numpy as np
import os

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def test_imperial_density_summation(world_5x5):
    map_ = world_5x5
    date_range = analysis.DateRange(-1500, 1500)
    imperial_density = analysis.ImperialDensity(map_, date_ranges=[date_range])

    # Ensure imperial density is zero with no large polities
    imperial_density.sample()
    assert np.all(
        imperial_density.data[date_range] == np.zeros([map_.xdim, map_.ydim])
        )

    # Create a large (size >= 10) polity by adding communities in coordinates
    # (0:2,0:4) to the polity at(4,4)
    test_density = np.zeros([5, 5])
    test_density[4][4] = 1.
    for x in range(2):
        for y in range(5):
            map_.index(4, 4).polity.add_community(map_.index(x, y))
            test_density[x, y] = 1.
    imperial_density.sample()
    assert np.all(imperial_density.data[date_range] == test_density)

    # Test one more iteration with the same polities
    imperial_density.sample()
    assert np.all(imperial_density.data[date_range] == 2.0*test_density)


def test_population_data(generate_world):
    map_ = world.World(
        from_file=project_dir + '/test/data/test_map_5x5.yml'
        )
    cities = analysis.CitiesPopulation(
        map_, project_dir + '/test/data/test_cities.yml'
        )

    assert cities.data['0-500AD'][0, 0] == 42000
    assert cities.data['1000BC-0'][0, 0] == 42000
    assert cities.data['1400AD-1500AD'][2, 4] == 400000
