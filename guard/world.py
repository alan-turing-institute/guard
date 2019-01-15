from . import community, polity
from .parameters import defaults
from numpy import sqrt
from numpy.random import random, permutation
import yaml

# Step numbers to activate communities in diffirent agricultural periods
activation_steps = {1: community.Period.agri1,
        900: community.Period.agri2,
        1100: community.Period.agri3}

# Container for all communities(tiles) and methods relating to them
class World(object):
    def __init__(self, xdim=0, ydim=0, params=defaults, from_file=None):
        self.params = params

        if from_file is not None:
            self.read_from_yaml(open(from_file, 'r'))
        else:
            self.xdim = xdim
            self.ydim = ydim
            self.total_tiles = xdim*ydim

        self.step_number = 0

    def __str__(self):
        string = 'World:\n'
        string += '\t- Tiles: {0}\n'.format(self.total_tiles)
        string += '\t- Dimensions: {0}x{1}\n'.format(self.xdim, self.ydim)
        string += '\t- Number of polities: {0}'.format(self.number_of_polities())

        return string

    # Calculate the number of polities in the world
    def number_of_polities(self):
        return len(self.polities)

    # Return the tile at coordinates (x,y)
    # Returns None if there is no such tile
    def index(self, x, y):
        if any([x < 0, x >= self.xdim, y < 0, y >= self.ydim]):
            return None
        return self.tiles[self._index(x,y)]

    # Returns the position in the tiles list of the tile at coordinates (x,y)
    def _index(self, x, y):
        return x + y*self.xdim

    # Determine maximum sea attack distance at current step
    def sea_attack_distance(self):
        return self.params.base_sea_attack_distance + \
                self.step_number * self.params.sea_attack_increment

    # Assign tiles their neighbours
    def set_neighbours(self):
        for x in range(self.xdim):
            for y in range(self.ydim):
                tile = self.index(x,y)
                tile.position = (x,y)
                tile.neighbours['left'] = self.index(x-1,y)
                tile.neighbours['right'] = self.index(x+1,y)
                tile.neighbours['up'] = self.index(x,y+1)
                tile.neighbours['down'] = self.index(x,y-1)

    # Determine which tiles are littoral
    def set_littoral_tiles(self):
        for tile in self.tiles:
            # Don't set littoral status for sea or desert tiles
            if tile.terrain in [community.Terrain.sea, community.Terrain.desert]:
                continue

            for direction in community.DIRECTIONS:
                neighbour = tile.neighbours[direction]
                # Ensure there is a neighour
                if neighbour == None:
                    continue
                # Check if neighbour is a sea tile
                if neighbour.terrain == community.Terrain.sea:
                    tile.littoral = True
                    # Break here as only one neighbour needs to be sea for tile to
                    # be littoral
                    break

    # Determine a list of all littoral neighbours and distance for all littoral tiles
    def set_littoral_neighbours(self):
        littoral_tiles = [tile for tile in self.tiles if tile.littoral == True]
        n_littoral = len(littoral_tiles)

        for tile in littoral_tiles:
            # Add self as a littoral neighbour with 0 distance, this is important
            # in order to reproduce Turchin's results
            tile.littoral_neighbours.append(community.LittoralNeighbour(tile,0))

        for i in range(n_littoral-1):
            itile = littoral_tiles[i]
            for j in range(i+1, n_littoral):
                jtile = littoral_tiles[j]

                # Calculate euclidean distance between tiles in tile dimension units
                distance = sqrt( (itile.position[0]-jtile.position[0])**2 + \
                        (itile.position[1]-jtile.position[1])**2 )

                # Add neighbour and the symmetric entry
                itile.littoral_neighbours.append(community.LittoralNeighbour(jtile,distance))
                jtile.littoral_neighbours.append(community.LittoralNeighbour(itile,distance))

    # Read a world from a YAML file
    def read_from_yaml(self, yaml_file):
        # Parse YAML file
        tile_data = yaml.load(yaml_file)

        # Determine total number of tiles and assign list
        self.total_tiles = len(tile_data)
        self.tiles = [None]*self.total_tiles

        # Determine bounds of lattice
        xmax = 0
        ymax = 0
        for tile in tile_data:
            x, y = tile['x'], tile['y']
            if x > xmax:
                xmax = x
            if y > ymax:
                ymax = y
        self.xdim = xmax+1
        self.ydim = ymax+1

        # Terrains which may form polities
        polity_forming = [community.Terrain.agriculture, community.Terrain.steppe]

        # Enter world data into tiles list
        for tile in tile_data:
            x, y = tile['x'], tile['y']

            assert tile['terrain'] in ['agriculture','steppe','desert','sea']
            if tile['terrain'] == 'agriculture':
                terrain = community.Terrain.agriculture
            elif tile['terrain'] == 'steppe':
                terrain = community.Terrain.steppe
            elif tile['terrain'] == 'desert':
                terrain = community.Terrain.desert
            elif tile['terrain'] == 'sea':
                terrain = community.Terrain.sea

            if terrain in polity_forming:
                elevation = tile['elevation']
                agricultural_period = tile['activeFrom']

                if agricultural_period == 'agri1':
                    active_from = community.Period.agri1
                elif agricultural_period == 'agri2':
                    active_from = community.Period.agri2
                elif agricultural_period == 'agri3':
                    active_from = community.Period.agri3

                self.tiles[self._index(x,y)] = community.Community(self.params, terrain,
                        elevation, active_from)
            else:
                self.tiles[self._index(x,y)] = community.Community(self.params, terrain)

        # Initialise neighbours and littoral neighbours
        self.set_neighbours()
        self.set_littoral_tiles()
        self.set_littoral_neighbours()

        # Each agricultural tile is its own polity
        self.polities = [polity.Polity([tile]) for tile in self.tiles if tile.terrain in polity_forming]

    # Populate the world with agriculture communities at zero elevation
    def create_flat_agricultural_world(self, steppes=[]):
        self.tiles = [community.Community(self.params) for i in range(self.total_tiles)]
        for coordinate in steppes:
            self.tiles[self._index(coordinate[0], coordinate[1])] = community.Community(self.params, community.Terrain.steppe)
        self.set_neighbours()
        # Each tile is its own polity
        self.polities = [polity.Polity([tile]) for tile in self.tiles]

    # Attempt culturual shift in all communities
    def cultural_shift(self):
        for tile in self.tiles:
            if tile.terrain in [community.Terrain.agriculture, community.Terrain.steppe]:
                tile.cultural_shift(self.params)

    # Attempt disintegration of all polities
    def disintegration(self):
        new_states = []
        for state in self.polities:
            probability = state.disintegrate_probability(self.params)

            if probability > random():
                # Create a new set of polities, one for each of the communities
                for tile in state.communities:
                    new_states.append(polity.Polity([tile]))
                # Destroy the old polity
                self.polities.remove(state)

        # Append new polities from disintegrated old polities to list
        self.polities += new_states

    # Activate agricultural communities
    def activate(self):
        # Determine the period
        period = activation_steps[self.step_number]

        for tile in self.tiles:
            if tile.terrain in [community.Terrain.agriculture, community.Terrain.steppe]:
                if tile.active_from == period:
                    tile.active = True

    # Attempt an attack from all communities
    def attack(self):
        # Generate a random order for communities to attempt attacks in
        attack_order = permutation(self.total_tiles)
        for tile_no in attack_order:
            tile = self.tiles[tile_no]
            if tile.terrain in [community.Terrain.agriculture, community.Terrain.steppe]:
                if tile.active:
                    tile.attempt_attack(self.params, self.sea_attack_distance())

        self.prune_empty_polities()

    # Prune polities with zero communities
    def prune_empty_polities(self):
        self.polities[:] = [state for state in self.polities if state.size() is not 0 ]

    # Conduct a simulation step
    def step(self):
        # Increment step counter
        self.step_number += 1

        # Activate agricultural communities
        if self.step_number in activation_steps.keys():
            self.activate()

        # Attacks
        self.attack()

        # Cultural shift
        self.cultural_shift()

        # Disintegration
        self.disintegration()
