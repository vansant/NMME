from multiprocessing import Pool
import numpy as np
from django.http import HttpResponse
from netCDF4 import Dataset
from models import  get_date_no_leap_year, spatial_subset, custom_resampler, process_gcm_data, index_from_numpy_array
import json
import os

from NMME.local_settings import scatterplot_path


def build_netcdf_data_paths(product, variable, model, time_frame, daily_or_monthly):
    """ Builds list of data paths to netcdf files based on certain criteria"""

    # Only one model uses a different run
    if model == 'CCSM4':
        runname = 'r6i1p1'
    else:
        runname = 'r1i1p1'

    # path on disk
    directory_name = scatterplot_path
    directory_path = scatterplot_path + "%s/%s/" % (product, model)
    
    # Change into directory
    os.chdir(directory_path)

    data_path_strings = []
    #print variable
    # Get list of NetCDF Files
    for file_name in os.listdir("."):
        if file_name.endswith(".nc"):
            #print 'true'
            if file_name.split("_")[1] == variable:
                # Filter time frame
                if time_frame in file_name and daily_or_monthly in file_name:
                    data_path_strings.append(file_name)
                    #print file_name
                else:
                    pass
            else:
                pass
        else:
            pass
    #print data_path_strings
    return data_path_strings

def filter_netcdf_paths_by_date_range(start_date, end_date, netcdf_data_paths):
    """ Determine which NetCDF files will be needed from date range"""
    filtered_by_date = []

    for file_name in netcdf_data_paths:
        start_year =  file_name.split("_")[5]
        end_year = file_name.split("_")[6]

        file_year_range = range(int(start_year), int(end_year)+1)
        total_date_range = range(int(start_date[0:4]), int(end_date[0:4])+1)
        #print total_date_range, file_year_range

        for year in total_date_range:
            if year in file_year_range:
                filtered_by_date.append(file_name)

    # Return a sorted list of netcdf file names
    return sorted([x for x in set(filtered_by_date)])

def get_scatterplot_data(request):
    """ View that calculate the temporal average from a NETCDF4 file for a spatial region"""
    errors = []

    # start_month
    if 'start-month' in request.GET:
        try:
            start_month = int(request.GET['start-month'])-1
            if start_month < 0 or start_month > 11 :
                errors.append("start-month parameter needs to to be between 0-11. 0 is Jan where 1 is Dec")
        except:
            errors.append("start-month parameter needs to be a int")
    else:
        errors.append("You need to specify a start-month parameter")

    # end_month
    if 'end-month' in request.GET:
        try:
            end_month = int(request.GET['end-month'])-1
            if end_month < 0 or end_month > 11 :
                errors.append("end-month parameter needs to to be between 0-11. 0 is Jan where 1 is Dec")
        except:
            errors.append("end-month parameter needs to be a int")
    else:
        errors.append("You need to specify a end-month parameter")

    months = [0,1,2,3,4,5,6,7,8,9,10,11]

    if start_month >= end_month:
        month_list = months[start_month:]
        month_list = month_list+months[:end_month]
        #print month_list
    else:
        month_list = months[start_month:end_month]
        #print month_list

    # start_year
    if 'start-year' in request.GET:
        try:
            start_year = int(request.GET['start-year'])
            if start_year < 1950:
                errors.append("start-year parameter needs to to be at least 1950")
        except:
            errors.append("start-year parameter needs to be a int")
    else:
        errors.append("You need to specify a start-year parameter")

    # end_year
    if 'end-year' in request.GET:
        try:
            end_year = int(request.GET['end-year'])
            if end_year > 2099:
                errors.append("end-year parameter needs to to be at 2099 or less")
        except:
            errors.append("end-year parameter needs to be a int")
    else:
        errors.append("You need to specify a end-year parameter")

    if start_year == end_year:
        errors.append("start-year and end-year need to be different")

    if start_year >= end_year:
        errors.append("start-year should be less than end-year")

    # sw lat
    if 'sw-lat' in request.GET:
        try:
            sw_lat = float(request.GET['sw-lat'])
            if sw_lat < -90 or sw_lat > 90:
                errors.append("sw-lat parameter needs to within -90 to 90 range")
        except:
            errors.append("sw-lat parameter needs to be a float")
    else:
        errors.append("You need to specify a sw-lat parameter")

    # sw lon
    if 'sw-lon' in request.GET:
        try:
            sw_lon = float(request.GET['sw-lon'])
            if sw_lon < -180 or sw_lon > 180:
                errors.append("sw-lon parameter needs to within -180 to 180 range")
        except:
            errors.append("sw-lon parameter needs to be a float")
    else:
        errors.append("You need to specify a sw-lon parameter")


    # ne lat
    if 'ne-lat' in request.GET:
        try:
            ne_lat = float(request.GET['ne-lat'])
            if ne_lat < -90 or ne_lat > 90:
                errors.append("ne-lat parameter needs to within -90 to 90 range")
        except:
            errors.append("ne-lat parameter needs to be a float")
    else:
        errors.append("You need to specify a ne-lat parameter")

    # ne lon
    if 'ne-lon' in request.GET:
        try:
            ne_lon = float(request.GET['ne-lon'])
            if ne_lon < -180 or ne_lon > 180:
                errors.append("ne-lon parameter needs to within -180 to 180 range")
        except:
            errors.append("ne-lon parameter needs to be a float")
    else:
        errors.append("You need to specify a ne-lon parameter")

    # calculation
    if 'calculation' in request.GET:
        calculation = request.GET['calculation']
        if calculation == 'sum' or calculation == 'mean':
            pass
        else:
            errors.append("calculation parameter needs to sum or mean")
    else:
        errors.append("You need to specify a calculation parameter")

    # variable
    if 'variable' in request.GET:
        variable = request.GET['variable']
    else:
        errors.append("You need to specify a variable parameter")

    # product
    if 'product' in request.GET:
        product = request.GET['product']
    else:
        errors.append("You need to specify a product parameter")

    # sw lon
    if 'time-frame' in request.GET:
        try:
            time_frame = request.GET['time-frame']
            if time_frame == "historical" or time_frame == "rcp45" or time_frame == "rcp85":
                pass
            else:
                errors.append("time-frame parameter needs to be historical rcp45 or rcp85")
        except:
            errors.append("time-frame parameter needs to be historical rcp45 or rcp85")
    else:
        errors.append("You need to specify a time-frame parameter")

    # Return errors
    if errors:
        return HttpResponse(errors)

    # Set pool of workers
    p = Pool(20) 

    # Each set of parameters is for one URL call
    function_parameters = []

    # List for all returned netcdf data
    netcdf_data_list = []

    variable_dictionary = {'huss':'specific_humidity', 'pr':'precipitation', 'tasmax':'air_temperature', 'rsds':'surface_downwelling_shortwave_flux_in_air', 'tasmin':'air_temperature', 'was':'wind_speed', 'SWE-monday1':'SWE','Evaporation-monsum':'Evaporation','TotalSoilMoist-monmean':'TotalSoilMoisture', 'C_ECOSYS':'C_ECOSYS',  'PART_BURN':'PART_BURN'}
    variable_transform = variable_dictionary[variable]

    # for models in model_list
    model_name = 'CCSM4'

    netcdf_data_paths = build_netcdf_data_paths(product=product, variable=variable, model=model_name, time_frame=time_frame, daily_or_monthly="monthly")
    filtered_path_names = filter_netcdf_paths_by_date_range(start_date=str(start_year), end_date=str(end_year), netcdf_data_paths=netcdf_data_paths)

    # for each path_name
    # get get dates
    # get data
    # spatially average data
    # combine all months for each model



    # Process each model and get results
    processed_data_list = []
    for data_path in filtered_path_names:
        proccessed_data = process_data(sw_lat, sw_lon, ne_lon, ne_lat, month_list, start_year, end_year, end_month, start_month, variable_transform, data_path, calculation, model_name)
        processed_data_list.append(proccessed_data)
    
    #print processed_data_list 
    monthly_dates_and_data =  reduce(lambda x,y: x+y,processed_data_list)
    
    # Model and averaged data
    all_data = process_combined_years_and_data(monthly_dates_and_data=monthly_dates_and_data, month_list=month_list, calculation=calculation, start_year=start_year, end_year=end_year, start_month=month_list[0]+1, end_month=month_list[-1]+1, model_name=model_name)

    # Close subprocess workers (open files)
    p.terminate()
    p.join()

    #response = [model_results_list]

    return HttpResponse(all_data)

def process_data(sw_lat, sw_lon, ne_lon, ne_lat, month_list, start_year, end_year, end_month, start_month, variable, data_path, calculation, model_name):

    # File handles
    pathname = data_path
    #print data_path
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
    try:
        timehandle=filehandle.variables['time']
    except:
        try:
            timehandle=filehandle.variables['Time']
        except:
            timehandle=filehandle.variables['day']

    # NetCDF variable 
    datahandle=filehandle.variables[variable]
    time_num=len(timehandle)
    timeindex=range(time_num)  #python starts arrays at 0
    time=timehandle[timeindex]
    lat_array = lathandle[:]
    lon_array = lonhandle[:]

    positive_east_longitude = "True"

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


    closestLat = slice(sw_lat, ne_lat)
    closestLon = slice(sw_lon, ne_lon)

    # Which months to get data for
    #month_list = [11,0,1]

    def get_monthly_dates_and_data(month):
        """ Function that get dates and data for a single month from a NetCDF File"""
        # Month to get data for
        request_month = month
        #print request_month

        # Dimensions
        variable_dimensions = datahandle.dimensions

        # Dictionary to map dimension with index value
        variable_index_dictionary = {}

        # Slice out month data for all years
        timeindex = slice(request_month,len(timehandle),12)

        #print timeindex
        for var in variable_dimensions:
            if var == "time" or var == "Time" or var == "day":
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
        #print variable_dimensions_dictionary

        # Get the dates using calculation for now leap years
        dates = [get_date_no_leap_year(x) for x in timehandle[timeindex]]
        #print dates, len(dates)

        # Get the data
        data = datahandle[variable_index_dictionary[variable_dimensions_dictionary[0]], variable_index_dictionary[variable_dimensions_dictionary[1]], variable_index_dictionary[variable_dimensions_dictionary[2]]]
        #print  "Temporal resolution from NetCDF= ", len(data[:])

        # Average or sum over spatial subset region
        data_spatial_analysis = spatial_subset(data, method="mean")
        #print "Spatial subset temporal resolution = ", len(data_spatial_analysis)

        dataset = []
        for i in range(len(dates)):
            dataset.append([dates[i], data_spatial_analysis[i]])
        #print dataset
        return dataset

    # Get and sort monthly dates and data
    monthly_dates_and_data = []
    for x in month_list:
        #print x
        monthly_dates_and_data += get_monthly_dates_and_data(x)
    monthly_dates_and_data.sort()

    return monthly_dates_and_data


def process_combined_years_and_data(monthly_dates_and_data, month_list, calculation, start_year, end_year, start_month, end_month, model_name):
    date_list = [i[0] for i in monthly_dates_and_data]
    data = [i[1] for i in monthly_dates_and_data]
    #print date_list

    # Process for results
    results = process_gcm_data(custom_span=len(month_list), sample_method=calculation, date_list=date_list, data=data, start_year=start_year, end_year=end_year, start_month=month_list[0]+1, end_month=month_list[-1]+1)

    # Drop nans
    results = results.dropna()
    #print results, len(results), "results",
    #print "Average for all specified years: ", np.mean(results)
    #print results
    return model_name, np.mean(results)