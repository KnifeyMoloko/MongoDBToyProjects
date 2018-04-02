

# OECD Household database request

# imports
import requests
import datetime
import os
import json

# requests
"""
# request in the SDMX-JASON format for Poland and Portugal and OECF with full
# data fields
r = requests.get("http://stats.oecd.org/SDMX-JSON/data/HH_DASH/POL+PRT+OECD.RGDP_INDEX+RGDP+RHHGDI_INDEX+RHHGDI+HHNT+HHSAV+HHFC_INDEX+HHFINCON+COCONF+ENDT+SBF90GDI+UNEMPRATE+LAB_UR6.Q/all?startTime=2007-Q1&endTime=2017-Q3&dimensionAtObservation=allDimensions").json()
"""

# same as above but in a time series format, output is JSON
r = requests.get("http://stats.oecd.org/SDMX-JSON/data/HH_DASH/POL.+UNEMPRATE.Q/all?startTime=2007-Q1&endTime=2017-Q3").json()

# get time at runtime (or about that time), format for file manipulations
time_at_creation = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def database_dump():
    # create path filename and dump the requested data to file
    filename = "OECD_Household_Database_" + time_at_creation + ".txt"
    path = os.path.join(os.path.curdir, "Mongo/Outputs/", filename)
    with open(path, mode="w") as outfile:
        json.dump(r, outfile)


# check for existing Outputs dir, if not found, create one and than dump data
if os.path.isdir(os.path.join(os.path.curdir, "Mongo/Outputs/")):
    database_dump()
else:
    os.mkdir(os.path.join(os.path.curdir, "Mongo/Outputs"))
    database_dump()
