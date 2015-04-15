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


    start_year=1900
    start_month=1
    start_day=1
    time_metric="days"
    time_units=1


    # Errors
    if errors:
    	return HttpResponse(errors)
    else:

        # Set number of processes to the number of variables being called
        p = Pool(len(variable_list)) 

        # List to hold  function parameters as tuples
        # Each set of parameters is for one URL call
        function_parameters = [] 

        # List for all returned netcdf data
        netcdf_data_list = []

        # Set as false until request is made later for just the dates
        request_dates = "False"

        # Process each variable from the variable list
        for v in variable_list:
            function_parameters.append((day,lat,lon,positive_east_longitude,v,request_dates, start_year, start_month, start_day, time_metric,time_units))

        # Map to pool - this gets netcdf data into a workable list
        netcdf_data_list.append ( p.map(allow_mulitple_parameters, function_parameters) )

        # After getting all data successfully we call the dates
        request_dates = "True"
        netcdf_time_list = models.get_netcdf_data(day, lat, lon, positive_east_longitude, variable, request_dates, start_year, start_month, start_day, time_metric,time_units)

        print len(netcdf_data_list[0]), "length of netcdf_data_list"
        print len(netcdf_time_list), "lengith of netcdf_time_list"
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
            # Write CSV style response
            response_string = ""
            response_rows = []
            variable_columns = []

            for variable_dataset in netcdf_data_list[0]:
                variable_columns.append(variable_dataset)

            # Create time and variable rows
            for i in range(len(netcdf_time_list)):
                new_row = []
                new_row.append(netcdf_time_list[i])
                for v in variable_columns:
                    new_row.append(v[i])

                #for x in new_row:
                response_rows.append(new_row)
                 #   new_row = []
                
            #print len(new_row), 'rows this wide'
                #print netcdf_time_list[i], variable_columns[0][i], variable_columns[1][i]
            
            #print len(variable_columns)
                #print variable_dataset[:]
            # Build the response string
            #for i in range(len(netcdf_data_list[0])):
            #    for j in range(len(netcdf_time_list)):
            #        response_rows.append(netcdf_time_list[j], netcdf_data_list[0][i][j] )
            #        #response_string.append(netcdf_data_list[0][i][j])
            #        #print netcdf_time_list[j], netcdf_data_list[0][i][j]
            #        for row in rows:
            #            print response_rows
                
                
            #all_data = [ i for i in netcdf_data_list[0]]
            #print all_data
            # convert rows to string
            for r in response_rows:
                # Convert list to string
                r = str(r)

                # Remove square bracket
                response_string += r
                
                response_string += "<br //>"
            #processed_response_string = response_string.replace("[]", "")
            #print processed_response_string
            response_string = response_string.replace('[', '')
            response_string = response_string.replace(']', '')
            response_string = response_string.replace("'", '')
            print type(response_string)
               

            #return HttpResponse([(response_string + "%s," % i) for i in netcdf_data_list])
            return HttpResponse(response_string)
