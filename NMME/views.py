from django.http import HttpResponse

import models

def index(request):
    return HttpResponse("Hello, world")

def get_netcdf_data(request):
    netcdf_data = models.get_data(day=1, lat=42.68244, lon=-113, positive_east_longitude=True, variable='specific_humidity')    
    return HttpResponse(netcdf_data)
