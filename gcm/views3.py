from multiprocessing import Pool
import numpy as np
from django.http import HttpResponse
from netCDF4 import Dataset
from models import  spatial_subset, index_from_numpy_array
import json
import os

#from NMME.local_settings import scatterplot_summary_path

scatterplot_summary_path = "/Users/vansant/Projects/NMME/datasets/summarylayers"

product = "macav2metdata"
variable_list = ['pr']#, 'tasmin', 'pet', 'rhsmin', 'rsds', 'rhsmax', 'tasmax', 'was']
month_ranges = ['ANN', 'DJF', 'MAM', 'JJA', 'SON']
year_ranges = ['20102039', '20702099', '19712000', '20402069']
scenarios = ['rcp45', 'historical', 'rcp85']
models = ['BNU-ESM', 'bcc-csm1-1', 'CSIRO-Mk3-6-0', 'HadGEM2-CC365', 'MIROC5', 'inmcm4', 'GFDL-ESM2M', 'CanESM2', 'IPSL-CM5A-MR', 'CNRM-CM5', 'MIROC-ESM-CHEM', 'CCSM4', 'MRI-CGCM3', 'HadGEM2-ES365', '20CMIP5ModelMean', 'IPSL-CM5B-LR', 'NorESM1-M', 'GFDL-ESM2G', 'bcc-csm1-1-m', 'IPSL-CM5A-LR', 'MIROC-ESM']

def get_scatterplot_data(request):
    sw_lat = 45
    sw_lon = -116
    ne_lon = -115
    ne_lat = 46
    month_range = "DJF"
    variable = "pr"
    year_range  = '20102039'
    scenario = 'rcp45'
    positive_east_longitude = "False"

    # Set pool of workers
    p = Pool(20) 

    # Each set of parameters is for one URL call
    function_parameters = []

    # List for all returned netcdf data
    netcdf_data_list = []

    #model_name = "20CMIP5ModelMean"

    variable_dictionary = {'huss':'specific_humidity', 'pr':'precipitation', 'tasmax':'air_temperature', 'rsds':'surface_downwelling_shortwave_flux_in_air', 'tasmin':'air_temperature', 'was':'wind_speed', 'SWE-monday1':'SWE','Evaporation-monsum':'Evaporation','TotalSoilMoist-monmean':'TotalSoilMoisture', 'C_ECOSYS':'C_ECOSYS',  'PART_BURN':'PART_BURN'}
    variable_transform = variable_dictionary[variable]
    print variable_transform

    for model_name in models:

        file_name = 'macav2metdata_%s_%s_%s_%s_%s.nc' % (variable, month_range, year_range, scenario, model_name)
        data_path = os.path.join(scatterplot_summary_path, file_name)
        #print model
        function_parameters.append((sw_lat, sw_lon, ne_lon, ne_lat, month_range, variable_transform, data_path, model_name, positive_east_longitude))

    # # Map to pool - this gets netcdf data into a workable list
    netcdf_data_list.append (p.map(allow_mulitple_parameters, function_parameters))

    # Close subprocess workers (open files)
    p.terminate()
    p.join()

    #results = process_data(sw_lat, sw_lon, ne_lon, ne_lat, month_range, variable, data_path, model_name)
    #print results
    #return HttpResponse(netcdf_data_list)

    #Dictionary of JSON rows
    JSON_dictionary = {}

    # Loop through each column and set the colunm name for JSON and assign data
    #print len(netcdf_data_list[0])
    for i in range(len(netcdf_data_list[0])):
        #print netcdf_data_list[0][i][1], type(netcdf_data_list[0][i][1])
        JSON_dictionary[netcdf_data_list[0][i][0]] = float(netcdf_data_list[0][i][1])
    
    #print JSON_dictionary
    object_for_JSON = {"data":[JSON_dictionary,]}
    response = json.dumps(object_for_JSON)

    return HttpResponse(response, content_type="application/json")

def summary_layer_spatial_subset(data, method):
    """ Returns the spatial average or sum for a NetCDF subset region"""
    if method == "sum":
        return np.sum(data)
    elif method == "mean":
        return np.mean(data)

# Pack parameters
def allow_mulitple_parameters(args):
    return process_data(*args)

def process_data(sw_lat, sw_lon, ne_lon, ne_lat, month_range, variable, data_path, model_name, positive_east_longitude):

    # File handles
    pathname = data_path
    print pathname
    filehandle=Dataset(pathname,'r',format="NETCDF4")
    #print filehandle.variables
    try:
        lathandle = filehandle.variables['lat']
    except:
        lathandle = filehandle.variables['Latitude']
    try:
        lonhandle=filehandle.variables['lon']
    except:
        lonhandle=filehandle.variables['Longitude']


    datahandle=filehandle.variables[variable]
    #print datahandle.dimensions

    lat_array = lathandle[:]
    lon_array = lonhandle[:]
    #lat_array =  np.sort(lat_array)
    #print lon_array

    # Lons from 0-360 converted to -180 to 180
    if positive_east_longitude == "True":
        lon_array = [x - 360 for x in lon_array[:]] 

    # Bounding box indices
    sw_lat = index_from_numpy_array(np.array(lat_array), sw_lat)
    #print SWLat, lat_array[SWLat]

    sw_lon = index_from_numpy_array(np.array(lon_array), sw_lon)
    #print SWLong, lon_array[SWLong]

    ne_lat = index_from_numpy_array(np.array(lat_array), ne_lat)
    #print NELat, lat_array[NELat]

    ne_lon = index_from_numpy_array(np.array(lon_array), ne_lon)
    #print NELong, lon_array[NELong]

    # Lats are in reverse sorted order with these datasets
    closestLat = slice(ne_lat, sw_lat)
    closestLon = slice(sw_lon, ne_lon)

    #print closestLon, closestLat
    data = datahandle[closestLat, closestLon]

    # Average or sum over spatial subset region
    data_spatial_analysis = summary_layer_spatial_subset(data, method="mean")
    return [model_name, data_spatial_analysis]


# sw_lat = 45
# sw_lon = -116
# ne_lon = -115
# ne_lat = 46
# month_range = "ANN"
# variable = "pr"
# year_range  = '20102039'
# scenario = 'rcp45'
# model_name = "20CMIP5ModelMean"

# file_name = 'macav2metdata_%s_%s_%s_%s_%s.nc' % (variable, month_range, year_range, scenario, model_name)
# data_path = os.path.join(scatterplot_summary_path, file_name)

# variable_dictionary = {'huss':'specific_humidity', 'pr':'precipitation', 'tasmax':'air_temperature', 'rsds':'surface_downwelling_shortwave_flux_in_air', 'tasmin':'air_temperature', 'was':'wind_speed', 'SWE-monday1':'SWE','Evaporation-monsum':'Evaporation','TotalSoilMoist-monmean':'TotalSoilMoisture', 'C_ECOSYS':'C_ECOSYS',  'PART_BURN':'PART_BURN'}
# variable = variable_dictionary[variable]

# results = process_data(sw_lat, sw_lon, ne_lon, ne_lat, month_range, variable, data_path, model_name)
# print results