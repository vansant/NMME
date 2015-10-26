import json
from django.http import HttpResponse
from multiprocessing import Pool
from django.http import HttpResponse
import models

def streamflow(request):
    errors = []

    # Outlet
    if 'outlet' in request.GET:
        try:
            outlet = request.GET['outlet']
        except:
            errors.append("outlet parameter needs to be a string")
    else:
        errors.append("You need to specify an outlet parameter")
   
    # Variable
    if 'variable' in request.GET:
        try:
            variable = request.GET['variable']
        except:
            errors.append("variable parameter needs to be a string")
    else:
        errors.append("You need to specify a variable parameter")

    # Product
    if 'product' in request.GET:
        try:
            product = request.GET['product']
        except:
            errors.append("product parameter needs to be a string")
    else:
        errors.append("You need to specify a product parameter")

    # Scenario
    if 'scenario' in request.GET:
        try:
            scenario = request.GET['scenario']
        except:
            errors.append("scenario parameter needs to be a string")
    else:
        errors.append("You need to specify a scenario parameter")

    if scenario == "historicalstream":
        model = "None"
    else:    
        # Model
        if 'model' in request.GET:
            try:
                model = request.GET['model']
            except:
                errors.append("model parameter needs to be a string")
        else:
            errors.append("You need to specify a model parameter")

    # Start Date
    start_date = ''
    if 'start-date' in request.GET:
        try:
            start_date = request.GET['start-date']
        except:
            errors.append("start-date parameter needs to be a string like 1950-01-01")

    # End Date
    end_date = ''
    if 'end-date' in request.GET:
        try:
            end_date = request.GET['end-date']
        except:
            errors.append("end-date parameter needs to be a string like 1950-01-01")

    if errors:
        return HttpResponse(errors)

    data = models.get_streamflow_data(outlet, variable, product, scenario, model, start_date, end_date)
    
    # Dictionary of JSON rows
    JSON_dictionary = {}

    month_name_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    netcdf_data_list = {}

    # Loop through each column and set the colunm name for JSON and assign data
    for i in range(len(month_name_list)):
        JSON_dictionary[month_name_list[i]] = float(data[i])
    
    object_for_JSON = {"data":[JSON_dictionary,]}
    response = json.dumps(object_for_JSON)
    
    return HttpResponse(response, content_type="application/json")