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

def get_netcdf_metadata(day, lat, lon, positive_east_longitude, variable, request_dates, start_year, start_month, start_day, time_metric,time_units, data_path):
    pathname = data_path
    filehandle=Dataset(pathname,'r',format="NETCDF4")

    #print filehandle.variables
    return [filehandle.variables[variable].long_name, filehandle.variables[variable].units]
 
def get_netcdf_data(day, lat, lon, positive_east_longitude, variable, request_dates, start_year, start_month, start_day, time_metric,time_units, data_path, request_lat_lon):

    # File handles
    pathname = data_path
    filehandle=Dataset(pathname,'r',format="NETCDF4")

    try:
        lathandle = filehandle.variables['lat']
    except:
        lathandle = filehandle.variables['Latitude']

    try:
        lonhandle=filehandle.variables['lon']
    except:
        lonhandle=filehandle.variables['Longitude']
    
    try:
        timehandle=filehandle.variables['time']
    except:
        timehandle=filehandle.variables['Time']

    datahandle=filehandle.variables[variable]
    #print datahandle.dimensions


    time_num=len(timehandle)
    
    timeindex=range(day-1,time_num)  #python starts arrays at 0
    time=timehandle[timeindex]
    #print time
    lat_array = lathandle[:]
    lon_array = lonhandle[:]
    time_array = timehandle[:]

    #print lon_array

    # Return only the dates for the dataset
    if request_dates == "True":

        #print "Trying to request dates"

        # Get the start date in days since another date
        start_date = find_start_date_from_days_since(days_since=int(timehandle[0]), start_year=start_year, start_month=start_month, start_day=start_day)

        # Get a List of dates from the start date
        date_list = []
        for time in time_array:
            t = find_start_date_from_days_since(int(time), 1900, 1, 1)
            date_list.append(t)

        # Convert datetime.date(1950, 1, 1) to 1950-01-01
        date_list = [date.isoformat() for date in date_list]

        return date_list

    # Lons from 0-360 converted to -180 to 180
    if positive_east_longitude == "True":
        lon_array = [x - 360 for x in lon_array[:]] 

    # Get the NetCDF indices for lat/lon
    closestLat = index_from_numpy_array (np.array(lat_array), lat)
    closestLon = index_from_numpy_array (np.array(lon_array), lon)

    if request_lat_lon == "True":
        return [lat_array[closestLat], lon_array[closestLon]]

    # Dimensions
    variable_dimensions = datahandle.dimensions

    # Dictionary to map dimension with index value
    variable_index_dictionary = {}

    for var in variable_dimensions:
        if var == "time" or var == "Time":
            variable_index_dictionary[var] = timeindex
        if var == "lat" or var == "Latitude":
            variable_index_dictionary[var] = closestLat
        if var == "lon" or var == "Longitude":
            variable_index_dictionary[var] = closestLon

    # Dictionary to map the order of the dimensions
    variable_dimensions_dictionary = {}
    variable_dimensions_dictionary[0] = datahandle.dimensions[0]
    variable_dimensions_dictionary[1] = datahandle.dimensions[1]
    variable_dimensions_dictionary[2] = datahandle.dimensions[2]

    data = datahandle[variable_index_dictionary[variable_dimensions_dictionary[0]], variable_index_dictionary[variable_dimensions_dictionary[1]], variable_index_dictionary[variable_dimensions_dictionary[2]]]
    return data

