import numpy as np

from django.http import HttpResponse
from netCDF4 import Dataset

from .models import  get_date_no_leap_year, spatial_subset, custom_resampler, process_gcm_data, index_from_numpy_array


def get_scatterplot_data(request):
	""" View that calculate the average DJF from a NETCDF4 file for a spatial region"""
	errors = []

	#calculation = 'sum'
	#SWLat = 45
	#SWLong= -115
	#NELat= 47
	#NELong= -117

	#monthStart = 12
	#monthEnd = 2
	#yearStart = 1950
	#yearEnd = 2005

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

	if errors:
		return HttpResponse(errors)

	# URL parameters
	#data_path = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/NWCSC_INTEGRATED_SCENARIOS_ALL_CLIMATE/projections/nmme/bcsd_nmme_metdata_NCAR_forecast_daily.nc"
	data_path = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/macav2livneh_pr_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_monthly_aggregated.nc"
	variable = "precipitation"

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
	month_list = [11,0,1]

	def get_monthly_dates_and_data(month):
		""" Function that get dates and data for a single month from a NetCDF File"""
		# Month to get data for
		request_month = month

		print request_month

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
		monthly_dates_and_data += get_monthly_dates_and_data(x)
	monthly_dates_and_data.sort()

	print monthly_dates_and_data

	date_list = [i[0] for i in monthly_dates_and_data]
	data = [i[1] for i in monthly_dates_and_data]
	#print date_list

	# Process for results
	results = process_gcm_data(custom_span=len(month_list), sample_method="mean", date_list=date_list, data=data, start_year=1950, end_year=2100, start_month=month_list[0]+1, end_month=month_list[-1]+1)

	# Drop nans
	results = results.dropna()
	print results, len(results), "results",
	print "Average for all specified years: ", np.mean(results)
	
	return HttpResponse(np.mean(results))

