from . import community
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
        agricultural_tiles = [tile for tile in self.world.tiles if tile.terrain in [community.Terrain.agriculture, community.Terrain.steppe]]
        agricultural_tiles[:] = [tile for tile in agricultural_tiles if tile.active]

        for tile in agricultural_tiles:
            if tile.polity.size() > _LARGE_POLITY_THRESHOLD:
                self.imperial_density[tile.position[0], tile.position[1]] += 1.

        # Reset accumulated data and store if required
        if self.world.step_number in _RESET_STEPS:
            era = _RESET_STEPS.index(self.world.step_number)
            self.imperial_density_eras.append(self.imperial_density * _NORMALISATION_FACTOR)
            self.imperial_density = np.zeros([self.world.xdim, self.world.ydim])

    def export(self, highlight_desert=False, highlight_steppe=False):
        for i,era in enumerate(self.imperial_density_eras):
            # Initialise figure and axis
            fig = plt.figure()
            ax = fig.subplots()

            # Hide axes ticks
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)

            # Express data as RGBA values
            colour_map = plt.get_cmap('RdYlGn').reversed()
            plot_data = colour_map(era)

            # Colour sea and optionally desert
            for tile in self.world.tiles:
                x, y = tile.position[0], tile.position[1]
                if tile.terrain is community.Terrain.sea:
                    plot_data[x][y] = _SEA
                elif tile.terrain is community.Terrain.desert:
                    if highlight_desert:
                        plot_data[x][y] = _DESERT
                elif tile.terrain is community.Terrain.steppe:
                    if highlight_steppe:
                        plot_data[x][y] = _STEPPE

            im = ax.imshow(np.rot90(plot_data), cmap=colour_map)
            fig.colorbar(im)
            fig.savefig('{}.pdf'.format(i), format='pdf')
