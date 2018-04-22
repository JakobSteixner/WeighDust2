#!/usr/bin/python
print "This script plots dust loads and dust transport rates over time from gribfiles"
import sys
import subprocess as sb


dates, hours = range(11,19), (0, 12)
trname, dcname = "Transport_rate_map_2018-04-{}_{}.png", "D_concentration_map_2018-04-{}_{}.png"
print dates, hours



from matplotlib.mlab import prctile_rank
print "importing  plt"
import matplotlib.pyplot as plt
print "importing numpy"
import numpy as np
print "importing Basemap"
print "importing pygrib"
import pygrib
from mpl_toolkits.basemap import Basemap as Basemap
import scipy.interpolate

mymap = Basemap(projection="aeqd",lat_0=48,lon_0=16, width=4000000, height=4000000)

def plot_transport_rate(savefilename = None):
        if savefilename == None:
                savefilename = trname.format(date, str(hour).rjust(2,"0"))
                print savefilename, "savefilename"
        print "plotting contourplot"
        mymap.contourf(x,y,aggregated_transport_rate,np.arange(-100,110,10) ** 3 * 0.00000005 ,cmap=plt.cm.jet)
        mymap.colorbar()
        mymap.drawcoastlines()
        plt.title("N-S dust transport rate, 2018-04-{}, {}:00".format(date, str(hour).rjust(2,"0")))
        plt.plot(*mymap(np.arange(8,29), np.zeros(21)+38),color="black")
        plt.savefig(savefilename)
        #plt.show() # uncomment for interactive version
        plt.close()

def plot_dust_density(savefilename = None):
        if savefilename == None:
                savefilename = dcname.format(date, str(hour).rjust(2,"0"))
                print savefilename, "savefilename"
        """should probably be refactured into a single function with the one above"""
        print "plotting concentrations"
        mymap.contourf(x,y,aggregateddust,np.arange(0,20) ** 1.5 * 0.00004 , cmap=plt.cm.jet)
        mymap.colorbar()
        mymap.drawcoastlines()
        plt.plot(*mymap(np.arange(8,29), np.zeros(21)+38),color="black")
        plt.title("Dust concentration, 2018-04-{}, {}:00".format(date, str(hour).rjust(2,"0")))
        plt.savefig(savefilename)
        #plt.show() # uncomment for interactive version
        plt.close()

def interpolate_totals(xs,ys, kind = "linear"):
    """returns an array of interpolated aggregate values per lat/lon,
    for use with pressure-level-data.
    input:
    xs = array of geopotential heights
    ys = array of data to be aggregated (e. g. pollutant concentrations
    per m3 for aggregated pollutant load per m2, windspeeds * densities
    for air transport, windspeeds * pollutant concentrations for pollutant
    transport rates...)

    """
    return np.array([[scipy.interpolate.interp1d(
                                            xs[:,lat,lon],
                                            ys[:,lat,lon],
                                            kind=kind,
                                            fill_value="extrapolate"
                                        )(np.arange(0,15000,50)).sum() * 50 for lon in range(longridpoints)] for lat in range(latgridpoints)
                                    ]
                                )

def get_data_by_name(name, gribfile, **kwargs):
    """name = string = identifier of the gribmessage type to be collected
    gribfile = iterable of gribmessages
    kwargs (not implemented atm) = further restrictions, e.g. selecting for
    date/time/step if file is multi-day"""
    return np.array([[msg.data()[0] for msg in gribfile if msg.step == 0 and msg.level == level and msg.name == name][0] for level in levels])

for date in dates:
    for hour in hours:
        print date, hour
      #if (dcname.format(date, hour) in sb.check_output(("ls"))
      #          and trname.format(date, hour) in sb.check_output(("ls"))):
      #          print "we did this before"
      #else:
      #  exit()
        print "loading dustflie"
        dustraw = [msg for msg in
                    pygrib.open("dust_concentrations2018-04-{}-{}:00:00.grib".format(str(date), str(hour).rjust(2,"0")))
                    if msg.step == 0]
        print "loading tempfile"
        tempraw = [msg for msg in
                    pygrib.open("temp_v_gh2018-04-{}-{}:00:00.grib".format(str(date), str(hour).rjust(2,"0")))
                    if msg.step == 0]

        #print [msg for msg in tempraw]
        levels = set([msg.level for msg in tempraw])
        #print levels
        latgridpoints = len(msg.data()[0])
        longridpoints = len(msg.data()[0][0])
        print "gridpoints along lons,lats", longridpoints, latgridpoints
        
        altitudes = get_data_by_name("Geopotential Height", tempraw)
        temperatures = get_data_by_name("Temperature", tempraw)
        totaldustmmr = np.array([np.array(np.sum([msg.data()[0] for msg in dustraw if msg.step == 0 and msg.level == level], 0)) for level in levels])
        
        densities = np.array([100 * level / (287.058 * temperatures[idx]) for idx,level in enumerate(levels)])

        dustmasses = densities * totaldustmmr
        
        windspeeds = np.array([[msg.data()[0] for msg in tempraw if msg.step == 0 and msg.level == level and msg.name == "V component of wind"][0] for level in levels])
        print "done defining alt  - windspeeds"
        print "attempting to calculate aggregate dust mass per m2"
        aggregateddust = interpolate_totals (altitudes, dustmasses)
        print "attempting to caclulate transport rates"
        aggregated_transport_rate = interpolate_totals(altitudes, dustmasses * windspeeds)
        print "done calculating aggregated values"
        
        #feedback about maximum values, useful for setting adequate thresholds in aggregate functions' colormaps
        print "transport rates ranging up to ", np.max(np.abs(aggregated_transport_rate))
        print "dust/m2 ranging up to ", np.max(aggregateddust)
        
        print "getting coordinates for values"
        x = msg.data()[2]
        y = msg.data()[1]
        x,y = mymap(x,y)
        plot_transport_rate()
        plot_dust_density()
        
