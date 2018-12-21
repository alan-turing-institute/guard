from . import community, polity
from .parameters import defaults
from numpy.random import random

# Container for all communities(tiles) and methods relating to them
class World(object):
    def __init__(self, xdim, ydim, params=defaults):
        self.xdim = xdim
        self.ydim = ydim
        self.total_tiles = xdim*ydim

        self.params = params

        #self.tiles = [None for i in range(self.total_tiles)]

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
                tile.neighbours['left'] = self.index(x-1,y)
                tile.neighbours['right'] = self.index(x+1,y)
                tile.neighbours['up'] = self.index(x,y+1)
                tile.neighbours['down'] = self.index(x,y-1)

    # Populate the world with agriculture communities at zero elevation
    def create_flat_agricultural_world(self):
        self.tiles = [community.Community(self.params) for i in range(self.xdim*self.ydim)]
        self.set_neighbours()
        # Each tile is its own polity
        self.polities = [polity.Polity([tile]) for tile in self.tiles]

    # Attempt to spread military technology in all communities
    def diffuse_military_tech(self):
        for tile in self.tiles:
            if tile.terrain is community.Terrain.agriculture:
                tile.diffuse_military_tech(self.params)

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
        for tile in self.tiles:
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
        # Diffuse military technology
        self.diffuse_military_tech()

        # Cultural shift
        self.cultural_shift()

        # Disintegration
        self.disintegration()

        # Attacks
        self.attack()
