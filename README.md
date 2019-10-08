# Poi Converter
Reads POIs and creates Locus POI databases

This is a python based command line application that converts POIs (points-of-interest) into the database
format suitable for Locus vector maps.

## Installation:
* install python 3.7 and pipenv
* clone this repository
* run `pipenv update` to download and install the necessary dependencies (pyosmium, pyspatialite and tdqm)
* run `pipenv shell` to activate the virtual environment
* start the tool

```
usage: poiconverter.py [-h] [-version] -if {pbf,poi} -om {create,append}
                       input_file output_file

Extracts POIs from osm file and create Locus poi database

positional arguments:
  input_file           enter input filename
  output_file          enter output spatialite filename (.db)

optional arguments:
  -h, --help           show this help message and exit
  -version             show program's version number and exit
  -if {pbf,poi}        specify input file format
  -om {create,append}  specify output mode: create will newly create database
                       and append will only append new POIs.

```

## Open topics
* only rudimentary error handling implemented
* support for POIs in ways and relations missing in PBF converter
* output tag mapping is hardcoded in python code

## Differences for PBF vs. POI input
* POI input file conversion is at least 10x faster
* POI input will use POIs from nodes, ways and relations, for PBF only nodes are supported currently

## Input file download:
* PBF files: https://download.geofabrik.de/europe/germany/bayern.html
* https://download.geofabrik.de/europe/germany/bayern/oberbayern-latest.osm.pbf
* POI files: https://www.openandromaps.org/downloads/deutschland
* http://download.openandromaps.org/pois/Germany/bayern.poi.zip


More information on the POI database format can be found here:
* https://www.openandromaps.org/oam-forums/topic/poi-nutzbarkeit-der-dateien-mit-locus
* https://gitlab.com/noschinl/locus-poi-db
