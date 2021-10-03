# guard [![Build Status](https://travis-ci.com/alan-turing-institute/guard.svg?token=QpRTp1bT17BnXV9jtJ6H&branch=master)](https://travis-ci.com/alan-turing-institute/guard) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/alan-turing-institute/guard/master)

This repository contains code and data to reproduce results from Madge et al. 2019. "Simulating Imperial Dynamics and Conflict in the Ancient World". https://arxiv.org/abs/1903.11729, which expands upon Turchin et al. 2013. "War, space, and the evolution of Old World complex societies". https://doi.org/10.1073/pnas.1308825110.

This work is part of the project [GUARD: Global Urban Analytics for Resilient Defence](https://www.turing.ac.uk/research/research-projects/global-urban-analytics-resilient-defence).

## Data

The data used to generate figures in the publication are located in the 'data'
directory.

We use three datasets:
1. Historical imperial density data from Turchin et al. 2013. "War, space, and the evolution of Old World complex societies". https://doi.org/10.1073/pnas.1308825110 and Bennett, James. 2016. "Repeated Demographic-Structural Crises Propel the Spread of Large-Scale Agrarian States Throughout the Old World." Cliodynamics: The Journal of Quantitative History and Cultural Evolution 7 (1). https://doi.org/10.21237/C7CLIO7128530.
2. Population data from Reba, Meredith, Femke Reitsma, and Karen C. Seto. 2016. "Spatializing 6,000 Years of Global Urbanization from 3700 BC to AD 2000." Scientific Data 3 (June): 160034. https://doi.org/10.1038/sdata.2016.34.
3. Conflict data from nodegoat (February 2016): https://nodegoat.net/blog.p/82.m/14/a-wikidatadbpedia-geography-of-violence.

## Examples

Example simulations and validations of the model against historical data are
given in the notebooks directory.

Try the examples using binder [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/alan-turing-institute/guard/master).

## Testing

The pytest module is required for testing (`pip install pytest`). The tests may
be run with the command `python -m pytest`.

## Dependancies

- Python >= 3.6
- matplotlib
- numpy
- pyyaml
- scipy

## Citation

Please cite as: Madge, Jim, Giovanni Colavizza, James Hetherington, Weisi Guo, and Alan Wilson. 2019. "Simulating Imperial Dynamics and Conflict in the Ancient World". https://arxiv.org/abs/1903.11729.

    @article{madge_simulating_2019,
      title = {Simulating {Imperial} {Dynamics} and {Conflict} in the {Ancient} {World}},
      url = {https://arxiv.org/abs/1903.11729},
      abstract = {The development of models to capture large-scale dynamics in human history is one of the core contributions of the cliodynamics field. Crucially and most often, these models are assessed by their predictive capability on some macro-scale and aggregated measure, compared to manually curated historical data. We consider the model predicting large-scale complex societies from Turchin et al. (2013), where the evaluation is done on the prediction of “imperial density”: the relative frequency with which a geographical area belonged to large-scale polities over a certain time window. We implement the model and release both code and data for reproducibility. Furthermore, we assess its behaviour against three historical data sets: the relative size of simulated polities vs historical ones; the spatial correlation of simulated imperial density with historical population density; the spatial correlation of simulated conflict vs historical conflict. At the global level, we show good agreement with the population density (R2 {\textless} 0.75), and some agreement with historical conflict in Europe (R2{\textless}0.42, a lower result possibly due to historical data bias). Despite being overall good at capturing these important effects, the model currently fails to reproduce the shapes of individual imperial polities. Nonetheless, we discuss a way forward by matching the probabilistic imperial strength from simulations to inferred networked communities from real settlement data.},
      author = {Madge, Jim and Colavizza, Giovanni and Hetherington, James and Guo, Weisi and Wilson, Alan},
      year = {2019}
    }
