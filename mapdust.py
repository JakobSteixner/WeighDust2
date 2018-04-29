#!/usr/bin/python
# -*- coding: utf8 -*-

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
        """should probably be rewritten a single function with the one above"""
        print "plotting concentrations"
        mymap.contourf(x,y,aggregateddust,np.arange(0,20) ** 1.5 * 0.00004 , cmap=plt.cm.jet)
        mymap.colorbar()
        mymap.drawcoastlines()
        plt.plot(*mymap(np.arange(8,29), np.zeros(21)+38),color="black")
        plt.title("Dust concentration, 2018-04-{}, {}:00".format(date, str(hour).rjust(2,"0")))
        plt.savefig(savefilename)
        #plt.show() # uncomment for interactive version
        plt.close()

def interpolate_totals(xs,ys, kind = "linear", force_abs = False):
    """returns an array of interpolated aggregate values per lat/lon,
    for use with pressure-level-data.
    input:
    xs = array of geopotential heights
    ys = array of data to be aggregated (e. g. pollutant concentrations
    per m3 for aggregated pollutant load per m2, windspeeds * densities
    for air transport, windspeeds * pollutant concentrations for pollutant
    transport rates...)

    """
    if force_abs:
        ys = abs(ys)
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

def findclosest(formatsample, value, maxdiff = 3):
        print value, formatsample
        if value in formatsample:
                #print "about to return", (value, np.nonzero(value == formatsample)[0][0])
                return (value, np.nonzero(value == formatsample)[0][0])
        else:
                print "value {} not found in data, attempting to find closest".format(value)
                diffs = [abs(datapoint-value) for datapoint in formatsample]
                closest = min(diffs)
                #print diffs, closest
                if closest < 3: # proceed with closest value if less then 3 degrees out of range
                                lat0idx = np.nonzero(closest == diffs)[0][0]
                                print lat0idx
                                lat0 = formatsample[lat0idx]
                                print "using latitude", lat0, "instead..."
                                print "about to return", (lat0, lat0idx)
                                return (lat0, lat0idx)
                else:
                        print "out of range, please pick a different value"
                        raise IndexError
                
        


def get_x_y(lat0=None, lat1=None, lon0=None, lon1=None):
        """input: latitude(s) and/or lontitude(s) of area of interest.
        returns index ranges in grib data of desired lats/lons.
        if only latitudes or only lontitudes are given, returns entire
        range along the other. If only lat0 and/or lon0 are given, returns
        a line."""
        if lat0 == None and lon0 == None:
                print "Please specify at least one of lat0, lon0!"
                return None
        if lat0:
                lat0 = findclosest(dataformatsample[1,:,0], lat0)
                if lat1:
                        lat1 = findclosest(dataformatsample[1,:,0], lat1)
                else:
                        lat1 = lat0
        if lon0:
                lon0 = findclosest(dataformatsample[2,0,:], lon0)
                if lon1:
                        lon1 = findclosest(dataformatsample[2,0,:], lon1)
                else: lon1 = lon0
        limits = northernlimit, southernlimit, westernlimit, easternlimit
        limitsasindex = 0, latgridpoints, 0, longridpoints
        coords = [lat0, lat1, lon0,lon1]
        for idx,coord in enumerate((lat0, lat1, lon0,lon1)):
                if coord == None:
                        coords[idx] = (limits[idx], limitsasindex[idx])
        return np.array(coords)
 
def parlength(par, seg=360):
        earthradius = 6388000.
        return earthradius * np.cos(np.radians(par)) * np.radians(seg)
        
class DataReader:
    def __init__(self, timeslots,
                 dusttemplate = "dust_concentrations2018-04-{}-{}:00:00.grib",
                 temptemplate = "temp_v_gh2018-04-{}-{}:00:00.grib",
                 ):
        dates, hours = timeslots
        gribdata_temps, gribdata_dust = [], []
        for date in dates:
            for hour in hours:
                try:
                    print "loading dustflie"
                    gribdata_dust.append([msg for msg in
                            pygrib.open(dusttemplate.format(str(date).rjust(2,"0"), str(hour).rjust(2,"0")))
                            if msg.step == 0])
                    print "loading tempfile"
                    gribdata_temps.append([msg for msg in
                            pygrib.open(temptemplate.format(str(date).rjust(2,"0"), str(hour).rjust(2,"0")))
                            if msg.step == 0])
                
                except IOError:
                    break
        
        
        

alldustmasses, allaggregatemasses, allaggregaterates = [], [], []
aggregatedrates_gross, par38gross = [], []
par38dustmasses, par38aggregatemasses, par38aggregaterates = [],[],[]
for date in dates:
    for hour in hours:
        print date, hour
      #if (dcname.format(date, hour) in sb.check_output(("ls"))
      #          and trname.format(date, hour) in sb.check_output(("ls"))):
      #          print "we did this before"
      #else:
      #  exit()
        try:
                print "loading dustflie"
                dustraw = [msg for msg in
                            pygrib.open("dust_concentrations2018-04-{}-{}:00:00.grib".format(str(date).rjust(2,"0"), str(hour).rjust(2,"0")))
                            if msg.step == 0]
                print "loading tempfile"
                tempraw = [msg for msg in
                            pygrib.open("temp_v_gh2018-04-{}-{}:00:00.grib".format(str(date).rjust(2,"0"), str(hour).rjust(2,"0")))
                            if msg.step == 0]
                
        except IOError:
                break
        dataformatsample = np.array(msg.data())
        
        #print [msg for msg in tempraw]
        levels = set([msg.level for msg in tempraw])
        westernlimit, easternlimit = dataformatsample[2,0,(0,-1)]
        northernlimit, southernlimit = dataformatsample[1,(0,-1),0]
        print dataformatsample[2,0,(0,-1)], type(dataformatsample[2,0,(0,-1)])
        #print levels
        latgridpoints, longridpoints = dataformatsample.shape[1:3]

        print "gridpoints along lons,lats", longridpoints, latgridpoints
        print "testing get_x_y"
        print get_x_y(50,44.4,10.78,16)
        print get_x_y(50,None,10.78,None)
        par38seg = get_x_y(38,38, 8, 28)
        print get_x_y(38)
        #exit()
        
        altitudes = get_data_by_name("Geopotential Height", tempraw)
        temperatures = get_data_by_name("Temperature", tempraw)
        totaldustmmmrnew = np.sum([get_data_by_name(name, dustraw) for name in set([msg.name for msg in dustraw])],0)
        totaldustmmr = np.array([np.array(np.sum([msg.data()[0] for msg in dustraw if msg.step == 0 and msg.level == level], 0)) for level in levels])
        print totaldustmmmrnew.shape
        print totaldustmmr.shape
        print (totaldustmmmrnew == totaldustmmr).all()
        exit()
        densities = np.array([100 * level / (287.058 * temperatures[idx]) for idx,level in enumerate(levels)])
        
        dustmasses = densities * totaldustmmr
        alldustmasses.append(dustmasses)
        
        
        par38mass = dustmasses[:,range(*par38seg[:2,1]+(0,1))][:,:,range(*par38seg[2:,1]+(0,1))]
        print par38mass.shape
        #exit()
        par38dustmasses.append(par38mass)
        
        windspeeds = np.array([[msg.data()[0] for msg in tempraw if msg.step == 0 and msg.level == level and msg.name == "V component of wind"][0] for level in levels])
        print "done defining alt  - windspeeds"
        print "attempting to calculate aggregate dust mass per m2"
        aggregateddust = interpolate_totals (altitudes, dustmasses)
        print aggregateddust.shape
        allaggregatemasses.append(aggregateddust[par38seg[:2,0],par38seg[2:,:]])
        par38aggmass = aggregateddust[range(*par38seg[:2,1]+(0,1))][:,range(*par38seg[2:,1]+(0,1))]
        par38aggregatemasses.append(par38aggmass)
        
        print "attempting to caclulate transport rates"
        aggregated_transport_rate = interpolate_totals(altitudes, dustmasses * windspeeds)
        abstransports = interpolate_totals(altitudes, dustmasses * windspeeds, force_abs=True)
        southward = (abstransports - aggregated_transport_rate) / 2.0
        grosstransport = abstransports - southward
        aggregatedrates_gross.append(grosstransport)
        allaggregaterates.append(aggregated_transport_rate)
        par38aggrate = aggregated_transport_rate[range(*par38seg[:2,1]+(0,1))][:,range(*par38seg[2:,1]+(0,1))]
        par38aggregaterates.append(par38aggrate)
        par38gross.append(grosstransport[range(*par38seg[:2,1]+(0,1))][:,range(*par38seg[2:,1]+(0,1))])
        print "done calculating aggregated values"
        
        #feedback about maximum values, useful for setting adequate thresholds in aggregate functions' colormaps
        print "transport rates ranging up to ", np.max(np.abs(aggregated_transport_rate))
        print "dust/m2 ranging up to ", np.max(aggregateddust)
        plt.plot(np.arange(8,28.5, 0.5), par38aggmass[0,:])
        plt.plot(np.arange(8,28.5, 0.5), par38aggrate[0,:])
        plt.title("Parallal 38, 2018-04-{}, {}:00".format(date, hour))
        plt.plot((8,28), (0,0))
        plt.ylim(-0.02,0.05)
        plt.xlim(8,28)
        plt.savefig("par38rates{}_{}.png".format(date,hour))
        plt.close()
        
        
        print "getting coordinates for values"
        x = msg.data()[2]
        y = msg.data()[1]
        x,y = mymap(x,y)
        plot_transport_rate()
        plot_dust_density()

#par38aggregaterates = np.array(par38aggregaterates)
#par38gross = np.array(par38gross)
plt.plot(np.arange(0,0.5 * len(par38aggregaterates),0.5)+min(dates), np.average(par38aggregaterates,2) * parlength(38, 20) * 3600, label= "net")
plt.plot(np.arange(0,0.5 * len(par38aggregaterates),0.5)+min(dates), np.average(par38gross,2) * parlength(38, 20) * 3600, label= "gross northward")
#plt.plot(np.arange(0,len(dates),0.5)+min(dates), np.average()
plt.title(u"Mass transport across 38th parallel, 8-28° E")
#plt.ylim(min((np.min(par38aggregaterates) * 1.05, 0)),max((0, np.max(par38aggregaterates) * 1.05)))
plt.ylabel("kg/hour")
plt.xlabel("Days")
plt.legend(loc='upper left')
plt.savefig("par38totals.png")
plt.show()