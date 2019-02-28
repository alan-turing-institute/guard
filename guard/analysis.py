from . import community, terrain
from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np
import pickle
from scipy import ndimage, stats
import yaml

# How many communities a polity requires before it is considered large and is
# recorded
_LARGE_POLITY_THRESHOLD = 10

# Colours
_SEA = np.array([0.25098039, 0.57647059, 0.92941176, 1.])
_DESERT = np.array([0.7372549 , 0.71372549, 0.25098039, 1.])
_STEPPE = np.array([0.42745098, 0.        , 0.75686275, 1.])

# A range of dates, used to control sampling periods
class DateRange(object):
    def __init__(self, start_year, end_year):
        assert start_year < end_year
        self.start_year = start_year
        self.end_year = end_year
        self.label = self._create_label()

    @classmethod
    def from_string(cls,string):
        # Get dates in AD/BC format from string
        dates = string.split('-')

        # Change into integer representation
        for i,date in enumerate(dates):
            if date == '0':
                dates[i] = 0
            elif date[-2:] == 'BC':
                dates[i] = int(date[:-2])*-1
            else:
                dates[i] = int(date[:-2])

        return cls(*dates)

    def _create_label(self):
        if self.start_year < 0:
            label = '{:d}BC-'.format(abs(self.start_year))
        elif self.start_year == 0:
            label = '{:d}-'.format(abs(self.start_year))
        else:
            label = '{:d}AD-'.format(abs(self.start_year))

        if self.end_year < 0:
            label += '{:d}BC'.format(abs(self.end_year))
        elif self.end_year == 0:
            label += '{:d}'.format(abs(self.end_year))
        else:
            label += '{:d}AD'.format(abs(self.end_year))

        return label

    def __str__(self):
        return self.label

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        if isinstance(other, DateRange):
            return self.start_year == other.start_year and self.end_year == other.end_year
        elif isinstance(other, str):
            return self.label == other
        else:
            return False

    # Determine whether a year is within the date range
    def is_within(self, year):
        if year >= self.start_year and year < self.end_year:
            return True
        else:
            return False

# Date ranges of cities data
cities_date_ranges = [DateRange(-2500,-1000),
        DateRange(-1000,0),
        DateRange(0,500),
        DateRange(500,1000),
        DateRange(700,850),
        DateRange(850,1000),
        DateRange(1000,1100),
        DateRange(1100,1200),
        DateRange(1200,1300),
        DateRange(1300,1400),
        DateRange(1400,1500)]

# Default date ranges for imperial density eras
imperial_density_date_ranges = [DateRange(-1500,-500),
        DateRange(-500,500),
        DateRange(500,1500)]

class InvalidDateRange(Exception):
    pass

# Contain and analyse imperial density information
class ImperialDensity(object):
    def __init__(self, world, date_ranges=imperial_density_date_ranges):
        self.world = world
        self.date_ranges = date_ranges

        self.imperial_density = {era: np.zeros([world.xdim, world.ydim]) for era in date_ranges}
        self.samples = {era: 0 for era in date_ranges}

    def sample(self):
        # Create list of tiles to sample, only tiles with agriculture
        agricultural_tiles = [tile for tile in self.world.tiles if tile.terrain.polity_forming]
        agricultural_tiles[:] = [tile for tile in agricultural_tiles \
                if tile.is_active(self.world.step_number)]

        # Create list of eras to add imperial density to, only those that
        # contain the current year
        year = self.world.year()
        active_eras = [era for era in self.date_ranges if era.is_within(year)]
        for tile in agricultural_tiles:
            if tile.polity.size() > _LARGE_POLITY_THRESHOLD:
                for era in active_eras:
                    self.imperial_density[era][tile.position[0], tile.position[1]] += 1.
                    self.samples[era] += 1

    def export(self, normalise=False, highlight_desert=False, highlight_steppe=False):
        for era in self.date_ranges:
            fig, ax, colour_map = _init_world_plot()
            plot_data = self.imperial_density[era]
            # Express data as RGBA values
            if normalise:
                plot_data = plot_data / np.max(plot_data)
            else:
                plot_data = plot_data / self.samples[era]
            plot_data = colour_map(plot_data)
            plot_data = _colour_special_tiles(plot_data, self.world, highlight_desert, highlight_steppe)

            im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
            fig.colorbar(im)
            fig.savefig('imperial_density_{}.pdf'.format(era), format='pdf')

    def dump(self, outfile):
        with open(outfile, 'wb') as picklefile:
            pickle.dump({str(key): value for key,value in self.imperial_density.items()},
                    picklefile)

    def load(self, infile):
        with open(infile, 'rb') as picklefile:
            data = pickle.load(picklefile)
            for era in self.imperial_density.items():
                if era in data.keys():
                    self.imperial_density[era] = data[era]
                else:
                    raise InvalidDateRange("Date range {} in file {} does not match any in ImperialDensity object".format(era, infile))

# Establish the figure, axis and colourmap for a standard map plot
def _init_world_plot():
        # Initialise figure and axis
        fig = plt.figure()
        ax = fig.subplots()

        # Hide axes ticks
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        # Colour map
        colour_map = plt.get_cmap('RdYlGn').reversed()

        return fig, ax, colour_map

# Colour sea, steppe and desert tiles distinctly
def _colour_special_tiles(rgba_data, world, highlight_desert=False, highlight_steppe=False):
        # Colour sea and optionally desert
        for tile in world.tiles:
            x, y = tile.position[0], tile.position[1]
            if tile.terrain is terrain.sea:
                rgba_data[x][y] = _SEA
            elif tile.terrain is terrain.desert:
                if highlight_desert:
                    rgba_data[x][y] = _DESERT
            elif tile.terrain is terrain.steppe:
                if highlight_steppe:
                    rgba_data[x][y] = _STEPPE
        return rgba_data

# Plot a heatmap of military technology level
def plot_military_techs(world, highlight_desert=False, highlight_steppe=False):
        fig, ax, colour_map = _init_world_plot()

        # Prepare data
        plot_data = np.array(
                [ [world.index(x,y).total_military_techs() for y in range(world.ydim)]
                    for x in range(world.xdim)])
        plot_data = plot_data / world.params.n_military_techs

        # Generate rgba data
        plot_data = colour_map(plot_data)
        plot_data = _colour_special_tiles(plot_data, world, highlight_desert, highlight_steppe)

        im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
        fig.colorbar(im)
        fig.savefig('military_techs_{:04d}.pdf'.format(world.step_number), format='pdf')

# Plot a heatmap of ultrasocietal traits
def plot_ultrasocietal_traits(world, highlight_desert=False, highlight_steppe=False):
        fig, ax, colour_map = _init_world_plot()

        # Prepare data
        plot_data = np.array(
                [ [world.index(x,y).total_ultrasocietal_traits() for y in range(world.ydim)]
                    for x in range(world.xdim)])
        plot_data = plot_data / world.params.n_ultrasocietal_traits

        # Generate rgba data
        plot_data = colour_map(plot_data)
        plot_data = _colour_special_tiles(plot_data, world, highlight_desert, highlight_steppe)

        im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
        fig.colorbar(im)
        fig.savefig('ultrasocietal_traits_{:04d}.pdf'.format(world.step_number), format='pdf')

# Plot which regions currently have agriculture
def plot_active_agriculture(world, highlight_desert=False, highlight_steppe=False):
        fig, ax, colour_map = _init_world_plot()

        # Prepare data
        active_tiles = [tile for tile in world.tiles if tile.is_active(world.step_number) == True]
        plot_data = np.zeros([world.xdim, world.ydim])
        for tile in active_tiles:
            x, y = tile.position
            plot_data[x][y] = 1.

        # Generate rgba data
        plot_data = colour_map(plot_data)
        plot_data = _colour_special_tiles(plot_data, world, highlight_desert, highlight_steppe)

        im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
        fig.colorbar(im)
        fig.savefig('active_{:04d}.pdf'.format(world.step_number), format='pdf')

# Analyse population data of cities
class CitiesPopulation(object):
    # Flag for pruning values before regression
    _REMOVE_FLAG = -5

    def __init__(self, world, data_file, date_ranges=cities_date_ranges):
        self.world = world
        self.date_ranges = date_ranges

        # Population in each tile for each era
        self.population = {era: np.zeros([world.xdim, world.ydim]) for era in date_ranges}

        # Sum populations from cities and eras
        with open(data_file, 'r') as yamlfile:
            cities_data = yaml.load(yamlfile)

            for city in cities_data:
                for era in date_ranges:
                    try:
                        self.population[era][city['x'],city['y']] += city['population'][era]
                    except KeyError:
                        raise InvalidDateRange("Date range {} not in city data\n\t{}".format(era,city))

    def plot_population_heatmap(self, blur=False):
        for era in self.date_ranges:
            fig, ax, colour_map = _init_world_plot()

            plot_data = self.population[era]

            if blur:
                plot_data = ndimage.gaussian_filter(plot_data, sigma=blur)
            # Normalise
            vmax = np.max(plot_data)
            plot_data = plot_data/vmax

            # Create rgb data
            plot_data = colour_map(plot_data)
            plot_data = _colour_special_tiles(plot_data, self.world)


            im = ax.imshow(np.rot90(plot_data), cmap=colour_map, vmax=vmax, vmin=0)
            fig.colorbar(im)
            fig.savefig('population_{}.pdf'.format(era))

    def correlate(self, imperial_density, blur=False, cumulative=False):
        assert self.world is imperial_density.world
        common_eras = [era for era in self.date_ranges if era in imperial_density.date_ranges]

        if cumulative:
            cumulative_impd = np.zeros([self.world.xdim, self.world.ydim])

        # Figure and axes
        fig, ax = plt.subplots()
        # Correlate population and imperial density between eras in both
        # cities data and imperial denisty
        for era in common_eras:
            # Axes setup
            ax.set_xlabel=('Imperial Density')
            ax.set_ylabel=('Population')
            ax.set_title(str(era))

            impd = imperial_density.imperial_density[era]
            if cumulative:
                impd += cumulative_impd
                cumulative_impd = impd
            pop = self.population[era]

            if blur:
                pop = ndimage.gaussian_filter(pop, sigma=blur)

            # Don't compare sea tiles
            for tile in self.world.tiles:
                if tile.terrain == terrain.sea:
                    x, y = tile.position[0], tile.position[1]
                    impd[x,y] = self._REMOVE_FLAG
                    pop[x,y] = self._REMOVE_FLAG

            impd = impd.flatten()
            pop = pop.flatten()

            if blur == False:
                # Only compare tiles with population data
                for index in range(len(impd)):
                    if pop[index] == 0:
                        impd[index] = self._REMOVE_FLAG
                        pop[index] = self._REMOVE_FLAG

            # Remove flagged elements
            impd = np.array([elem for elem in impd if elem != self._REMOVE_FLAG])
            pop = np.array([elem for elem in pop if elem != self._REMOVE_FLAG])

            linreg = stats.linregress(impd,pop)

            ax.plot(impd, pop, 'x')
            ax.plot(impd, impd*linreg.slope + linreg.intercept)
            ax.text(0, 1, str(linreg.rvalue), transform=ax.transAxes)

            fig.tight_layout()
            fig.savefig('ipd_pop_{}.pdf'.format(era), format='pdf')
            ax.cla()

# Base class for accumulators of tile wise data
class AccumulatorBase(object):
    _prefix = None

    def __init__(self, world, date_ranges=None):
        self.world = world
        self.date_ranges = date_ranges
        self.data = {era: np.zeros([world.xdim, world.ydim]) for era in date_ranges}

    @classmethod
    def from_file(cls, world, data_file):
        date_ranges = []
        data = {}
        with open(data_file, 'rb') as picklefile:
            data_dict = pickle.load(picklefile)
            for era, value in data_dict.items():
                daterange = DateRange.from_string(era)
                date_ranges.append(daterange)
                data[daterange] = value

            accumulator = cls(world, date_ranges)
            accumulator.data = data
        return accumulator

    def sample(self):
        pass

    def plot(self, highlight_desert=False, highlight_steppe=False):
        for era in self.date_ranges:
            fig, ax, colour_map = _init_world_plot()
            plot_data = self.data[era]

            plot_data = plot_data / np.max(plot_data)
            plot_data = colour_map(plot_data)
            plot_data = _colour_special_tiles(plot_data, self.world, highlight_desert, highlight_steppe)
            im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
            fig.colorbar(im)
            fig.savefig('{}_{}.pdf'.format(self._prefix,era), format='pdf')

    def dump(self, outfile):
        with open(outfile, 'wb') as picklefile:
            pickle.dump(
                {str(key): value for key,value in self.data.items()},
                picklefile)

# Enumerate and analyse attack frequency in each tile
class AttackEvents(AccumulatorBase):
    _prefix = 'attack_frequency'

    def __init__(self, world, date_ranges=None):
        super().__init__(world, date_ranges)

    def sample(self, tile):
        year = self.world.year()
        active_eras = [era for era in self.date_ranges if era.is_within(year)]
        for era in active_eras:
            self.attacks[era][tile.position[0], tile.position[1]] += 1.

# Base class for correlated data projected onto the map with tilewise properties
class CorrelateBase(object):
    _prefix = None
    _REMOVE_FLAG = -5

    def __init__(self, world, date_ranges):
        self.world = world
        self.date_ranges = date_ranges
        self.data = {era: np.zeros([world.xdim, world.ydim]) for era in date_ranges}

    # Draw a heatmap of the data projected onto the map
    def plot_heatmap(self, blur=False):
        for era in self.date_ranges:
            fig, ax, colour_map = _init_world_plot()

            plot_data = self.data[era]

            if blur:
                plot_data = ndimage.gaussian_filter(plot_data, sigma=blur)
            # Normalise
            vmax = np.max(plot_data)
            plot_data = plot_data/vmax

            # Create rgb data
            plot_data = colour_map(plot_data)
            plot_data = _colour_special_tiles(plot_data, self.world)


            im = ax.imshow(np.rot90(plot_data), cmap=colour_map, vmax=vmax, vmin=0)
            fig.colorbar(im)
            fig.savefig('{}_{}.pdf'.format(self._prefix,era))

    # Perform a linear regression of the accumaltors date against the
    # correlators data and plot the result
    def correlate(self, accumulator, blur=False, cumulative=False):
        assert self.world is accumulator.world
        common_eras = [era for era in self.date_ranges if era in accumulator.date_ranges]

        if cumulative:
            cumulative = np.zeros([self.world.xdim, self.world.ydim])

        # Figure and axes
        fig, ax = plt.subplots()
        # Correlate population and imperial density between eras in both
        # cities data and imperial denisty
        for era in common_eras:
            # Axes setup
            ax.set_xlabel=('Imperial Density')
            ax.set_ylabel=('Population')
            ax.set_title(str(era))

            comparison = accumulator.data[era]
            if cumulative:
                comparison += cumulative
                cumulative = comparison
            data = self.data[era]

            if blur:
                data = ndimage.gaussian_filter(data, sigma=blur)

            # Don't compare sea tiles
            for tile in self.world.tiles:
                if tile.terrain == terrain.sea:
                    x, y = tile.position[0], tile.position[1]
                    comparison[x,y] = self._REMOVE_FLAG
                    data[x,y] = self._REMOVE_FLAG

            comparison = comparison.flatten()
            data = data.flatten()

            if blur == False:
                # Only compare tiles with data
                for index in range(len(comparison)):
                    if data[index] == 0:
                        comparison[index] = self._REMOVE_FLAG
                        data[index] = self._REMOVE_FLAG

            # Remove flagged elements
            comparison = np.array([elem for elem in comparison if elem != self._REMOVE_FLAG])
            data = np.array([elem for elem in data if elem != self._REMOVE_FLAG])

            # Linear regression
            linreg = stats.linregress(comparison,data)

            # Scatter plot of data against comparison with best fit line
            ax.plot(comparison, data, 'x')
            ax.plot(comparison, comparison*linreg.slope + linreg.intercept)
            ax.text(0, 1, str(linreg.rvalue), transform=ax.transAxes)

            fig.tight_layout()
            fig.savefig('{}_correlation_{}.pdf'.format(self._prefix,era), format='pdf')
            ax.cla()

# Battles corralatable class
class Battles(CorrelateBase):
    _prefix = 'battles'
    def __init__(self, world, date_range, data_file):
        super().__init__(world, date_range)

        # Sum battles from data file
        with open(data_file, 'r') as yamlfile:
            battles = yaml.load(yamlfile)

            for battle in battles:
                for era in self.date_ranges:
                    if era.is_within(battle['year']):
                        self.data[era][battle['x'], battle['y']] += 1.

