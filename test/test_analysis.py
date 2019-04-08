from guard import analysis
import numpy as np
import os
import pytest

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope='class')
def imperial_density(world_5x5):
    date_range = analysis.DateRange(-1500, 1500)
    imperial_density = analysis.ImperialDensity(world_5x5,
                                                date_ranges=[date_range])
    return imperial_density


@pytest.mark.incremental
class TestImperialDensitySummation():
    def test_initialisation(self, imperial_density):
        imperial_density.sample()
        date_range = imperial_density.date_ranges[0]
        world = imperial_density.world
        assert np.all(imperial_density.data[date_range]
                      == np.zeros([world.xdim, world.ydim]))

        def test_summation_1(self, imperial_density):
            date_range = imperial_density.date_ranges[0]
            world = imperial_density.world
            # Create a large (size >= 10) polity by adding communities in
            # coordinates (0:2,0:4) to the polity at(4,4)
            self.test_density = np.zeros([5, 5])
            self.test_density[4][4] = 1.
            for x in range(2):
                for y in range(5):
                    world.index(4, 4).polity.add_community(world.index(x, y))
                    self.test_density[x, y] = 1.
            imperial_density.sample()
            assert np.all(imperial_density.data[date_range]
                          == self.test_density)

        def test_summation_2(self, imperial_density):
            date_range = imperial_density.date_ranges[0]
            imperial_density.sample()
            assert np.all(imperial_density.data[date_range]
                          == 2.0*self.test_density)


@pytest.fixture(scope='class')
def example_cities(world_5x5):
    cities = analysis.CitiesPopulation(
        world_5x5, project_dir + '/test/data/test_cities.yml'
        )
    return cities


@pytest.mark.parametrize('era,coordinate,population', [
    ('0-500AD', (0, 0), 42000),
    ('1000BC-0', (0, 0), 42000),
    ('1400AD-1500AD', (2, 4), 400000)
    ])
def test_population_data(example_cities, era, coordinate, population):
    assert example_cities.data[era][coordinate] == population


@pytest.mark.parametrize('accumulator_class', [analysis.AccumulatorBase,
                                               analysis.ImperialDensity,
                                               analysis.AttackEvents])
def test_mean_accumulator(world_5x5, daterange_0_100AD, accumulator_class):
    # Create a set of accumulators and populate with random data
    accumulators = [
        accumulator_class(world_5x5, [daterange_0_100AD])
        for i in range(5)
        ]

    # Determine the mean
    mean_data = np.zeros([5, 5])
    for accumulator in accumulators:
        data = np.random.random([5, 5])
        accumulator.data[daterange_0_100AD] = data
        mean_data += data
    mean_data = mean_data / 5.

    mean = analysis.AccumulatorBase.mean(accumulators)
    assert np.all(mean.data[daterange_0_100AD] == mean_data)
