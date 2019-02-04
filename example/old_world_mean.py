#!/usr/bin/env python3
import os
import sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from guard import world, analysis
from guard.parameters import defaults
from guard.community import DIRECTIONS

params = defaults

n_sim = 20
imperial_density = []
date_ranges = analysis.imperial_density_date_ranges

for sim in range(n_sim):
    map_ = world.World(params=params, from_file=project_dir+'/data/old_world.yml')
    imperial_density.append(analysis.ImperialDensity(map_))
    for step in range(1500):
        map_.step()
        imperial_density[sim].sample()
        if (map_.step_number)%100 == 0:
            print('simulation: {:2d}\tstep: {:4d}'.format(sim+1,map_.step_number))

# Average imperial density for all simulations
mean_impd = analysis.ImperialDensity(map_)
for era in date_ranges:
    mean_impd.imperial_density[era] = sum([run.imperial_density[era] for run in imperial_density])
    mean_impd.imperial_density[era] = mean_impd.imperial_density[era] / n_sim

mean_impd.export(normalise=True,highlight_steppe=False)
mean_impd.dump('./imperial_density.pkl')
