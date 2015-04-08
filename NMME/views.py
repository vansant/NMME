import csv 
from multiprocessing import Pool

import numpy as np
from django.http import HttpResponse

import models


# This sets the NumPy array threshold to infinity so it does not truncate with ...
np.set_printoptions(threshold=np.inf)

def index(request):
    return HttpResponse("Hello, world")

# Pack parameters
def allow_mulitple_parameters(args):
    return models.get_netcdf_data(*args)

def get_netcdf_data(request):
    errors = []

    # Day
    if 'day' in request.GET:
        try:
            day = int(request.GET['day'])
        except:
        	errors.append("Day parameter needs to be an integer")
    else:
    	errors.append("You need to specify a day parameter")

    # Lat
    if 'lat' in request.GET:
        try:
            lat = float(request.GET['lat'])
            if lat < -90 or lat > 90:
                errors.append("Lat parameter needs to within -90 to 90 range")

        except:
            errors.append("Lat parameter needs to be a float")
    else:
        errors.append("You need to specify a lat parameter")

    # Lon
    if 'lon' in request.GET:
        try:
            lon = float(request.GET['lon'])
            if lat < -180 or lat > 180:
                errors.append("Lon parameter needs to within -180 to 180 range")
        except:
            errors.append("Lon parameter needs to be a float")
    else:
        errors.append("You need to specify a lon parameter")

    # Positive east longitude
    if 'positive-east-longitude' in request.GET:
        positive_east_longitude = request.GET['positive-east-longitude']
        if positive_east_longitude == "True" or positive_east_longitude == "False":
            pass
        else:
            errors.append("positive-east-longitude paramater should be either True or False")
    else:
        errors.append("You need to specify a positive-east-longitude parameter")

    # Variable
    if 'variable' in request.GET:
        variable_list = request.GET.getlist('variable')
        print "got the variables", variable_list

        for variable in variable_list:
            if str(variable).isdigit():
                errors.append("variable paramaters must be a a variable name not a number")
            else:
                str(variable)
    else:
        errors.append("You need to specify a variable parameter")

    
    # CSV Download
    if 'download-csv' in request.GET:
        download_csv = request.GET["download-csv"]
        if download_csv == "True" or download_csv == "False":
            pass
        else:
            errors.append("You need to specify a download-csv parameter as True or False")
            
    else:
        errors.append("You need to specify a download-csv parameter")


    # Errors
    if errors:
    	return HttpResponse(errors)
    else:

        # Set number of processes
        p = Pool(len(variable_list)) 

        # List to hold  function parameters as tuples
        # Each set of parameters is for one URL call
        function_parameters = [] 

        # List for all returned netcdf data
        netcdf_data_list = []

        # Process each variable from the variable list
        for v in variable_list:
            function_parameters.append((day,lat,lon,positive_east_longitude,v))

        # Map to pool
        netcdf_data_list.append ( p.map(allow_mulitple_parameters, function_parameters) )

        print len(netcdf_data_list[0][:]), "length of netcdf_data_list"
        #for i in netcdf_data_list[0][1]:
        #    print i
  
        # Download CSV Data
        if download_csv == "True":
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            writer = csv.writer(response)
            writer.writerow([i for i in netcdf_data_list])
            return response
        else:
            # Write CSV to response
            response_string = ""
            #all_data = [ i for i in netcdf_data_list[0]]
            #print all_data

            return HttpResponse([(response_string + "%s," % i) for i in netcdf_data_list])
            #return HttpResponse(netcdf_data)
