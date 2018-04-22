Quick Description
===========

A set of scripts to plot dust concentrations (or rather, aggregate dust
loads per square meter surface, which may be more useful for many application) and/or dust transport rates (with current parameters, only alon north-south-axis).

Requirements
====

python >= 2.4 < 3 (according to the specifications in my version of Basemap), tested in python 2.7.14

Packages: matplotlib, numpy, scipy, pygrib, gribapi, basemap

Pygrib in particular may (or may not -- I only started to work with it after taking a go at the wgrib2's C interface) require the installataion of [wgrib2](http://www.cpc.noaa.gov/products/wesley/wgrib2/). 

For downloading the raw data, you need a free account with the [European Centre for Medium Range Weather Forecasts](https://www.ecmwf.int/). After agreeing with their Terms of Use, you get a user key in JSON forma which you have to store as `.ecmwfapirc` in your home directory.

Usage
===
Just a couple scripts at the moment...

`python request.py` (pulls the required data from ECMWF; most of the keys in the request syntax are self explanatory, if you need more details, start [here](https://software.ecmwf.int/wiki/display/WEBAPI/Brief+MARS+request+syntax))
`python mapdust.py` (draws the maps)

Optionally (assumes you have ImageMagick installed) to create animated gifs:
`convert -delay 150 -loop 0 D_concentration_map_*.png Dust_concentrations.gif`
`convert -delay 150 -loop 0 Transport_rate*.png Transport_rates.gif`
 
Legal
===

No warranty, free reuse (Public Domain
Legal
===

No warranty, free reuse (Public Domain).
