# GUARD data

This directory contains the data used to run the simulation and generate the
plots in [our publication](https://arxiv.org/abs/1903.11729).

## old_world.yml
The definition of the simulation map as a list of tiles. This is a
reformulation of Turchin et al. (2013)'s [original
map](https://doi.org/10.1073/pnas.1308825110) into YAML.

## imperial_density_data.pkl
Historical imperial density across three eras as estimated by
[Turchin et al. (2013)](https://doi.org/10.1073/pnas.1308825110).

## cities.yml
A list of cities with locations (in terms of simulation map coordinates) and
populations for a set of historical periods when available. This data was
derived from the data set of [Reba et al.
(2016)](https://www.nature.com/articles/sdata201634)

## battles.yml
A list of historical battles with locations (map coordinates) and date (year
only). This data is the concatenation of the two data sets of historical battles
scrapped from wikidata and dbpedia respectively. The original data, along with
discussion and visualisation, is available on
[nodegoat](https://nodegoat.net/blog.p/82.m/14/a-wikidatadbpedia-geography-of-violence).

## roman_empire.yml
The extent of the Roman empire expressed as sets of occupied tiles at century
intervals. This is derived from a data set of historical empires by
[Turchin et al. (2013)](https://doi.org/10.1073/pnas.1308825110).
