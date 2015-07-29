from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import datetime as dt
from dateutil import rrule, relativedelta


def filter_dates(start_date, end_date, time_duration):
    """ Returns a list of dates between two time periods
    start_date:
        The begining date as a string
        ex. 2014-06-21
    end_date:
        The ending date as a string
        ex. 2014-07-07
    time_duration:
        Duration of dates in days or months
    """
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")

    if time_duration == "days":
        #date_range = [start_date + dt.timedelta(days=x) for x in range(0, (end_date-start_date).days + 1)]
        date_range = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date))

    if time_duration == "months":
        date_range = list(rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date))

    # List containing all dates
    return date_range
    #for date in date_range:
    #    print date.strftime("%Y-%m-%d")

def index_from_list(array, value):
    """ Returns the index of a value from a list"""
    return array.index(value)

def index_from_numpy_array(array, value):
    """ Returns the index of the closest value from from NumPy Array"""
    return (np.abs(array-value)).argmin()

def find_start_date_from_days_since(days_since, start_year, start_month, start_day):
    """ Returns the start date from number of days since a start year, month, day"""
    days_since = timedelta(days=days_since)
    start_date = dt.date(start_year, start_month, start_day)
    return start_date + days_since

def get_netcdf_metadata(lat, lon, positive_east_longitude, variable, request_dates, start_year, start_month, start_day, time_metric,time_units, data_path):
    pathname = data_path
    filehandle=Dataset(pathname,'r',format="NETCDF4")

    #print filehandle.variables
    return [filehandle.variables[variable].long_name, filehandle.variables[variable].units]
 
def get_netcdf_data(lat, lon, positive_east_longitude, variable, request_dates, start_year, start_month, start_day, time_metric,time_units, data_path, request_lat_lon, start_date, end_date, start_date_index, end_date_index):

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
    
    timeindex=range(time_num)  #python starts arrays at 0
    time=timehandle[timeindex]
    #print time
    lat_array = lathandle[:]
    lon_array = lonhandle[:]
    time_array = timehandle[:]

    #print lon_array

    #



    # Return only the dates for the dataset
    if request_dates == "True":

        #print "Trying to request dates"

        # Get the start date in days since another date
        #start_date = find_start_date_from_days_since(days_since=int(timehandle[0]), start_year=start_year, start_month=start_month, start_day=start_day)

        # Get a List of dates from the start date
        date_list = []
        for time in time_array:
            t = find_start_date_from_days_since(int(time), 1900, 1, 1)
            date_list.append(t)

        # Convert datetime.date(1950, 1, 1) to 1950-01-01
        date_list = [date.isoformat() for date in date_list]

        #print "trying to do this"
        if start_day == '' or end_date == '':
            start_time_index = ''
            end_time_index = ''
            return date_list[:], [start_time_index, end_time_index]
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

    #print timeindex
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
    if start_date_index == '' or end_date_index == '':
        print "return all data"
        return data[:]
    else:
        return data[start_date_index:end_date_index]

