#from django.db import models

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import datetime as dt
from dateutil import rrule, relativedelta


def find_start_date_from_days_since(days_since, start_year, start_month, start_day):
    """ Returns the start date from number of days since a start year, month, day"""
    days_since = timedelta(days=days_since)
    start_date = dt.date(start_year, start_month, start_day)
    return start_date + days_since

def get_streamflow_data(outlet, variable, product, year_start, year_end,scenario,model,request_dates,netcdf_time_index):

    if model=='CCSM4':
        runname='r6i1p1'
    else:
        runname='r1i1p1'
    #get data path
    if scenario =='historicalstream':
        pathname ='http://thredds.northwestknowledge.net:8080/thredds/dodsC/NWCSC_INTEGRATED_SCENARIOS_ALL_HYDROLOGY_VIC2/vic_RoutedRunoff_livneh-CANv1.1-USv1.0_None_historical_1950_2005_WUSA_daily.nc'
        start_date=''
        end_date=''
    elif scenario=='historical':
        pathname='http://thredds.northwestknowledge.net:8080/thredds/dodsC/NWCSC_INTEGRATED_SCENARIOS_ALL_HYDROLOGY_VIC2/vic_RoutedRunoff_'+model+'_'+runname+'_historical_1950_2005_WUSA_daily.nc'   
        start_date=''
        end_date=''
    elif scenario =='rcp45':
        pathname ='http://thredds.northwestknowledge.net:8080/thredds/dodsC/NWCSC_INTEGRATED_SCENARIOS_ALL_HYDROLOGY_VIC2/vic_RoutedRunoff_'+model+'_'+runname+'_rcp45_2006_2099_WUSA_daily.nc'
        start_date = str(year_start)+"-01-01"
        end_date=str(year_end)+"-12-31"
    elif scenario =='rcp85':
        pathname ='http://thredds.northwestknowledge.net:8080/thredds/dodsC/NWCSC_INTEGRATED_SCENARIOS_ALL_HYDROLOGY_VIC2/vic_RoutedRunoff_'+model+'_'+runname+'_rcp85_2006_2099_WUSA_daily.nc'
        start_date = str(year_start)+"-01-01"
        end_date=str(year_end)+"-12-31"

    # File handles
    filehandle=Dataset(pathname,'r',format="NETCDF4")
    #print filehandle.variables
    if request_dates=='False':
        outlethandle=filehandle.variables['outlet_name']
        datahandle=filehandle.variables[variable]
        outlet_array = outlethandle[:]
        outlet_newarray={}
        for i in range(len(outlet_array)):
            outlet_newarray[i]=''.join(outlet_array[i]).strip()
            
	outlet_array=outlet_newarray.values()
        outlet_index = outlet_array.index(outlet)
    timehandle=filehandle.variables['Time']
    time_num=len(timehandle)
   
    timeindex=range(time_num)  #python starts arrays at 0
    time=timehandle[timeindex]
    time_array = timehandle[:]

    # Return only the dates for the dataset
    if request_dates == "True":
        # Get the start date in days since another date
        #start_date = find_start_date_from_days_since(days_since=int(timehandle[0]), start_year=start_year, start_month=start_month, start_day=start_day)

        # Get a List of dates from the start date
        date_list = []
        for time in time_array:
            t = find_start_date_from_days_since(int(time), 1950, 1, 1)
            date_list.append(t)

        # Convert datetime.date(1950, 1, 1) to 1950-01-01
        date_list = [date.isoformat() for date in date_list]

        #print "trying to do this"
        if start_date == '' or end_date == '':
            #start_time_index = ''
            #end_time_index = ''
            return date_list[:], ['','']
        else:
            try:
                start_time_index = date_list.index(start_date)
            except:
                return ["error", "start_date not in dataset"], ['','']
            try:
                end_time_index = date_list.index(end_date)
            except:
                return ["error", "end_date not in dataset"], ['','']

            #print type(start_time_index)
            # return the filtered times as well as the index for start_date and end_date
            return date_list[start_time_index: end_time_index], [start_time_index, end_time_index]

    else: 
        start_date_index=netcdf_time_index[0]
        end_date_index=netcdf_time_index[1]
        if start_date_index == '' or end_date_index == '':
            data = datahandle[:][outlet_index]
	else:
            data = datahandle[start_time_index:end_time_index][outlet_index]

