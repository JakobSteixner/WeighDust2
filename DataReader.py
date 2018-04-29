#/usr/bin/python

import numpy as np
import pygrib
import scipy.interpolate
import itertools

earthradius = 6388000. 

try: trname, dcname = open(".mapnametemplate", "r").readlines()
except: trname, dcname = "Transport_rate_map_2018-04-{}_{}.png", "D_concentration_map_2018-04-{}_{}.png"

try: inputdusttemplate, inputtemptemplate = [s.strip() for s in open(".inputfilenametemplate", "r").readlines()]
except: inputdusttemplate, inputtemptemplate = "dust_concentrations2018-04-{}-{}:00:00.grib", "temp_v_gh2018-04-{}-{}:00:00.grib"

print inputdusttemplate, inputtemptemplate
print trname, dcname

def parlength(par, segment=360, radius = earthradius):
        return radius * np.cos(np.radians(par)) * np.radians(segment)

def meridianlength(segment=180, radius = earthradius):
        if segment == 180:
                return np.pi * radius
        else:
                return radius * np.radians(segment)


def interpolate_totals(xs,ys, size, kind = "linear", force_abs = False):
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
        latgridpoints, longridpoints = size
        return np.array([[[scipy.interpolate.interp1d(
                                            xs[i,:,lat,lon],
                                            ys[i,:,lat,lon],
                                            kind=kind,
                                            fill_value="extrapolate"
                                        )(np.arange(0,15000,50)).sum() * 50 for lon in range(longridpoints)] for lat in range(latgridpoints)
                                    ]
                                for i in range(len(xs))]
                                )

class TypedData():
    def __init__(self, array, name, daterange, unit):
        self.data = array
        self.name = name
        self.daterange = daterange
        self.unit = unit
    def __repr__(self):
        return repr(self.data)

class DataReader:
    def __init__(self, timeslots,
                 dusttemplate = inputdusttemplate,
                 temptemplate = inputtemptemplate,
                 multidayfiles = False,
                 area = [40,121,0,121]
                 ):
        self.dates = min(timeslots[0]), max(timeslots[0])
        timeslots = list(itertools.product(*timeslots))
        self.gribdata_temps, self.gribdata_dust = [],[]
        #self.gribdata_temps, self.gribdata_dust = {}, {}
        # self.
        #if multidayfiles == True:
        #        pass # not implemented
        #else:
        for slot in [s for s in timeslots]:
                try:
                    self.gribdata_dust.append([msg for msg in
                        pygrib.open(dusttemplate.format(*[str(field).rjust(2,"0") for field in slot]))
                        if msg.step == 0])
                    self.gribdata_temps.append([msg for msg in
                        pygrib.open(temptemplate.format(*[str(field).rjust(2,"0") for field in slot]))
                        if msg.step == 0])
                    print "loaded data for", slot
                except:
                    timeslots.remove(slot)
                    print "no data available for", slot
        self.timeslots = timeslots
        self.grid = abs(msg.data()[2][0][1] - msg.data()[2][0][0]) % 360.0
        
        self.levels = levels = set([msg.level for msg in self.gribdata_dust[0]])
        area = np.array(area)
        print area
        print 90.-area[:2], self.grid
        self.areaindices = ((np.arange(*(90.-area[:2])/self.grid)).astype(int),
                (np.arange(*area[2:]/self.grid)%(360./self.grid)).astype(int))
        print self.areaindices
        rnl, rwl = rawnorthernlimit, rawwesternlimit = msg.data()[1][0][0], msg.data()[2][0][0]
        
        self.dataformatsample = np.array(msg.data())[:][:,self.areaindices[0]][:,:,self.areaindices[1]]
        print self.dataformatsample.shape
        #,np.arange(*self.area[;2],self.grid),np.arange(*self.area(2:),self.grid)] # assumes all input data has same grid and geographical coverage
        self.maplimits = (northernlimit, southernlimit, westernlimit, easternlimit) = list(self.dataformatsample[1,(0,-1),0]) + list(self.dataformatsample[2,0,(0,-1)])
        self.size = latgridpoints, longridpoints = self.dataformatsample.shape[1:]
        #self.gribdata_temps = np.array(self.gribdata_temps)
        self.extract()
        self.timeslots = np.array(self.timeslots)
    def get_data_in_range(self, msg):
        #print msg.data()
        #print np.array(msg.data()).shape
        #print np.array(msg.data())[0,self.areaindices[0],self.areaindices[1]].shape
                
        return np.array(msg.data())[0][self.areaindices[0]][:,self.areaindices[1]]
    def get_data_by_name(self, name, gribfile, **kwargs):
        """name = string = identifier of the gribmessage type to be collected
        gribfile = iterable of gribmessages
        kwargs (not implemented atm) = further restrictions, e.g. selecting for
        date/time/step if file is multi-day"""
        try:
                return np.array([[self.get_data_in_range(msg) for msg in gribfile if msg.level == level and msg.name == name][0] for level in self.levels])
        except:
                #print gribfile[0]
                return np.array([self.get_data_by_name(name,subarray) for subarray in gribfile])
    def extract(self):
        print set([msg.name for msg in self.gribdata_dust[0]])
        self.totaldustmmr = TypedData(
                np.array(
                        np.sum([self.get_data_by_name(name, self.gribdata_dust)
                                 for  name in set([msg.name for msg in self.gribdata_dust[0]])],0)),
                "Dust by mass", self.dates, unit="kg kg$^{-1}$"
                )
        print "extracted dust mmrs (sums)"
        print self.totaldustmmr.data.shape
        del self.gribdata_dust
        del msg
        
        self.altitudes = TypedData(self.get_data_by_name("Geopotential Height",self.gribdata_temps),
                "Altitudes", self.dates, unit="m"
                )
        print "successfully extracted altitudes with new formula"
        print self.altitudes.data.shape
        self.temperatures = TypedData(self.get_data_by_name("Temperature", self.gribdata_temps),
                "Temperature", self.dates, unit = "K"
                )
        print "extracted temperatures"
        self.windspeeds = TypedData(self.get_data_by_name("V component of wind", self.gribdata_temps),
                "Wind speeds (N-S component)", self.dates, unit="m s$^{-1}$"
                )
        print "extracted windspeeds"
        del self.gribdata_temps
        
        self.airdensities = TypedData(
                np.array(
                        [100 * level / (287.058 * self.temperatures.data[:,idx])
                         for idx,level in enumerate(self.levels)]).transpose(1,0,2,3),
                "Air density", self.dates, unit = "kg m$^{-3}$"
                )
        print "calculated air densities"
        #print self.totaldustmmr.shape
        self.dustmasses = TypedData(self.airdensities.data * self.totaldustmmr.data, "Dust concentrations", self.dates, unit="kg m$^{-3}$")
        #assert self.dustmasses.shape == self.altitudes.shape
        print "interpolating aggregated dust masses / m2"
        
        self.aggregateddust = TypedData(
                interpolate_totals (self.altitudes.data, self.dustmasses.data, self.size),
                "Column dust load", self.dates, unit="kg m$^{-2}$"
                )
        #print "interpolating N-S net dust transport rates / m"
        #self.aggregatedrate = TypedData(
        #        interpolate_totals (self.altitudes.data, self.dustmasses.data * self.windspeeds.data, self.size),
        #        "Net N-S dust transfer rate", self.dates, unit="kg m$^{-1}$ s^${-1}$"
        #        )
        #print "interpolating absolute rates"
        #abstransports = interpolate_totals(self.altitudes.data, self.dustmasses.data * self.windspeeds.data, self.size, force_abs=True)
        #southward = (abstransports - self.aggregatedrate.data) / 2.0
        #self.grosstransport = TypedData(
        #        abstransports - southward,
        #        "Gross northward dust transfer", self.dates, "kg m$^{-1}$ s^${-1}$"
        #        )
        #assert self.grosstransport.data.shape == self.aggregatedrate.data.shape
    def findclosest(self, formatsample, value, indexingcorrection=False, maxdiff = 3):
            """Find closest grid point if coorinates do not exactly
            match any available grid point. Parameters:
            formatsample: sample gribmessage.data() array with the
                        correct dimensions and coordinate values
            value: latitude or lontitude (float)
            indexingcorrection: boolean, call with True for the
                        second lontitude or latitude
            maxdiff: maximal allowable distance.
            """
            #print "No precise match found for coordinate", value
            if value in formatsample:
                    #print "about to return", (value, np.nonzero(value == formatsample)[0][0])
                    return [value, np.nonzero(value == formatsample)[0][0]]
            else:
                    print "value {} not found in data, attempting to find closest".format(value)
                    diffs = [abs(datapoint-value) for datapoint in formatsample]
                    closest = min(diffs)
                    #print diffs, closest
                    if closest < maxdiff: # proceed with closest value if less then maxdiff degrees out of range
                                    lat0idx = np.nonzero(closest == diffs)[0][0]
                                    lat0 = formatsample[lat0idx]
                                    print "Using latitude", lat0, "instead."
                                    return [lat0, lat0idx]
                    else:
                            print "Coordinate Out of range, please pick a different value"
                            raise IndexError
    def get_x_y(self, lat0=None, lat1=None, lon0=None, lon1=None):
        """input: latitude(s) and/or lontitude(s) of area of interest.
        returns index ranges in grib data of desired lats/lons.
        if only latitudes or only lontitudes are given, returns entire
        range along the other. If only lat0 and/or lon0 are given, returns
        a line."""
        dataformatsample = self.dataformatsample
        findclosest = self.findclosest
        if lat0 == None and lon0 == None:
                print "Please specify at least one of lat0, lon0!"
                return None
        if lat0 != None:
                lat0 = findclosest(dataformatsample[1,:,0], lat0)
                if lat1 != None:
                        lat1 = findclosest(dataformatsample[1,:,0], lat1, True)
                else:
                        lat1 = dataformatsample[1,lat0[1],0], lat0[1]+1 
        if lon0 != None:
                lon0 = findclosest(dataformatsample[2,0,:], lon0)
                if lon1 != None:
                        lon1 = findclosest(dataformatsample[2,0,:], lon1, True)
                else: lon1 = dataformatsample[2,0,lon0[1]], lon0[1]+1
        limits = self.maplimits; latgridpoints, longridpoints = self.size - np.array(1)
        limitsasindex = 0, latgridpoints, 0, longridpoints
        coords = [lat0, lat1, lon0,lon1]
        for idx,coord in enumerate((lat0, lat1, lon0,lon1)):
                print coord
                if coord == None:
                        coord = (limits[idx], limitsasindex[idx])
                        coords[idx] = coord
        
        if coords[1] <= coords[0]:
                coords[1] = coords[0] + np.array((0,1))
        if coords[3] <= coords[2]:
                coords[3] = coords[2] + np.array((0,1))
        return np.array(coords)