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

n_sim = 20
attack_frequency = []

for run in range(n_sim):
    map_ = world.World(params=params, from_file=project_dir+'/data/old_world.yml')
    attack_frequency.append(analysis.AttackEvents(map_, date_ranges=date_ranges))

    for step in range(1500):
        map_.step(attack_frequency[run].sample)
        if (map_.step_number)%100 == 0:
            print('simulation: {:d}\tstep: {:4d}\tyear: {:d}'.format(run, map_.step_number, map_.year()))

mean_attack_frequency = analysis.AttackEvents(map_, date_ranges=date_ranges)
for era in date_ranges:
    mean_attack_frequency.attacks[era] = sum([run.attacks[era] for run in attack_frequency])
    mean_attack_frequency.attacks[era] = mean_attack_frequency.attacks[era] / n_sim

mean_attack_frequency.dump('attack_frequency.pkl')


#map_ = world.World(params=params, from_file=project_dir+'/data/old_world.yml')
#mean_attack_frequency = analysis.AttackEvents(
#    map_,
#    from_file='./attack_frequency.pkl')

mean_attack_frequency.plot()

battles = analysis.Battles(map_, date_ranges, project_dir+'/data/battles.yml')
battles.plot_heatmap()
battles.correlate(mean_attack_frequency)
