#!/usr/bin/env python3
import os
import sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from guard import world, analysis
from guard.parameters import defaults

params = defaults

date_ranges = [analysis.DateRange(-1000,0),
        analysis.DateRange(0,500),
        analysis.DateRange(500,1000),
        analysis.DateRange(1000,1100),
        analysis.DateRange(1100,1200),
        analysis.DateRange(1200,1300),
        analysis.DateRange(1300,1400),
        analysis.DateRange(1400,1500)]

map_ = world.World(params=params, from_file=project_dir+'/data/old_world.yml')
imperial_density = analysis.ImperialDensity(map_, date_ranges=date_ranges)
population = analysis.CitiesPopulation(map_, data_file=project_dir+'/data/cities.yml', date_ranges=date_ranges)

for step in range(1500):
    map_.step()
    imperial_density.sample()
    if (map_.step_number)%100 == 0:
        print('step: {:4d}\tyear: {:d}'.format(map_.step_number, map_.year()))

imperial_density.plot_all(highlight_steppe=False)
imperial_density.dump('./imperial_density.pkl')

#imperial_density = ImperialDensity.from_file(map_,'./imperial_density.pkl')

blur = 3.0
population.plot_population_heatmap(blur=blur)
population.correlate(imperial_density, blur=blur, cumulative=True)
