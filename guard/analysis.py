"""
Classes and routines for analysis of simulations.
"""

from . import terrain
from .area import Rectangle
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


def _init_world_plot():
    """
    Establish the figure, axis and colourmap for a standard map plot
    """
    # Initialise figure and axis
    fig = plt.figure()
    ax = fig.subplots()

    # Hide axes ticks
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Colour map
    colour_map = plt.get_cmap('RdYlGn').reversed()

    return fig, ax, colour_map


def _colour_special_tiles(rgba_data, world, highlight_desert=False,
                          highlight_steppe=False, area=None):
    """
    Colour sea, steppe and desert tiles distinctly
    """
    if area is None:
        area = Rectangle.entire_map(world)
    xmin, xmax, ymin, ymax = area.bounds()
    # Colour sea and optionally desert
    for tile in world.tiles:
        x, y = tile.position[0], tile.position[1]
        if area.in_area(x, y):
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


def _highlight(rgba_data, area, highlight):
    """
    Highlight tiles in an area
    """
    xmin, xmax, ymin, ymax = area.bounds()
    for x, y in highlight.all_tiles:
        if area.in_area(x, y):
            x -= xmin
            y -= ymin
            rgba_data[x][y] += np.array([0.3, 0.0, 0.3, 0.0])
            rgba_data[x][y] = np.array(
                [min(value, 1.0) for value in rgba_data[x][y]]
                )
    return rgba_data


def plot_military_techs(world, highlight_desert=False, highlight_steppe=False):
    fig, ax, colour_map = _init_world_plot()
    """
    Plot a heatmap of military technology level.

    Args:
        world (World): The world object to plot.
        highligt_desert (bool, default=False): Highlight desert tiles on the
            map.
        highligt_steppe (bool, default=False): Highlight steppe tiles on the
            map.
    """

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


def plot_ultrasocietal_traits(world, highlight_desert=False,
                              highlight_steppe=False):
    """
    Plot a heatmap of ultrasocietal trait level.

    Args:
        world (World): The world object to plot.
        highligt_desert (bool, default=False): Highlight desert tiles on the
            map.
        highligt_steppe (bool, default=False): Highlight steppe tiles on the
            map.
    """
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


def plot_active_agriculture(world, highlight_desert=False,
                            highlight_steppe=False):
    """
    Plot which regions currently have agriculture.

    Args:
        world (World): The world object to plot.
        highligt_desert (bool, default=False): Highlight desert tiles on the
            map.
        highligt_steppe (bool, default=False): Highlight steppe tiles on the
            map.
    """
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


class AccumulatorBase(object):
    """
    Base class for accumulators of tile wise data

    Args:
        world (World): The world definition.
        date_ranges (list[DateRange]): The date ranges to accumulate data for.
            These ranges may overlap.

    Attributes:
        data (dict): The accumulated data for each of the date ranges
            specified.  The keys of the dictionary are the date ranges. The
            values of two dimensional numpy arrays where each element
            represents the accumulated value in a tile of the map.
    """
    _prefix = None

    def __init__(self, world, date_ranges):
        self.world = world
        self.date_ranges = date_ranges
        self.data = {era: np.zeros([world.xdim, world.ydim])
                     for era in date_ranges}

    @classmethod
    def from_file(cls, world, data_file):
        """
        Reconstruct and accumulator from dumped data.

        Args:
            world (World): The world definition.
            data_file (str): Path to the dumped data pickle file.

        Returns:
            (AccumulatorBase): An accumulator object with the state defined in
                data_file.
        """
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

    @classmethod
    def mean(cls, accumulators):
        mean_accumulator = cls(accumulators[0].world,
                               accumulators[0].date_ranges)

        total = len(accumulators)
        for era in mean_accumulator.date_ranges:
            data = sum([accumulator.data[era] for accumulator in accumulators])
            data = data / total
            mean_accumulator.data[era] = data

        return mean_accumulator

    def sample(self):
        """
        Sample the current state of the world.
        """
        raise NotImplementedError

    def preprocess(self, data, era):
        """
        Preprocess data to be plotted. In this implementation the data is
        normalised by dividing each point by the maximum value.

        Args:
            data (numpy Array): A two dimensional numpy array where each
                element represents a datapoint for a tile on the world map.
            era (DateRange): The era the data corresponds to.

        Returns:
            (numpy Array): The processed data.
        """
        return data / np.max(data)

    def min_max(self, data, era):
        """
        Determine the minimum and maximum values of the data to use for the
        colorbar bounds.

        Args:
            data (numpy Array): A two dimensional numpy array where each
                element represents a datapoint for a tile on the world map.
            era (DateRange): The era the data corresponds to.

        Returns:
            (tuple): A tuple in the form (minimum, maximum).
        """
        return 0, np.max(data)

    def plot_all(self, highlight_desert=False, highlight_steppe=False,
                 area=None, highlight=None):
        """
        Produce plots of the accumlated data for all eras.

        Args:
            highligt_desert (bool, default=False): Highlight desert tiles on
                the map.
            highligt_steppe (bool, default=False): Highlight steppe tiles on
                the map.
            area (Area, default=None): The area to plot. If None then the
                entire map is plotted.
            highlight (Area, default=None): An arbitrary region of the map to
                highlight.
        """
        if area is None:
            area = Rectangle.entire_map(self.world)
        for era in self.date_ranges:
            self.plot(era, highlight_desert, highlight_steppe, area, highlight)

    def plot(self, era, highlight_desert=False, highlight_steppe=False,
             area=None, highlight=None):
        """
        Produce a plot of the accumlated data for one era.

        Args:
            era (DateRange): The era to plot data for.
            highligt_desert (bool, default=False): Highlight desert tiles on
                the map.
            highligt_steppe (bool, default=False): Highlight steppe tiles on
                the map.
            area (Area, default=None): The area to plot. If None then the
                entire map is plotted.
            highlight (Area, default=None): An arbitrary region of the map to
                highlight.
        """
        fig, ax, colour_map = _init_world_plot()

        if area is None:
            area = Rectangle.entire_map(self.world)
        xmin, xmax, ymin, ymax = area.bounds()

        plot_data = self.data[era][xmin:xmax, ymin:ymax]
        plot_data = self.preprocess(plot_data, era)
        vmin, vmax = self.min_max(plot_data, era)

        plot_data = colour_map(plot_data)
        plot_data = _colour_special_tiles(plot_data, self.world,
                                          highlight_desert, highlight_steppe,
                                          area)
        if highlight:
            plot_data = _highlight(plot_data, area, highlight)

        im = ax.imshow(np.rot90(plot_data), cmap=colour_map, vmin=vmin,
                       vmax=vmax)
        fig.colorbar(im)
        fig.savefig('{}_{}.pdf'.format(self._prefix, era), format='pdf')

    def dump(self, outfile):
        """
        Write the state of the accumulator to a file in a pickled format.

        Args:
            outfile (str): path to the file to write.
        """
        with open(outfile, 'wb') as picklefile:
            pickle.dump(
                {str(key): value for key, value in self.data.items()},
                picklefile)


class ImperialDensity(AccumulatorBase):
    """
    Imperial density accumulator

    Args:
        world (World): The world definition.
        date_ranges (list[DateRange], default=imperial_density_date_ranges):
            The date ranges to accumulate data for. These ranges may overlap.
            The default are the imperial density eras from Turchin et al.
            (2013)

    Attributes:
        data (dict): The accumulated imperial density for each of the date
            ranges specified.  The keys of the dictionary are the date ranges.
            The values of two dimensional numpy arrays where each element
            represents the accumulated value in a tile of the map.
    """
    _label = 'imperial density'
    _prefix = 'imperial_density'

    def __init__(self, world, date_ranges=imperial_density_date_ranges):
        super().__init__(world, date_ranges)

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


class AttackEvents(AccumulatorBase):
    """
    Attacks accumulator

    Args:
        world (World): The world definition.
        date_ranges (list[DateRange]): The date ranges to accumulate data for.
            These ranges may overlap.

    Attributes:
        data (dict): The accumulated number of attacks for each of the date
            ranges specified.  The keys of the dictionary are the date ranges.
            The values of two dimensional numpy arrays where each element
            represents the accumulated value in a tile of the map.
    """
    _label = 'attack frequency'
    _prefix = 'attack_frequency'

    def __init__(self, world, date_ranges):
        super().__init__(world, date_ranges)

    def sample(self, tile):
        year = self.world.year()
        active_eras = [era for era in self.date_ranges if era.is_within(year)]
        for era in active_eras:
            self.data[era][tile.position[0], tile.position[1]] += 1.


class CorrelateBase(object):
    """
    Base class for correlating data projected onto the map with the data in an
    accumulator object

    Args:
        world (World): The world definition.
        date_ranges (list[DateRange]): The date ranges of the data.
    """
    _label = None
    _prefix = None
    _REMOVE_FLAG = -5

    def __init__(self, world, date_ranges):
        self.world = world
        self.date_ranges = date_ranges
        self.data = {era: np.zeros([world.xdim, world.ydim])
                     for era in date_ranges}

    def plot_heatmap(self, blur=False, area=None, highlight=None):
        """
        Plot a heatmap of the data projected onto the map.

        Args:
            blur (float, default=False): The radius of Gaussian blur to apply
                to the data. If False no blur is applied.
            area (Area, default=None): The area to plot. If None the whole map
                is plotted.
            highlight (Area, default=None): An area of the map to highlight.
        """
        if area is None:
            area = Rectangle.entire_map(self.world)
        xmin, xmax, ymin, ymax = area.bounds()

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
            if highlight:
                plot_data = _highlight(plot_data, area, highlight)

            im = ax.imshow(np.rot90(plot_data), cmap=colour_map, vmax=vmax,
                           vmin=0)
            fig.colorbar(im)
            fig.savefig('{}_{}.pdf'.format(self._prefix, era))

    def correlate(self, accumulator, blur=False, cumulative=False, area=None,
                  exclude=None, log_log=False):
        """
        Perform a linear regression of the accumulators date against the
        correlators data and plot the result.

        Args:
            accumulator (AccumulatorBase): The accumulator to compare against.
            blur (float, default=False): The radius of Gaussian blur to apply
                to the data. If False no blur is applied.
            cumulative (bool, default=False): Whether to compare against
                cumulative accumulator data or not.
            area (Area, default=None): The area to correlate and plot. If None
                the whole map correlated.
            exclude (Area, default=None): An area to exclude from the
                correlation.
            log_log (bool, default=False): If true correlate the logarithms of
                the data and accumulator data.
        """
        assert self.world is accumulator.world
        common_eras = [era for era in self.date_ranges
                       if era in accumulator.date_ranges]

        if area is None:
            area = Rectangle.entire_map(self.world)
        xmin, xmax, ymin, ymax = area.bounds()
        xdim = xmax - xmin
        ydim = ymax - ymin

        if cumulative:
            cumulative_sum = np.zeros([xdim, ydim])

        sea_tiles = []
        for tile in self.world.tiles:
            if tile.terrain == terrain.sea:
                x, y = tile.position[0], tile.position[1]
                if area.in_area(x, y):
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

            # Don't compare excluded tiles
            if exclude:
                for x, y in exclude.all_tiles:
                    comparison[x, y] = self._REMOVE_FLAG
                    data[x, y] = self._REMOVE_FLAG

            comparison = comparison.flatten()
            data = data.flatten()

            if log_log is True:
                # Remove any tiles with value 0
                for index in range(len(comparison)):
                    if data[index] == 0 or comparison[index] == 0:
                        comparison[index] = self._REMOVE_FLAG
                        data[index] = self._REMOVE_FLAG

            # Remove flagged elements
            comparison = np.array([elem for elem in comparison
                                   if elem != self._REMOVE_FLAG])
            data = np.array([elem for elem in data
                             if elem != self._REMOVE_FLAG])

            # Take logarithms if requested
            if log_log is True:
                comparison = np.log(comparison)
                data = np.log(data)

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
    """
    Correlator for historical population data.

    Args:
        world (World): The world definition.
        data_file (str): Path to the historical population YAML file.
        date_ranges (list[DateRange], default=cities_date_ranges): The date
            ranges of the data.
    """
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
    """
    Correlator for historical battles data.

    Args:
        world (World): The world definition.
        data_file (str): Path to the historical battles YAML file.
        date_ranges (list[DateRange]): The date
            ranges of the data.
    """
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


# Historical imperial density correlatble class
class HistoricalImperialDensity(CorrelateBase):
    """
    Correlator for historical imperial density.

    Args:
        world (World): The world definition.
        data_file (str): Path to the imperial density pickle file.
    """
    _label = 'historical imperial density'
    _prefix = 'imperial_density'

    def __init__(self, world, data_file):
        # Use the date ranges from Turchin et al.
        super().__init__(world, date_ranges=imperial_density_date_ranges)

        with open(data_file, 'rb') as picklefile:
            impd = pickle.load(picklefile)

        for era, imperial_density in impd.items():
            self.data[era] = imperial_density


class CompareEmpireShape(object):
    """
    A class for analysing the polities contained within the historical extent
    of an empire.

    Args:
        world (World): The world definition.
        data_file (str): The path to the empire definition YAML file.
        years (list[str]): The years at which the extend of the empire are
            defined. These must correspond to keys in the YAML file and are of
            the format "year era" _e.g._ "100 AD", "300 BC". Year 0 is given by
            "0".
    """
    def __init__(self, world, data_file, years):
        self.world = world
        self.years = years

        with open(data_file, 'r') as infile:
            empire_dict = yaml.load(infile)

        self.name = empire_dict['empire']
        self.occupied = {}
        self.n_polities = {}
        self.polity_sizes = {}

        for year in self.years:
            self.occupied[year] = []
            # Copy occupied tiles from empire definition
            for occupied in empire_dict[year]:
                self.occupied[year].append((occupied['x'], occupied['y']))

    def sample(self):
        """
        Sample the polities within a historical empires extent.
        """
        # Convert year from number to string (i.e. -1200 to 1200BC)
        year = self.world.year()
        if year < 0:
            year = str(year)[1:] + 'BC'
        elif year == 0:
            year = '0'
        elif year > 0:
            year = str(year) + 'AD'
        # Only sample when we are at a valid year
        if year not in self.years:
            return

        # retrieve list of occupied tile coordinates
        occupied = self.occupied[year]

        # Sum the number of polities in the historical extent of the empire,
        # and their sizes
        included_polities = []
        n_polities = 0
        polity_sizes = []
        for coordinates in occupied:
            tile = self.world.index(coordinates[0], coordinates[1])
            # Skip desert tiles included in the extent of the empire
            if not tile.terrain.polity_forming:
                continue
            polity = tile.polity
            # Ensure polities are not doubly counted if they possess more than
            # one community in the extent of the empire
            if polity in included_polities:
                continue
            included_polities.append(polity)
            n_polities += 1
            polity_sizes.append(polity.size())

        self.n_polities[year] = n_polities
        self.polity_sizes[year] = polity_sizes

    def plot_histograms(self):
        """
        Plot histograms of the number of polities of each size, and the number
        of communities in polities of each size.
        """
        for year in self.years:
            # Don't produce a histogram if there are no polities or the
            # empire did not exist at this century
            if self.n_polities[year] == 0:
                continue
            elif self.occupied[year] == []:
                continue

            # Initialise figure and axis
            fig = plt.figure()
            ax = fig.subplots(1, 2)

            polity_sizes = self.polity_sizes[year]
            bins = max(polity_sizes)

            ax[0].set_title('Polities of size N')
            ax[0].set_ylabel('number of polities')
            ax[0].set_xlabel('size of polity / cells')
            ax[0].hist(polity_sizes, bins=bins)
            ax[1].set_title('Number of cells in\npolities of size N')
            ax[1].set_ylabel('number of cells')
            ax[1].set_xlabel('size of polity / cells')
            ax[1].hist(polity_sizes, bins=bins, weights=polity_sizes)
            fig.tight_layout()
            fig.savefig('{}_{}.pdf'.format(self.name, year))

    def dump(self, outfile):
        """
        Dump the data of the object to a pickle file.

        Args:
            outfile (str): Path to the pickle file to create.
        """
        with open(outfile, 'wb') as picklefile:
            pickle.dump(self.n_polities, picklefile)
            pickle.dump(self.polity_sizes, picklefile)

    @classmethod
    def from_file(cls, world, data_file, years, infile):
        """
        Reconstruct a CompareEmpireShape object previously dumped to a pickle
        file.

        Args:
            world (World): The world definition.
            data_file (str): The path to the empire definition YAML file.
            years (list[str]): The years at which the extend of the empire are
                defined. These must correspond to keys in the YAML file and are
                of the format "year era" _e.g._ "100 AD", "300 BC". Year 0 is
                given by "0".
            infile (str): Path to the pickle file.

        Returns:
            (CompareEmpireShape): A CompareEmpireSHape object with the state of
                that previously dumped to the pickle file.
        """
        compare = cls(world, data_file, years)
        with open(infile, 'rb') as picklefile:
            compare.n_polities = pickle.load(picklefile)
            compare.polity_sizes = pickle.load(picklefile)
        return compare
