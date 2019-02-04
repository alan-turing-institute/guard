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
imperial_density = analysis.ImperialDensity(map_)

historical_data = pickle.load(open(project_dir+'/data/imperial_density_data.pkl', 'rb'))

for era in historical_data:
    imperial_density.imperial_density_eras.append(era/10.)

imperial_density.export(normalise=False,highlight_steppe=False)
