from . import community, polity
from .parameters import defaults
from numpy import sqrt
from numpy.random import random, permutation

# Container for all communities(tiles) and methods relating to them
class World(object):
    def __init__(self, xdim, ydim, params=defaults):
        self.xdim = xdim
        self.ydim = ydim
        self.total_tiles = xdim*ydim

        self.params = params

        #self.tiles = [None for i in range(self.total_tiles)]

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
        return self.tiles[x*self.xdim + y]

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
        littoral_tiles = list(filter(lambda tile: tile.littoral == True, self.tiles))
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

    # Populate the world with agriculture communities at zero elevation
    def create_flat_agricultural_world(self):
        self.tiles = [community.Community(self.params) for i in range(self.total_tiles)]
        self.set_neighbours()
        # Each tile is its own polity
        self.polities = [polity.Polity([tile]) for tile in self.tiles]

    # Attempt culturual shift in all communities
    def cultural_shift(self):
        for tile in self.tiles:
            if tile.terrain is community.Terrain.agriculture:
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

    # Attempt an attack from all communities
    def attack(self):
        # Generate a random order for communities to attempt attacks in
        attack_order = permutation(self.total_tiles)
        for tile_no in attack_order:
            tile = self.tiles[tile_no]
            if tile.terrain is community.Terrain.agriculture:
                tile.attempt_attack(self.params)

        self.prune_empty_polities()

    # Prune polities with zero communities
    def prune_empty_polities(self):
        for state in self.polities:
            if state.size() == 0:
                self.polities.remove(state)

    # Conduct a simulation step
    def step(self):
        # Attacks
        self.attack()

        # Cultural shift
        self.cultural_shift()

        # Disintegration
        self.disintegration()
