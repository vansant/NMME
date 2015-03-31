from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt

def Index(array, userInput):
        '''Function to find the index value of an array value closest to user input value '''     

        # Convert array to list and find the value with the smallest difference between the array and user input.
        userInput = float(userInput)
        newList =  [abs(userInput - i) for i in array]
        originalList = [i for i in array]
        newList.sort()
        smallestDifference = newList[0]
   
        # Return to index of the closest value to the original
        index = userInput + smallestDifference
        if index in originalList:
            pass
        else:
            index = userInput - smallestDifference
        closestIndex = originalList.index(index)
        return closestIndex


def get_data(day, lat, lon, positive_east_longitude, variable):

    
    # Path to OpenDap NetCDF 
    pathname = 'http://thredds.northwestknowledge.net:8080/thredds/dodsC/macav2livneh_huss_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_daily_aggregated.nc'
    
    # File handles
    filehandle=Dataset(pathname,'r',format="NETCDF4")
    lathandle=filehandle.variables['lat']
    lonhandle=filehandle.variables['lon']
    timehandle=filehandle.variables['time']
    datahandle=filehandle.variables[variable]
   

    time_num=len(timehandle)
    timeindex=range(day-1,time_num,365)  #python starts arrays at 0
    time=timehandle[timeindex]
    lat_array = lathandle[:]
    lon_array = lonhandle[:]

    if positive_east_longitude:
        lon_array = [x - 365 for x in lon_array[:]] # lons from 0-360 convert to -180 to 180

    # The index closest to the lat/lon values
    closestLat = Index(lat_array, lat)
    closestLon = Index(lon_array, lon)

    # The data
    data = datahandle[timeindex, closestLat, closestLon]

    return data