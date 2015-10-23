# Create your views here.
from django.http import HttpResponse

#import json
#import csv
from multiprocessing import Pool

#import numpy as np
from django.http import HttpResponse
import models

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

        # List to hold function parameters as tuples
        # Each set of parameters is for one URL call
        function_parameters = []

        # List for all returned netcdf data
        streamflow_data_list = []

        # Get the dates data
        request_dates = "True"

        #scenario='historical'
        scenario='historicalstream'
        #scenario='rcp45'
        model=''
        netcdf_time_list, netcdf_time_index=models.get_streamflow_data(outlet, variable, product,year_start, year_end,scenario,model,request_dates,['',''])

        #print netcdf_time_list
        if netcdf_time_list[0] == 'error':
            return HttpResponse("There was an error: " + netcdf_time_list[1] )

        netcdf_start_date_index = netcdf_time_index[0]
        netcdf_end_date_index = netcdf_time_index[1]

        # Set as false until request is made later for just the dates
        request_dates = "False"

        # List to hold Metadata items
        metadata_list = []
        metadata_column_list = []

        model_list=['bcc-csm1-1','NorESM1-M']
        #model_list=['bcc-csm1-1','NorESM1-M','MIROC5','IPSL-CM5A-MR','HadGEM2-ES365','HadGEM2-CC365','CanESM2','CSIRO-Mk3-6-0','CNRM-CM5','CCSM4']
	print len(model_list)
        # Process each model from the model list
        for i in range(len(model_list)):
            print model_list[i]
            #function_parameters.append((lat,lon,positive_east_longitude,variable_list[i],request_dates, start_year, start_month, start_day, time_metric,time_units, data_path_list[i], request_lat_lon, start_date, end_date, netcdf_start_date_index, netcdf_end_date_index))

            # m returns variable long name, variable units
            m = models.get_streamflow_data(outlet, variable, product,year_start, year_end,scenario,model_list[i],request_dates,netcdf_time_index)

            # Contains long names of variables
            metadata_list.append(m[0])

            # Contains user defined variable names and units from metadata
            metadata_column_list.append(variable_name_list[i] + ' (' + m[1] + ')')


        # Map to pool - this gets netcdf data into a workable list
        netcdf_data_list.append ( p.map(allow_mulitple_parameters, function_parameters) )

        # Close subprocess workers (open files)
        #p.terminate()
        #p.join()
        #print netcdf_time_list.index("1960-01-01")

        # Converts from U'' to ''
        metadata_column_list = [str(x) for x in metadata_column_list]
        metadata_list = [str(x) for x in metadata_list]

        # Convert metadata colum list to string and clean it up
        metadata_columns_string = str(metadata_column_list)
        metadata_columns_string = clean_list_string(metadata_columns_string)

        #metadata_column_list = [str(x) for x in metadata_column_list]

        # URL data was requested with
        request_path = request.META['HTTP_HOST'] + request.get_full_path()

        # List containing the clean string names of the NetCDF filenames
        netcdf_filenames_list = [str(x.split('/')[-1]) for x in data_path_list]
        netcdf_filenames_list = [clean_list_string(x.split('/')[-1]) for x in netcdf_filenames_list] 


        return HttpResponse("outlet="+outlet+"<br> variable="+variable+"<br>year_start="+str(year_start)+"<br>year_end="+str(year_end)+"<br>product="+product)
