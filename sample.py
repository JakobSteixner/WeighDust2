#/usr/bin/python

from DataReader import *
from plottingtools import *

import subprocess
# a rough and dirty check whether the raw data files are available,
# call the request script otherwise
dustfiles = subprocess.check_output(("ls dust_concentrations2018-04-1*grib"), shell=True).split()
tempfiles = subprocess.check_output(("ls temp_v_gh2018-04-1*grib"), shell=True).split()
if len(dustfiles) < 4 or len(tempfiles) < 4:
    subprocess.call(("python", "request.py"))

# instantiate a data reader object to read in and preprocess
# files for date range April 11-17, at 00:00 and 12:00 hours
dr = DataReader((range(11,18), (0,12)))

#instantiate a Euromap instance
em = Euromap()

# create a series of maps showing the dust transport rate
# along north-south axis
for idx,time in enumerate(dr.timeslots):
    em.densitymap(savefilename="North_South_Dust_Transport_{}_{}.png".format(*time),
                  formatsample=dr.dataformatsample[1:],
                  title = "North-South Dust Transport, 2018-04{}, {}:00".format(*time),
                  array3d=dr.aggregatedrate.data[idx],
                  timeslot=time,
                  scale=np.arange(-100,110,10) ** 3 * 0.00000005,
                  name=dr.aggregatedrate.name)
try:
    # turn maps into animated gif (assumes ImageMagick is installed)
    subprocess.call(("convert -delay 150 -loop North_South_Dust_Transport*png North_South_Transport.gif"))
except:
    pass

# create a series of images with dust/m2

for idx,time in enumerate(dr.timeslots):
    em.densitymap(savefilename="Dust_Volume_{}_{}.png".format(*time),
                  formatsample=dr.dataformatsample[1:],
                  title = "Total Dust Volume, 2018-04{}, {}:00".format(*time),
                  array3d=dr.aggregateddust.data[idx],
                  timeslot=time,
		  countries=True,
                  scale="posonly", # string identifier of a predefined scale that seemed to work well
                  name=dr.aggregateddust.name)

# plot the volume of dust crossing the 38th parallel in the central and eastern Mediterranean
p = Plotter(dr)
p.plotlatitude(["aggregatedrate", "grosstransport"], 38.0, 8., 28., title="Gross_Net_dust_transports_2018_05_{}-{}.png".format(*dr.timeslots[0,(0,-1)]))

