from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt

def index_from_numpy_array(array, value):
    """ Returns the index of the closest value from from NumPy Array"""
    return (np.abs(array-value)).argmin()


def get_netcdf_data(day, lat, lon, positive_east_longitude, variable):

    # Path to OpenDap NetCDF 
    #pathname = 'http://thredds.northwestknowledge.net:8080/thredds/dodsC/macav2livneh_huss_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_daily_aggregated.nc'
    pathname =  'http://inside-dev1.nkn.uidaho.edu:8080/thredds/dodsC/agg_macav2metdata_huss_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_daily.nc' 
    # File handles
    filehandle=Dataset(pathname,'r',format="NETCDF4")

    lathandle=filehandle.variables['lat']
    lonhandle=filehandle.variables['lon']
    timehandle=filehandle.variables['time']
    datahandle=filehandle.variables[variable]

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
    print time_num

    # Lons from 0-360 converted to -180 to 180
    if positive_east_longitude == "True":
        lon_array = [x - 360 for x in lon_array[:]] 

    # Get the NetCDF indices for lat/lon
    closestLat = index_from_numpy_array (np.array(lat_array), lat)
    closestLon = index_from_numpy_array (np.array(lon_array), lon)

    # The data
    data = datahandle[timeindex, closestLat, closestLon]

    return data