import math
import numpy as np
import pandas as pd

def index_from_numpy_array(array, value):
    """ Returns the index of the closest value from from NumPy Array"""
    return (np.abs(array-value)).argmin()

def get_date_no_leap_year(index):
    """ Function to calculate the year-month-day from netCDF4 days since 1900-01-01 index which are calculated with no leap years"""
    year = 1900 + math.floor(index/365)
    doy = index - math.floor(index/365)*365
    month_sum_array = np.array([31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365])
    if doy < month_sum_array[0]:
    	day = doy - 1
    	month = 0
    else:
    	month = np.abs(month_sum_array - doy).argmin()
    	day = doy - month_sum_array[month] - 1
        month = month + 1
    return "%d-%02d-%d" % (year, month+1, day)

def spatial_subset(data, method):
	""" Returns the spatial average or sum for a NetCDF subset region"""
	if method == "sum":
	    return [np.sum(x) for x in data]
	elif method == "mean":
		return [np.mean(x) for x in data]

def custom_resampler(array):
    """ Pandas custom resampler to include resampled dates only if they are available"""
    # print len(array), custom_span_global

    if len(array) == custom_span_global:
        if sample_method_global == "mean":
            return np.mean(array)
        elif sample_method_global == "sum":
            return np.sum(array)

def process_gcm_data(custom_span, sample_method, date_list, data, start_year, end_year, start_month, end_month):

    # Global variables set to be called from custom_resampler method
    global custom_span_global
    global sample_method_global
    custom_span_global = custom_span
    sample_method_global = sample_method

    # Convert list of dates to pandas date_range 
    pandas_date_range = pd.DatetimeIndex(date_list)

    # Create pangdas time series 
    time_series = pd.Series(data, index=pandas_date_range)

    # Filter out the dates of concern
    #print (start_year,start_month), "this is satataetated"
    filtered_time_range =  time_series['%s-%s'%(start_year,start_month):'%s-%s'%(end_year,end_month)]
    #print filtered_time_range

    # M is for pandas months here
    time_span = '%sM' % custom_span

    # Resample daily to monthly values
    resampled_time_series = filtered_time_range.resample(time_span, how=custom_resampler, closed="left", label="right")
    #print resampled_time_series
    return resampled_time_series