from . import terrain
from .daterange import (DateRange, InvalidDateRange,
                        imperial_density_date_ranges, cities_date_ranges)
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
_DESERT = np.array([0.7372549, 0.71372549, 0.25098039, 1.])
_STEPPE = np.array([0.42745098, 0., 0.75686275, 1.])


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
def _colour_special_tiles(rgba_data, world, highlight_desert=False,
                          highlight_steppe=False, area=None):
    if area is None:
        xmin, xmax = 0, world.xdim
        ymin, ymax = 0, world.ydim
    else:
        xmin, xmax, ymin, ymax = area

    # Colour sea and optionally desert
    for tile in world.tiles:
        x, y = tile.position[0], tile.position[1]
        if x < xmax and x >= xmin:
            if y < ymax and y >= ymin:
                x -= xmin
                y -= ymin
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
    plot_data = np.array([
        [world.index(x, y).total_military_techs()
         for y in range(world.ydim)] for x in range(world.xdim)
        ])
    plot_data = plot_data / world.params.n_military_techs

    # Generate rgba data
    plot_data = colour_map(plot_data)
    plot_data = _colour_special_tiles(plot_data, world, highlight_desert,
                                      highlight_steppe)

    im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
    fig.colorbar(im)
    fig.savefig('military_techs_{:04d}.pdf'.format(world.step_number),
                format='pdf')


# Plot a heatmap of ultrasocietal traits
def plot_ultrasocietal_traits(world, highlight_desert=False,
                              highlight_steppe=False):
    fig, ax, colour_map = _init_world_plot()

    # Prepare data
    plot_data = np.array([
        [world.index(x, y).total_ultrasocietal_traits()
         for y in range(world.ydim)] for x in range(world.xdim)
         ])
    plot_data = plot_data / world.params.n_ultrasocietal_traits

    # Generate rgba data
    plot_data = colour_map(plot_data)
    plot_data = _colour_special_tiles(plot_data, world, highlight_desert,
                                      highlight_steppe)

    im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
    fig.colorbar(im)
    fig.savefig('ultrasocietal_traits_{:04d}.pdf'.format(world.step_number),
                format='pdf')


# Plot which regions currently have agriculture
def plot_active_agriculture(world, highlight_desert=False,
                            highlight_steppe=False):
    fig, ax, colour_map = _init_world_plot()

    # Prepare data
    active_tiles = [tile for tile in world.tiles
                    if tile.is_active(world.step_number) is True]
    plot_data = np.zeros([world.xdim, world.ydim])
    for tile in active_tiles:
        x, y = tile.position
        plot_data[x][y] = 1.

    # Generate rgba data
    plot_data = colour_map(plot_data)
    plot_data = _colour_special_tiles(plot_data, world, highlight_desert,
                                      highlight_steppe)

    im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
    fig.colorbar(im)
    fig.savefig('active_{:04d}.pdf'.format(world.step_number), format='pdf')


# Base class for accumulators of tile wise data
class AccumulatorBase(object):
    _prefix = None

    def __init__(self, world, date_ranges=None):
        self.world = world
        self.date_ranges = date_ranges
        self.data = {era: np.zeros([world.xdim, world.ydim])
                     for era in date_ranges}

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

    def preprocess(self, data, era):
        return data / np.max(data)

    def min_max(self, data, era):
        return 0, np.max(data)

    def plot_all(self, highlight_desert=False, highlight_steppe=False,
                 area=None):
        for era in self.date_ranges:
            self.plot(era, highlight_desert, highlight_steppe, area)

    def plot(self, era, highlight_desert=False, highlight_steppe=False,
             area=None):
        fig, ax, colour_map = _init_world_plot()

        if area is None:
            xmin, xmax = 0, self.world.xdim
            ymin, ymax = 0, self.world.ydim
        else:
            xmin, xmax, ymin, ymax = area

        plot_data = self.data[era][xmin:xmax, ymin:ymax]

        plot_data = self.preprocess(plot_data, era)
        plot_data = colour_map(plot_data)
        plot_data = _colour_special_tiles(plot_data, self.world,
                                          highlight_desert, highlight_steppe,
                                          area=area)
        vmin, vmax = self.min_max(plot_data, era)
        im = ax.imshow(np.rot90(plot_data), cmap=colour_map, vmin=vmin,
                       vmax=vmax)
        fig.colorbar(im)
        fig.savefig('{}_{}.pdf'.format(self._prefix, era), format='pdf')

    def dump(self, outfile):
        with open(outfile, 'wb') as picklefile:
            pickle.dump(
                {str(key): value for key, value in self.data.items()},
                picklefile)


# Eumerate imperial density
class ImperialDensity(AccumulatorBase):
    _label = 'imperial density'
    _prefix = 'imperial_density'

    def __init__(self, world, date_ranges=imperial_density_date_ranges):
        super().__init__(world, date_ranges)
        self.samples = {era: 0 for era in date_ranges}

    def sample(self):
        # Create list of tiles to sample, only tiles with agriculture
        agricultural_tiles = [tile for tile in self.world.tiles
                              if tile.terrain.polity_forming]
        agricultural_tiles[:] = [tile for tile in agricultural_tiles
                                 if tile.is_active(self.world.step_number)]

        # Create list of eras to add imperial density to, only those that
        # contain the current year
        year = self.world.year()
        active_eras = [era for era in self.date_ranges if era.is_within(year)]
        for tile in agricultural_tiles:
            if tile.polity.size() > _LARGE_POLITY_THRESHOLD:
                for era in active_eras:
                    self.data[era][tile.position[0], tile.position[1]] += 1.
                    self.samples[era] += 1

    def min_max(self, data, era):
        return 0, np.max(self.data[era])


# Enumerate and analyse attack frequency in each tile
class AttackEvents(AccumulatorBase):
    _label = 'attack frequency'
    _prefix = 'attack_frequency'

    def __init__(self, world, date_ranges=None):
        super().__init__(world, date_ranges)

    def sample(self, tile):
        year = self.world.year()
        active_eras = [era for era in self.date_ranges if era.is_within(year)]
        for era in active_eras:
            self.data[era][tile.position[0], tile.position[1]] += 1.


# Base class for correlated data projected onto the map with tilewise
# properties
class CorrelateBase(object):
    _label = None
    _prefix = None
    _REMOVE_FLAG = -5

    def __init__(self, world, date_ranges):
        self.world = world
        self.date_ranges = date_ranges
        self.data = {era: np.zeros([world.xdim, world.ydim])
                     for era in date_ranges}

    # Draw a heatmap of the data projected onto the map
    def plot_heatmap(self, blur=False, area=None):
        if area is None:
            xmin, xmax = 0, self.world.xdim
            ymin, ymax = 0, self.world.ydim
        else:
            xmin, xmax, ymin, ymax = area

        for era in self.date_ranges:
            fig, ax, colour_map = _init_world_plot()

            plot_data = self.data[era][xmin:xmax, ymin:ymax]

            if blur:
                plot_data = ndimage.gaussian_filter(plot_data, sigma=blur)
            # Normalise
            vmax = np.max(plot_data)
            plot_data = plot_data/vmax

            # Create rgb data
            plot_data = colour_map(plot_data)
            plot_data = _colour_special_tiles(plot_data, self.world, area=area)

            im = ax.imshow(np.rot90(plot_data), cmap=colour_map, vmax=vmax,
                           vmin=0)
            fig.colorbar(im)
            fig.savefig('{}_{}.pdf'.format(self._prefix, era))

    # Perform a linear regression of the accumaltors date against the
    # correlators data and plot the result
    def correlate(self, accumulator, blur=False, cumulative=False, area=None):
        assert self.world is accumulator.world
        common_eras = [era for era in self.date_ranges
                       if era in accumulator.date_ranges]

        if area is None:
            xdim = self.world.xdim
            ydim = self.world.ydim
            xmin, xmax = 0, xdim
            ymin, ymax = 0, ydim
        else:
            xmin, xmax, ymin, ymax = area
            xdim = xmax - xmin
            ydim = ymax - ymin

        if cumulative:
            cumulative_sum = np.zeros([xdim, ydim])

        sea_tiles = []
        for tile in self.world.tiles:
            if tile.terrain == terrain.sea:
                x, y = tile.position[0], tile.position[1]
                if x < xmax and x >= xmin:
                    if y < ymax and y >= ymin:
                        sea_tiles.append((x-xmin, y-ymin))

        # Correlate population and imperial density between eras in both
        # cities data and imperial denisty
        for era in common_eras:
            # Figure and axes
            fig, ax = plt.subplots()
            # Axes setup
            ax.set_xlabel(accumulator._label)
            ax.set_ylabel(self._label)
            ax.set_title(str(era))

            comparison = accumulator.data[era][xmin:xmax, ymin:ymax]
            if cumulative:
                comparison += cumulative_sum
                cumulative_sum = comparison
            data = self.data[era][xmin:xmax, ymin:ymax]

            if blur:
                data = ndimage.gaussian_filter(data, sigma=blur)

            # Don't compare sea tiles
            for x, y in sea_tiles:
                comparison[x, y] = self._REMOVE_FLAG
                data[x, y] = self._REMOVE_FLAG

            comparison = comparison.flatten()
            data = data.flatten()

            if blur is False:
                # Only compare tiles with data
                for index in range(len(comparison)):
                    if data[index] == 0:
                        comparison[index] = self._REMOVE_FLAG
                        data[index] = self._REMOVE_FLAG

            # Remove flagged elements
            comparison = np.array([elem for elem in comparison
                                   if elem != self._REMOVE_FLAG])
            data = np.array([elem for elem in data
                             if elem != self._REMOVE_FLAG])

            # Linear regression
            linreg = stats.linregress(comparison, data)

            # Scatter plot of data against comparison with best fit line
            ax.plot(comparison, data, 'x')
            ax.plot(comparison, comparison*linreg.slope + linreg.intercept)
            ax.text(0, 1, str(linreg.rvalue), transform=ax.transAxes)

            fig.tight_layout()
            fig.savefig('{}_{}_correlation_{}.pdf'.format(
                self._prefix, accumulator._prefix, era), format='pdf')


# Population corralatable class
class CitiesPopulation(CorrelateBase):
    _label = 'population'
    _prefix = 'population'

    def __init__(self, world, data_file, date_ranges=cities_date_ranges):
        super().__init__(world, date_ranges)

        # Sum populations from cities and eras
        with open(data_file, 'r') as yamlfile:
            cities_data = yaml.load(yamlfile)

            for city in cities_data:
                for era in date_ranges:
                    try:
                        self.data[era][
                            city['x'], city['y']
                            ] += city['population'][era]
                    except KeyError:
                        raise InvalidDateRange(
                            "Date range {} not in city data\n\t{}".format(
                                era, city)
                            )


# Battles corralatable class
class Battles(CorrelateBase):
    _label = 'number of battles'
    _prefix = 'battles'

    def __init__(self, world, date_ranges, data_file):
        super().__init__(world, date_ranges)

        # Sum battles from data file
        with open(data_file, 'r') as yamlfile:
            battles = yaml.load(yamlfile)

            for battle in battles:
                for era in self.date_ranges:
                    if era.is_within(battle['year']):
                        self.data[era][battle['x'], battle['y']] += 1.
