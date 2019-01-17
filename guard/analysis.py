from . import community, terrain
import matplotlib.pyplot as plt
import numpy as np

# How many communities a polity requires before it is considered large and is
# recorded
_LARGE_POLITY_THRESHOLD = 10

# Steps at which to reset the imperial density map and store accumulated data
# as an era (corresponding to 500BCE, 500CE and 1500CE)
# Each step is 2 years and the simulation begins at 1500BCE
_RESET_STEPS = [500,1000,1500]

# Normalisation factor, to ensure imperial density is always in the range [0,1]
_NORMALISATION_FACTOR = 1/500.

# Colours
_SEA = np.array([0.25098039, 0.57647059, 0.92941176, 1.])
_DESERT = np.array([0.7372549 , 0.71372549, 0.25098039, 1.])
_STEPPE = np.array([0.42745098, 0.        , 0.75686275, 1.])

class ImperialDensity(object):
    def __init__(self, world):
        self.world = world

        self.imperial_density = np.zeros([world.xdim, world.ydim])
        self.imperial_density_eras = []

    def sample(self):
        # Create list of tiles to sample, only tiles with agriculture
        agricultural_tiles = [tile for tile in self.world.tiles if tile.terrain.polity_forming]
        agricultural_tiles[:] = [tile for tile in agricultural_tiles \
                if tile.is_active(self.world.step_number)]

        for tile in agricultural_tiles:
            if tile.polity.size() > _LARGE_POLITY_THRESHOLD:
                self.imperial_density[tile.position[0], tile.position[1]] += 1.

        # Reset accumulated data and store if required
        if self.world.step_number in _RESET_STEPS:
            era = _RESET_STEPS.index(self.world.step_number)
            self.imperial_density_eras.append(self.imperial_density * _NORMALISATION_FACTOR)
            self.imperial_density = np.zeros([self.world.xdim, self.world.ydim])

    def export(self, normalise=False, highlight_desert=False, highlight_steppe=False):
        for i,era in enumerate(self.imperial_density_eras):
            fig, ax, colour_map = _init_world_plot()

            # Express data as RGBA values
            if normalise:
                era = era / np.max(era)
            plot_data = colour_map(era)

            plot_data = _colour_special_tiles(plot_data, self.world, highlight_desert, highlight_steppe)

            im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
            fig.colorbar(im)
            fig.savefig('era_{:d}.pdf'.format(i+1), format='pdf')

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
