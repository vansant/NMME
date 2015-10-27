from netCDF4 import Dataset
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
from dateutil import rrule 
import pandas as pd

from NMME.local_settings import streamflow_path

def find_start_date_from_days_since(days_since, start_year, start_month, start_day):
    """ Returns the start date from number of days since a start year, month, day"""
    days_since = timedelta(days=days_since)
    start_date = dt.date(start_year, start_month, start_day)
    return start_date + days_since

def get_streamflow_data(outlet, variable, product, scenario, model, start_date, end_date):
    """ Returns monthly averaged streamflow data"""

    # Only one model uses a different run
    if model == 'CCSM4':
        runname = 'r6i1p1'
    else:
        runname = 'r1i1p1'
        
    # Get data path
    if scenario == 'historicalstream':
        pathname = streamflow_path + 'livneh-CANv1.1-USv1.0_None_historical_1950_2005_WUSA_daily.nc'
    elif scenario == 'historical':
        pathname = streamflow_path+model+'_'+runname+'_historical_1950_2005_WUSA_daily.nc'   
    elif scenario == 'rcp45':
        pathname = streamflow_path+model+'_'+runname+'_rcp45_2006_2099_WUSA_daily.nc'
    elif scenario =='rcp85':
        pathname =streamflow_path+model+'_'+runname+'_rcp85_2006_2099_WUSA_daily.nc'

    #print pathname
    filehandle=Dataset(pathname,'r',format="NETCDF4")
    #print filehandle.variables

    try:
        outlethandle = filehandle.variables['outlet_name']
    except:
        pass
        #print "there is no outlets variable"
    try:
        timehandle=filehandle.variables['time']
    except:
        try:
            timehandle=filehandle.variables['Time']
        except:
            timehandle=filehandle.variables['day']

    datahandle = filehandle.variables[variable]
    time_num = len(timehandle)
    timeindex = range(time_num)  
    time = timehandle[timeindex]
    outlet_array = outlethandle[:]
    time_array = timehandle[:]

    # Get a List of dates from the start date
    date_list = []
    for time in time_array:
        t = find_start_date_from_days_since(int(time), 1950, 1, 1)
        date_list.append(t)

    # Convert datetime.date(1950, 1, 1) to 1950-01-01
    date_list = [date.isoformat() for date in date_list]
    #print date_list

    # Outlet dictionary for index lookup
    outlet_dictionary = {}
    for i in range(len(outlet_array)):
        outlet_name = ""
        outlet_data = outlet_array[i]
        for name in outlet_data:
            outlet_name += name
        outlet_dictionary[outlet_name] = i
        i+=1
    #print outlet_dictionary

    closestOutlet = outlet_dictionary[outlet]
    #print closestOutlet
    timeindex = slice(0, len(time_array))

    if start_date and end_date:
        #print start_date, end_date
        timeindex = slice(date_list.index(start_date), date_list.index(end_date))
        date_list =  date_list[timeindex]
        #print date_list
    data = datahandle[timeindex,closestOutlet]
    #print data

    # Convert list of dates to pandas date_range 
    pandas_date_range = pd.DatetimeIndex(date_list)

    # Create pangdas time series 
    time_series = pd.Series(data, index=pandas_date_range)
    time_series_data = time_series.resample('M')
    #print time_series_data

    # Filter monthly data
    month = time_series_data.index.month
    jan_selector = (month == 1) 
    jan_data = time_series_data[jan_selector]
    
    feb_selector = (month == 2) 
    feb_data = time_series_data[feb_selector]

    mar_selector = (month == 3) 
    mar_data = time_series_data[mar_selector]

    apr_selector = (month == 4) 
    apr_data = time_series_data[apr_selector]

    may_selector = (month == 5) 
    may_data = time_series_data[may_selector]

    jun_selector = (month == 6) 
    jun_data = time_series_data[jun_selector]

    jul_selector = (month == 7) 
    jul_data = time_series_data[jul_selector]

    aug_selector = (month == 8) 
    aug_data = time_series_data[aug_selector]

    sep_selector = (month == 9) 
    sep_data = time_series_data[sep_selector]

    oct_selector = (month == 10) 
    oct_data = time_series_data[oct_selector]

    nov_selector = (month == 11) 
    nov_data = time_series_data[nov_selector]

    dec_selector = (month == 12) 
    dec_data = time_series_data[dec_selector]

    monthly_data = [jan_data, feb_data, mar_data, apr_data, may_data, jun_data, jul_data, aug_data, sep_data, oct_data, nov_data, dec_data]
    if scenario == 'historicalstream':
        monthly_calculation =  [np.mean(x) for x in monthly_data]
        return [monthly_calculation]
    else:
        monthly_min = [np.min(x) for x in monthly_data]
        monthly_max = [np.max(x) for x in monthly_data]
        return [monthly_min, monthly_max]
    