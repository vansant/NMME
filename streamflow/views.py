# Create your views here.
from django.http import HttpResponse

#import json
#import csv
from multiprocessing import Pool

#import numpy as np
from django.http import HttpResponse

#import inputs ...where can I put other files in Django? 

#============================================================================
# CHECK INPUTS 
#============================================================================
def check_inputs(request):

    errors = []
    #======================
    # year-start
    #======================
    year_start = ""
    if 'year-start' in request.GET:
        try:
            year_start = int(request.GET['year-start'])
            if year_start<2006 or year_start>2099: 
                errors.append("Integer year-start must be between 2006 and 2099. ")
        except:
            errors.append("Enter an integer for the year-start between 2006 and 2099. ")
    #======================
    # year-end
    #======================
    year_end = ""
    if 'year-end' in request.GET:
        try:
            year_end = int(request.GET['year-end'])
            if year_end<2006 or year_end>2099:
                errors.append("Integer year-start must be between 2006 and 2099. ")
            if year_end<year_start:
                errors.append("Integer year-start must be less than or equal to year-end. ")
        except:
            errors.append("Enter an integer for the year-end between 2006 and 2099. ")

    #======================
    # outlet 
    #======================
    outlet = ""
    if 'outlet' in request.GET:
        try:
            outlet = str(request.GET['outlet'])
        except:
            errors.append("Parameter outlet must be ...")
    #======================
    # variable 
    #======================
    variable ='' 
    if 'variable' in request.GET:
        try:
            variable = str(request.GET['variable'])
        except:
            errors.append("Parameter variable must be ...")
    #======================
    # product
    #======================
    product = ""
    if 'product' in request.GET:
        try:
            product = str(request.GET['product'])
        except:
            errors.append("Product must be ...")
    #======================
    return outlet, variable,product,year_start,year_end,errors
    #======================

#============================================================================
# MAIN ROUTINE: STREAMFLOW
#============================================================================
def streamflow(request):
    errors = []

    outlet,variable,product,year_start,year_end,errors = check_inputs(request)

    if errors:
        return HttpResponse(errors)
    else:
        # Set number of processes to the number of variables being called
        #p = Pool(20)

        # Set request lat lon variable
        request_lat_lon = False

        # List to hold  function parameters as tuples
        # Each set of parameters is for one URL call
        function_parameters = []

        # List for all returned netcdf data
        streamflow_data_list = []

        # Get the dates data
        request_dates = "True"

        #streamflow_time_list, netcdf_time_index = models.get_netcdf_data(lat, lon, positive_east_longitude, variable_list[0], request_dates, start_year, start_month, start_day, time_metric,time_units, data_path_list[0], request_lat_lon=False, start_date=start_date, end_date=end_date, start_date_index='', end_date_index='' )

        #print netcdf_time_list
        #if sreamflow_time_list[0] == 'error':
        #    return HttpResponse("There was an error: " + netcdf_time_list[1] )

        #streamflow_start_date_index = streamflow_time_index[0]
        #streamflow_end_date_index = streamflow_time_index[1]

        # List to hold Metadata items
        metadata_list = []
        metadata_column_list = []

        # Process each model from the model list

        return HttpResponse("outlet="+outlet+"<br> variable="+variable+"<br>year_start="+str(year_start)+"<br>year_end="+str(year_end)+"<br>product="+product)
