from django.http import HttpResponse

import models

def index(request):
    return HttpResponse("Hello, world")

def get_netcdf_data(request):
    errors = []

    if 'day' in request.GET:
        try:
        	day = int(request.GET['day'])
        except:
        	errors.append("Day parameter needs to be an integer")
    else:
    	errors.append("You need to specify a day parameter")

    print errors

    if errors:
    	return HttpResponse(errors)
    else:
        netcdf_data = models.get_data(day=day, lat=42.68244, lon=-113, positive_east_longitude=True, variable='specific_humidity')    
    return HttpResponse(netcdf_data)
