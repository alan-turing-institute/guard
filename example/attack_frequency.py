#!/usr/bin/env python3
import os
import sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from guard import world, analysis
from guard.parameters import defaults

params = defaults

date_ranges = [
        analysis.DateRange(0,500),
        analysis.DateRange(500,1000),
        analysis.DateRange(1000,1100),
        analysis.DateRange(1100,1200),
        analysis.DateRange(1200,1300),
        analysis.DateRange(1300,1400),
        analysis.DateRange(1400,1500)]

map_ = world.World(params=params, from_file=project_dir+'/data/old_world.yml')
attack_frequency = analysis.AttackEvents(map_, date_ranges=date_ranges)

for step in range(1500):
    map_.step(attack_frequency.sample)
    if (map_.step_number)%100 == 0:
        print('step: {:4d}\tyear: {:d}'.format(map_.step_number, map_.year()))

attack_frequency.plot()
