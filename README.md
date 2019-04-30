# guard [![Build Status](https://travis-ci.com/alan-turing-institute/guard.svg?token=QpRTp1bT17BnXV9jtJ6H&branch=master)](https://travis-ci.com/alan-turing-institute/guard) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/alan-turing-institute/guard/master)
GUARD: Global Urban Analytics for Resilient Defence

An agent-based model for the evolution of large scale empires in the historical
world, based on [the work of Peter
Turchin](https://doi.org/10.1073/pnas.1308825110).

An analysis of simulation results and the models ability to predict empires,
population and battles are presented in [our
publication](https://arxiv.org/abs/1903.11729).

## Data

The data used to generate figures in the publication are located in the 'data'
directory.

Try the examples using binder [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/alan-turing-institute/guard/master).

## Examples

Example simulations and validations of the model against historical data are
given in the notebooks directory.

## Testing

The pytest module is required for testing (`pip install pytest`). The tests may
be run with the command `python -m pytest`.

## Dependancies

- Python >= 3.6
- matplotlib
- numpy
- pyyaml
- scipy
