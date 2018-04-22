from ecmwfapi import ECMWFDataServer

import sys

if __name__ == '__main__':
    try:
        dates = eval(sys.argv[1])
        hours = eval(sys.argv[2])
        hours = [str(hour).rjust(2,"0") for hour in hours]
    except:
        dates = range(11,18)
        hours = ["00", "12"]
        

dates = ["2018-04-" + str(i) for i in dates]
print dates
server = ECMWFDataServer()
for date in dates:
    for hour in ("{}:00:00".format(hour) for hour in hours):
        server.retrieve({
            "class": "ti",
            "dataset": "tigge",
            "date": date,
            "area": "70/-15/30/50",
            "grid": "0.5/0.5",
            "expver": "prod",
            "levelist": "50/200/250/300/500/700/850/925/1000",
            "levtype": "pl",
            "origin": "cwao",
            "param": "130/132/156",
            "step": "0",
            "time": hour,
            "type": "cf",  
            "target": "./temp_v_gh{}-{}.grib".format(date, hour),
        })
        server.retrieve({
            "class": "mc",
            "dataset": "cams_nrealtime",
            "date": date,
            "expver": "0001",
            "levelist": "50/200/250/300/500/700/850/925/1000",
            "levtype": "pl",
            "param": "4.210/5.210/6.210",
            "step": "0",
            "stream": "oper",
            "time": hour,
            "type": "an",
            "area": "70/-15/30/50",
            "grid": "0.5/0.5",
            "target": "./dust_concentrations{}-{}.grib".format(date, hour),
        })