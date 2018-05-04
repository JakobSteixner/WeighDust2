Quick Description
===========

A set of scripts to plot dust concentrations (or rather, aggregate dust
loads per square meter surface, which may be more useful for many application) and/or dust transport rates (with current parameters, only along north-south-axis).

Requirements
====

python >= 2.4 < 3 (according to the specifications in my version of Basemap), tested in python 2.7.14

Packages: matplotlib, numpy, scipy, pygrib, gribapi, basemap

Pygrib in particular may (or may not -- I only started to work with it after taking a go at the wgrib2's C interface) require the installataion of [wgrib2](http://www.cpc.noaa.gov/products/wesley/wgrib2/). 

For downloading the raw data, you need a free account with the [European Centre for Medium Range Weather Forecasts](https://www.ecmwf.int/). After agreeing with their Terms of Use, you get a user key in JSON forma which you have to store as `.ecmwfapirc` in your home directory.

Usage
===

The script `request.py` (pulls the required data from ECMWF; most of the keys in the request syntax are self explanatory, if you need more details, start [here](https://software.ecmwf.int/wiki/display/WEBAPI/Brief+MARS+request+syntax)) can be used to pull data from the ECMWF's repository.
It requires the ECMWFapi module and a (free) registration to obtain a user key. Once the raw data are available, there are two options:

Modular version
---------
`DataReader` parses the `.grib`-files, `plottingtools` has two classes specially designed to deal with DR's output, one for producing maps (using Basemap), the other one for line graphs.

The script `sample.py` illustrates these module's use.

Script version
---------
A single fully functioning script prototype is also available as `mapdust.py`.
`python mapdust.py` (draws the maps)
 
Legal
===

No warranty, free reuse (Public Domain)
