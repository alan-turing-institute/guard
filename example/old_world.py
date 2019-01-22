#!/usr/bin/env python3
import os
import sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from guard import world, analysis
from guard.parameters import defaults

params = defaults

map_ = world.World(params=params, from_file=project_dir+'/data/old_world.yml')
imperial_density = analysis.ImperialDensity(map_)

for step in range(1500):
    map_.step()
    imperial_density.sample()
    if (map_.step_number)%100 == 0:
        print('step: {:4d}'.format(step+1))

    if (map_.step_number)%250 == 0:
        analysis.plot_military_techs(map_)
        analysis.plot_ultrasocietal_traits(map_)

imperial_density.export(normalise=True,highlight_steppe=True)
