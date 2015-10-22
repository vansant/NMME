from multiprocessing import Pool
import numpy as np
from django.http import HttpResponse
from netCDF4 import Dataset
from models import  get_date_no_leap_year, spatial_subset, custom_resampler, process_gcm_data, index_from_numpy_array
import json

def get_scatterplot_data(request):
	""" View that calculate the temporal average from a NETCDF4 file for a spatial region"""
	errors = []

	# start_month
	if 'start-month' in request.GET:
		try:
			start_month = int(request.GET['start-month'])
			if start_month < 0 or start_month > 11 :
				errors.append("start-month parameter needs to to be between 0-11. 0 is Jan where 1 is Dec")
		except:
			errors.append("start-month parameter needs to be a int")
	else:
		errors.append("You need to specify a start-month parameter")

	# end_month
	if 'end-month' in request.GET:
		try:
			end_month = int(request.GET['end-month'])
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

	#product = "Maca"


	# List of GCM models and runs
	model_and_run_list = ['IPSL-CM5A-LR_r1i1p1', 'HadGEM2-CC365_r1i1p1', 'inmcm4_r1i1p1', 'MIROC-ESM_r1i1p1', 'CNRM-CM5_r1i1p1', 'MIROC5_r1i1p1', 'CanESM2_r1i1p1', 'MIROC-ESM-CHEM_r1i1p1', 'BNU-ESM_r1i1p1', 'IPSL-CM5B-LR_r1i1p1', 'HadGEM2-ES365_r1i1p1', 'GFDL-ESM2G_r1i1p1', 'bcc-csm1-1-m_r1i1p1', 'MRI-CGCM3_r1i1p1', 'GFDL-ESM2M_r1i1p1', 'CSIRO-Mk3-6-0_r1i1p1', 'NorESM1-M_r1i1p1', 'bcc-csm1-1_r1i1p1', 'IPSL-CM5A-MR_r1i1p1', 'CCSM4_r6i1p1']
	time_list = ["historical_1950_2005", "rcp45_2006_2099", "rcp85_2006_2099"]
	#variable_list = ['pr', 'rsds', 'huss', 'tasmin', 'tasmax', 'was']

	if time_frame == "historical":
		time_range = time_list[0]
	if time_frame == "rcp45":
		time_range = time_list[1]
	if time_frame == "rcp85":
		time_range = time_list[2]

	variable_dictionary = {'specific_humidity':'huss', 'precipitation':'pr', 'air_temperature':'tasmax', 'surface_downwelling_shortwave_flux_in_air':'rsds', 'air_temperature':'tasmin', }

	# Process each model and run
	for model_and_run in model_and_run_list:
		data_path="http://thredds.northwestknowledge.net:8080/thredds/dodsC/macav2livneh_%s_%s_%s_CONUS_monthly_aggregated.nc" % (variable_dictionary[variable], model_and_run, time_range)
		#print model_and_run, data_path
		model_name = model_and_run.split("_")[0]
		#print model_name
		function_parameters.append((sw_lat, sw_lon, ne_lon, ne_lat, month_list, start_year, end_year, end_month, start_month, variable, data_path, calculation, model_name))

	# Map to pool - this gets netcdf data into a workable list
	netcdf_data_list.append ( p.map(allow_mulitple_parameters, function_parameters) )

	# Close subprocess workers (open files)
	p.terminate()
	p.join()

    #Dictionary of JSON rows
	JSON_dictionary = {}

	# Loop through each column and set the colunm name for JSON and assign data
	#print len(netcdf_data_list[0])
	for i in range(len(netcdf_data_list[0])):
		#print netcdf_data_list[0][i][0], type(netcdf_data_list[0][i][0])
		JSON_dictionary[netcdf_data_list[0][i][0]] = netcdf_data_list[0][i][1]
	
	object_for_JSON = {"data":[JSON_dictionary,]}
	response = json.dumps(object_for_JSON)
	
	return HttpResponse(response, content_type="application/json")

	#return HttpResponse(netcdf_data_list)

# Pack parameters
def allow_mulitple_parameters(args):
    return process_data(*args)

def process_data(sw_lat, sw_lon, ne_lon, ne_lat, month_list, start_year, end_year, end_month, start_month, variable, data_path, calculation, model_name):

	# File handles
	pathname = data_path
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
	closestLon = slice(ne_lon, sw_lon)

	# Which months to get data for
	#month_list = [11,0,1]

	def get_monthly_dates_and_data(month):
		""" Function that get dates and data for a single month from a NetCDF File"""
		# Month to get data for
		request_month = month

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
		return dataset

	# Get and sort monthly dates and data
	monthly_dates_and_data = []
	for x in month_list:
		#print x
		monthly_dates_and_data += get_monthly_dates_and_data(x)
	monthly_dates_and_data.sort()

	#print monthly_dates_and_data

	date_list = [i[0] for i in monthly_dates_and_data]
	data = [i[1] for i in monthly_dates_and_data]
	#print date_list

	# Process for results
	results = process_gcm_data(custom_span=len(month_list), sample_method=calculation, date_list=date_list, data=data, start_year=start_year, end_year=end_year, start_month=month_list[0]+1, end_month=month_list[-1]+1)

	# Drop nans
	results = results.dropna()
	#print results, len(results), "results",
	#print "Average for all specified years: ", np.mean(results)
	return model_name, np.mean(results)

