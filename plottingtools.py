import matplotlib.pyplot as plt
     
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import string

earthradius = 6388000.


def parlength(par, segment=360, radius = earthradius):
        return radius * np.cos(np.radians(par)) * np.radians(segment)

def meridianlength(segment=180, radius = earthradius):
        if segment == 180:
                return np.pi * radius
        else:
                return radius * np.radians(segment)


trname, dcname = "Transport_rate_map_2018-04-{}_{}.png", "D_concentration_map_2018-04-{}_{}.png"

class Euromap():
    def __init__(self, centrelat=48.2, centrelon=16.3, citybyname=None, width=4000., height=None,  **kwargs):
        """Wrapper around Basemap with default setting for a
        map centered at Vienna, **kwargs will be passed on to `Basemap`
        * centrelat, centrelon: float; coordinates of centre, default Vienna
        * width, height: float; size of the displayed area, in km (Basemap uses metres!)
          defaults to a quadratic map with base 4000km; stating width alone will result
          in a quadratic map with different base.
        all **kwargs are passed on to `Basemap`
        """
        if height == None:
            height = width
        lat,lon = centrelat, centrelon
        self.mymap = Basemap(projection="aeqd",lat_0=lat,lon_0=lon, width=width * 1000, height=height * 1000, **kwargs)
        
        
    def densitymap_prepare(self, formatsample, array3d, timeslot, countries=False, savefilename = None, scale="posonly", name="Concentration", title=None):
        """Prepares a density map without finalising it.
        Can be called directly for greater freedom to manipulate
        the map, or through self.densitymap
        """
        scales = {"posonly":np.arange(0,20) ** 1.5 * 0.00004, "twosided":np.arange(-100,110,10) ** 3 * 0.000000004}
        try: scale = scales[scale]
        except: #assume that an explicit scale has been provided; 
                scale = scale
        date,hour = timeslot
        if savefilename == None:
                savefilename = dcname.format(date, str(hour).rjust(2,"0"))
                print savefilename, "savefilename"
        print "plotting "+name
        x, y= self.mymap(*reversed(formatsample))
        self.mymap.contourf(x,y,array3d,scale, cmap=plt.cm.jet)
        self.mymap.colorbar()
        self.mymap.drawcoastlines()
        if countries==True:
            self.mymap.drawcountries()
        plt.plot(*self.mymap(np.arange(8,29), np.zeros(21)+38),color="black")
        if not title:
            plt.title(name+ " 2018-04-{}, {}:00".format(date, str(hour).rjust(2,"0")))
        else:
            plt.title(title)
    def densitymap_finalise(self,savefilename):
        """finalises a density map prepared by densitymap_prepare"""
        plt.savefig(savefilename)
        #plt.show() # uncomment for interactive version
        plt.close()
    def densitymap(self, **kwargs):
        """creates and finalises a map in one go"""
        self.densitymap_prepare(**kwargs)
        savefilename=kwargs["savefilename"]
        self.densitymap_finalise(savefilename)

# example usage by :
# em = Euromap()
# for idx,time in enumerate(dr.timeslots): 
#     em.densitymap_prepare(dr.dataformatsample[1:], array3d=dr.
#       aggregatedrate.data[idx], timeslot=time,
#       savefilename="Dust_transport_rate{}-{}.png".format(*time),
#        scale=np.arange(-100,110,10) ** 3 * 0.00000005)
#     em.densitymap_finalise("Dust_transport_rate{}-{}.png".format(*time))
#example usage with a single call:
#>>> for idx,time in enumerate(dr.timeslots):
#...   em.densitymap(savefilename="Test{}_{}.png".format(*time), formatsample=dr.dataformatsample[1:], array3d=dr.aggregatedrate.data[idx],timeslot=time,scale=np.arange(-100,110,10) ** 3 * 0.00000005, name=dr.aggregatedrate.name)

class Plotter():
    def __init__(self, processeddata):
        self.parseddata = processeddata
        #print dr.aggregatedrate[:,range(*parslice[:2,1]+(0,1))][:,:,range(*parslice[2:,1]+(0,1))]

    def get_scalefactors(self, sourcedata):
        print sourcedata
        globalmax, globalmin = np.amax(np.array([dataset.data for dataset in sourcedata])), np.amin(np.array([dataset.data for dataset in sourcedata]))
        scalefactors = []
        for dataset in sourcedata:
            localmax = np.amax(dataset.data)
            if localmax < globalmax / 2.0:
                scalefactors.append(globalmax / localmax)
            else:
                scalefactors.append(1)
        return scalefactors

    def plotlatitude(self, datatype, lat, lon0=None,lon1=None, aggregate=True, secondstohours = False, title="", scale=False, plotgeo=False, ylabel=None, timeslot=None, scale_to_global_max=True, interactive=False, forcenolabel=False):
        """Uses the class's DataReader instance to plot values along
        a (segment of a) given latitude. Default behavior is to plot
        aggregate or average values for a given point in time along
        the entire length of the segment. With plotgeo=True, it instead
        plots time-aggregated totals/averages for a given lontitude along
        the parallel.
        Parameters:
        datatype -- iterable of strings referring to the TypedData instances
                    of self.parseddata
        lat, lon0, lon1 -- the parallel to be sampled, and start end entpoints
              if lon0 and lon1 are None, the entire range of the parallel
              as far as present in the data will be sampled
        aggregate -- boolean whether to multiply
        secondstohours -- boolean whether to present an hourly rate rather than
              per second.
        scale -- boolean, allows to determine a scale factor when multiple
              data types are presented in the same graph
        plotgeo -- if True, x-axis is lontitudes rather than time, allows to
                aggregate over time for a single location.
        timeslot -- allows to plot only a single point in time
        scale_to_global_max -- for use with the timeslot option, when looping
                over timeslots, allows to enforce a uniform scale in multiple
                images (for creating animations...)
        
        Example uses:
        p.plotlatitude(["aggregateddust"], 48, 6,16,aggregate=False) # dust concentrations
                # 48N, 6 to 16E, over the entire teporal range
                
        p.plotlatitude(["aggregatedrate"], 38, secondstohours=True,aggregate=True,plotgeo=True)
               # dust transport rates across the 38th parallel, summed over time and plotted by
               # longtitude
        p.plotlatitude(["aggregatedrate"], 38, 8,28, secondstohours=True,aggregate=True)
                # hourly dust transport rates over timeacross 38th parallel, 8-28 deg East, aggregated
                # over the entire segment.
        

        """
        dr = self.parseddata
        sourcedata = [eval("dr."+ dataset) for dataset in datatype]
        
        if scale:
            scalefactors = self.get_scalefactors(sourcedata)
        else:
            scalefactors = [1 for entry in sourcedata]
        parslice = dr.get_x_y(lat,lat, lon0, lon1).astype("int")
        lon0, lon1 = parslice[2:,0]
        #check whether all data plotted have the same units. if yes,
        # mark unit on y-axis
        if len(set([dataset.unit for dataset in sourcedata])) == 1:
            unit = dataset.unit
            if secondstohours and "s" in unit:
                unit = unit.replace("s", "h")
            plt.ylabel(unit)
            individuallabels = False
        else:
            individuallabels = True
        
        # determine by how much the data has to be multiplied due to
        # converion to hours, aggregation, etc.
        scalefactor = 1.0
        if aggregate:
            if plotgeo == True:
                if timeslot==None:
                    scalefactor *= (len(dr.timeslots)-1) * 3600 * 12
                else: print "Aggregating in geo mode when only one timeslot is selected is undefined and ignored!"
            else:
                scalefactor *= parlength(lat,lon1-lon0)
        if secondstohours:
                scalefactor *= 3600
                
        for (idx,dataset) in enumerate(sourcedata):
            unit = dataset.unit
            # only create a label when different data are plotted and/or have to be scaled
            scalenotif = int(scale == True and scalefactors[idx] != 1.0) * (", scaled * %.1f" % scalefactors[idx])
            labelstring = ((bool(individuallabels) and len(sourcedata) > 1) * string.join([dataset.name,  dataset.unit], "") + scalenotif) * (not forcenolabel)
            
            unit = dataset.unit
            if plotgeo == True:
                
                if timeslot != None:
                        preselected = dataset.data[timeslot:timeslot+1,:,:]
                else: preselected = dataset.data
                datatoplot = np.average(
                        preselected[:,np.arange(*parslice[:2,1]),np.arange(*parslice[2:,1])],
                        0)
                
            else:
                datatoplot = np.average(
                        dataset.data[:,np.arange(*parslice[:2,1]),np.arange(*parslice[2:,1])],1)
            if secondstohours and "s" in unit:
                unit = unit.replace("s","h")
            if scale:
                local_scalefactor = scalefactor * scalefactors[idx]
            else:
                local_scalefactor = scalefactor
            datatoplot *= local_scalefactor
            
            #determine whether we're using time or lontitude as x-axis
            if plotgeo == True:
                x_axis = np.arange(*parslice[2:,1]) * 0.5 + dr.maplimits[2]
            else:
                x_axis = np.array(dr.timeslots)[:,0]+(np.array(dr.timeslots)[:,1]/24.)
            #print x_axis.shape
            #return 0
            #print datatoplot.shape
            plt.plot(
                    x_axis,
                    datatoplot,
                    label=labelstring
                )

        plt.legend()
        #check for explicit ylabel
        if ylabel:
                plt.ylabel(ylabel)
        #otherwise generate automatic ylabel if all data has the same unit:
        elif individuallabels == False:
            plt.ylabel(unit)
        if plotgeo:
            plt.xlabel("Longtitude")
        else:
            plt.xlabel("Day")
        if scale_to_global_max:
                plt.ylim(*np.array(scalefactor) * (min([np.amin(dataset.data) for dataset in sourcedata]),max([np.amax(dataset.data) for dataset in sourcedata])))
        if plotgeo and timeslot:
            title = title+" {}N 2018-04-{}, {}:00".format(lat, *dr.timeslots[timeslot])
        elif plotgeo:
                title = title+" {}N 2018-04-{}-{}".format(lat, *dr.timeslots[(0,-1),0])
        else:
            title = title+" {}N, {}-{}, 2018-04-{}-{}".format(lat, lon0, lon1, *dr.timeslots[(0,-1),0])
        plt.title(title)
        plt.savefig(title.replace(" ", "_").replace(",",".").replace(":",".")+".png")
        if interactive:
                plt.show()
        plt.close()
        
    


