"""
World module.
"""
from . import polity, terrain, period
from .parameters import defaults
from .community import Community, DIRECTIONS, LittoralNeighbour
from numpy import sqrt
from numpy.random import random, permutation
import yaml

_START_YEAR = -1500
_YEARS_PER_STEP = 2


class World(object):
    """
    World class, a container for all polities, communities and methods relating
    to them.

    Args:
        xdim (int, default=0): The x dimension of the world in communities.
        ydim (int, default=0): The y dimension of the world in communities.
        params (Parameters, default=parameters.defaults): The simulation
            parameter set to use.
        from_file (str, default=None): Path to a world definition YAML file. If
            supplied the world definition will be read from the file.

    Attributes:
        xdim (int): The x dimension of the world in communities.
        ydim (int): The y dimension of the world in communities.
        params (Parameters): The simulation parameter set.
        step_number (int): The current step number.
        tiles (list[Community]): A list of communities in the world.
        polities (list[Polity]): A list of polities in the world.
    """
    def __init__(self, xdim, ydim, communities, params=defaults):
        self.params = params

        self.xdim = xdim
        self.ydim = ydim
        self.total_tiles = xdim*ydim
        self.tiles = communities

        # Initialise neighbours and littoral neighbours
        self.set_neighbours()
        self.set_littoral_tiles()
        self.set_littoral_neighbours()

        # Each agricultural tile is its own polity, set step number to zero
        self.reset()

    def __str__(self):
        string = 'World:\n'
        string += '\t- Tiles: {0}\n'.format(self.total_tiles)
        string += '\t- Dimensions: {0}x{1}\n'.format(self.xdim, self.ydim)
        string += '\t- Number of polities: {0}'.format(
            self.number_of_polities())

        return string

    def number_of_polities(self):
        """
        Calculate the number of polities in the world.

        Returns:
            (int): The number of polities.
        """
        return len(self.polities)

    def index(self, x, y):
        """
        Return the tile at coordinates (x,y).

        Returns:
            (Community): The community at coordinate (x,y).
            (None): If there is no such tile.
        """
        if any([x < 0, x >= self.xdim, y < 0, y >= self.ydim]):
            return None
        return self.tiles[self._index(x, y)]

    def _index(self, x, y):
        """
        Return the position in the tiles list of the tile at coordinates
        (x,y).
        """
        return x + y*self.xdim

    def year(self):
        """
        Return the current year.

        Returns:
            (int): The current year. Years BC are negative.
        """
        return self.step_number*_YEARS_PER_STEP + _START_YEAR

    def sea_attack_distance(self):
        """
        Determine maximum sea attack distance at current step.

        Returns:
            (float): The maximum sea attack distance.
        """
        return (self.params.base_sea_attack_distance
                + self.step_number * self.params.sea_attack_increment)

    def set_neighbours(self):
        """
        Assign tiles their neighbours.
        """
        for x in range(self.xdim):
            for y in range(self.ydim):
                tile = self.index(x, y)
                tile.position = (x, y)
                tile.neighbours['left'] = self.index(x-1, y)
                tile.neighbours['right'] = self.index(x+1, y)
                tile.neighbours['up'] = self.index(x, y+1)
                tile.neighbours['down'] = self.index(x, y-1)

    def set_littoral_tiles(self):
        """
        Assign littoral tiles the littoral flag.
        """
        for tile in self.tiles:
            # Don't set littoral status for sea or desert tiles
            if not tile.terrain.polity_forming:
                continue

            for direction in DIRECTIONS:
                neighbour = tile.neighbours[direction]
                # Ensure there is a neighour
                if neighbour is None:
                    continue
                # Check if neighbour is a sea tile
                if neighbour.terrain is terrain.sea:
                    tile.littoral = True
                    # Break here as only one neighbour needs to be sea for tile
                    # to be littoral
                    break

    def set_littoral_neighbours(self):
        """
        Assign littoral tiles their lists of littoral neighbours.
        """
        littoral_tiles = [tile for tile in self.tiles if tile.littoral is True]
        n_littoral = len(littoral_tiles)

        for tile in littoral_tiles:
            # Add self as a littoral neighbour with 0 distance, this is
            # important in order to reproduce Turchin's results
            tile.littoral_neighbours.append(LittoralNeighbour(tile, 0))

        for i in range(n_littoral-1):
            itile = littoral_tiles[i]
            for j in range(i+1, n_littoral):
                jtile = littoral_tiles[j]

                # Calculate euclidean distance between tiles in tile dimension
                # units
                distance = sqrt((itile.position[0]-jtile.position[0])**2 +
                                (itile.position[1]-jtile.position[1])**2)

                # Add neighbour and the symmetric entry
                itile.littoral_neighbours.append(
                    LittoralNeighbour(jtile, distance))
                jtile.littoral_neighbours.append(
                    LittoralNeighbour(itile, distance))

    @classmethod
    def from_file(cls, yaml_file, params=defaults):
        """
        Read a world from a YAML file.

        Args:
            yaml_file (str): Path to the file containing a YAML definition of
                the world.
        """
        # Parse YAML file
        with open(yaml_file, 'r') as infile:
            world_data = yaml.load(infile)
        xdim = world_data['xdim']
        ydim = world_data['ydim']

        # Determine total number of tiles and assign list
        total_communities = xdim*ydim
        communities = [None]*total_communities

        # Enter world data into tiles list
        for community in world_data['communities']:
            x, y = community['x'], community['y']

            assert community['terrain'] in ['agriculture', 'steppe',
                                            'desert', 'sea']
            if community['terrain'] == 'agriculture':
                landscape = terrain.agriculture
            elif community['terrain'] == 'steppe':
                landscape = terrain.steppe
            elif community['terrain'] == 'desert':
                landscape = terrain.desert
            elif community['terrain'] == 'sea':
                landscape = terrain.sea

            if landscape.polity_forming:
                elevation = community['elevation'] / 1000.
                agricultural_period = community['activeFrom']

                if agricultural_period == 'agri1':
                    active_from = period.agri1
                elif agricultural_period == 'agri2':
                    active_from = period.agri2
                elif agricultural_period == 'agri3':
                    active_from = period.agri3

                communities[x + y*xdim] = Community(params, landscape,
                                                    elevation, active_from)
            else:
                communities[x + y*xdim] = Community(params, landscape)

        return cls(xdim, ydim, communities, params)

    def reset(self):
        """
        Reset the world by returning all polities to single communities and
        setting the step number to 0.
        """
        self.step_number = 0
        self.polities = [polity.Polity([tile])
                         for tile in self.tiles if tile.terrain.polity_forming]

    def cultural_shift(self):
        """
        Attempt cultural shift in all communities.
        """
        for tile in self.tiles:
            if tile.terrain.polity_forming:
                tile.cultural_shift(self.params)

    def disintegration(self):
        """
        Attempt disintegration of all polities
        """
        new_states = []
        for state in self.polities:
            # Skip single community polities
            if state.size() == 1:
                continue
            if state.disintegrate_probability(self.params) > random():
                # Create a new set of polities, one for each of the communities
                new_states += state.disintegrate()

        # Delete the now empy polities
        self.prune_empty_polities()

        # Append new polities from disintegrated old polities to list
        self.polities += new_states

    def attack(self, callback=None):
        """
        Attempt an attack from all communities.

        Args:
            callback (function, default=None): A callback function invoked if
                an attack is successful. Used to record attack events.
        """
        # Generate a random order for communities to attempt attacks in
        attack_order = permutation(self.total_tiles)
        for tile_no in attack_order:
            tile = self.tiles[tile_no]
            if tile.can_attack(self.step_number):
                tile.attempt_attack(self.params, self.step_number,
                                    self.sea_attack_distance(), callback)

        self.prune_empty_polities()

    def prune_empty_polities(self):
        """
        Prune polities with zero communities.
        """
        self.polities = [state for state in self.polities
                         if state.size() != 0]

    def step(self, attack_callback=None):
        """
        Conduct a simulation step

        Args:
            attack_callback (function, default=None): A callback function
                invoked if an attack is successful. Used to record attack
                events.
        """
        # Attacks
        self.attack(attack_callback)

        # Cultural shift
        self.cultural_shift()

        # Disintegration
        self.disintegration()

        # Increment step counter
        self.step_number += 1
