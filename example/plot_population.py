#!/usr/bin/env python3
import os
import sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from guard import world, analysis
from guard.parameters import defaults
import pickle

params = defaults

map_ = world.World(params=params, from_file=project_dir+'/data/old_world.yml')
population = analysis.CitiesPopulation(map_, data_file=project_dir+'/data/cities.yml')

population.plot_population_heatmap()
#population.plot_population_heatmap(blur=3.0)
