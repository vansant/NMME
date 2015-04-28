from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import datetime as dt

def index_from_numpy_array(array, value):
    """ Returns the index of the closest value from from NumPy Array"""
    return (np.abs(array-value)).argmin()

def find_start_date_from_days_since(days_since, start_year, start_month, start_day):
    """ Returns the start date from number of days since a start year, month, day"""
    days_since = timedelta(days=days_since)
    start_date = dt.date(start_year, start_month, start_day)
    return start_date + days_since

def get_dates_since_start_date(start_date, length_of_time):
    """ Gets all dates from a start date to an end date"""
    #print start_date
    dates_list = []
    for i in range(length_of_time):
        day_since_start_day = timedelta(days=i)
        dates_list.append(start_date + day_since_start_day)
    return dates_list
    

def get_netcdf_metadata(day, lat, lon, positive_east_longitude, variable, request_dates, start_year, start_month, start_day, time_metric,time_units, data_path):
    pathname = data_path
    filehandle=Dataset(pathname,'r',format="NETCDF4")


    #print filehandle.variables
    return [filehandle.variables[variable].long_name, filehandle.variables[variable].units]


    
def get_netcdf_data(day, lat, lon, positive_east_longitude, variable, request_dates, start_year, start_month, start_day, time_metric,time_units, data_path):

    print "Processing NetCDF"
    # Path to OpenDap NetCDF 
    #pathname = 'http://thredds.northwestknowledge.net:8080/thredds/dodsC/macav2livneh_huss_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_daily_aggregated.nc'
    #pathname =  'http://inside-dev1.nkn.uidaho.edu:8080/thredds/dodsC/agg_macav2metdata_huss_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_daily.nc' 
    #'http://www.reacchpna.org/reacchspace/obj1/netcdf/MACAV1/agg_macav2metdata_tasmax_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_daily.nc'
    # File handles
    pathname = data_path
    filehandle=Dataset(pathname,'r',format="NETCDF4")


    #print filehandle.variables
    #print filehandle.variables[variable].long_name

    lathandle=filehandle.variables['lat']
    lonhandle=filehandle.variables['lon']
    timehandle=filehandle.variables['time']
    datahandle=filehandle.variables[variable]

    #print filehandle.variables

    # #### Need a function here
    # #### The order of variable dimensions are not consistent so time, lat, lon could
    # #### be lon, time, lat
    # ####  

    time_num=len(timehandle)
    timeindex=range(day-1,time_num)  #python starts arrays at 0
    time=timehandle[timeindex]
    lat_array = lathandle[:]
    lon_array = lonhandle[:]
    time_array = timehandle[:]

    
    # Return only the dates for the dataset
    if request_dates == "True":
        print "request dates true"
        # Get the start date in days since another date
        start_date = find_start_date_from_days_since(days_since=int(timehandle[0]), start_year=start_year, start_month=start_month, start_day=start_day)

        # Get a List of dates from the start date
        date_list = get_dates_since_start_date(start_date, len(time_array))
        # Convert datetime.date(1950, 1, 1) to 1950-01-01
        date_list = [date.isoformat() for date in date_list]

        return date_list

       #print dates
    # Lons from 0-360 converted to -180 to 180
    if positive_east_longitude == "True":
        lon_array = [x - 360 for x in lon_array[:]] 

    # Get the NetCDF indices for lat/lon
    closestLat = index_from_numpy_array (np.array(lat_array), lat)
    closestLon = index_from_numpy_array (np.array(lon_array), lon)

    # The data
    data = datahandle[timeindex, closestLat, closestLon]

    return data