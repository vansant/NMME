import csv 

from django.http import HttpResponse

import models

def index(request):
    return HttpResponse("Hello, world")

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
        variable = request.GET['variable']
        if str(variable).isdigit():
            errors.append("variable paramater must be a a variable name not a number")
        else:
            variable = str(variable)
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
        # Get data from NetCDF
        netcdf_data = models.get_netcdf_data(day=day, lat=lat, lon=lon,
                                      positive_east_longitude=positive_east_longitude,
                                      variable=variable)    
        # Download CSV Data
        if download_csv == "True":
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            writer = csv.writer(response)
            writer.writerow([i for i in netcdf_data])
            return response
        else:
            # Write CSV to response
            response_string = ""

            return HttpResponse([(response_string + "%s," % i) for i in netcdf_data])
            #return HttpResponse(netcdf_data)
