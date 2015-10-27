# NMME
<pre>
# Setup SECRET_KEY for setting.py
Create a file called local_settings.py
Inside local_settings.py create a variable called SECRET_KEY and assign a string (long, random key).

# Add in local_settings.py
FORCE_SCRIPT_NAME = '/Services'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []


#Required URL parameters for /get-netcdf-data
lat
  The WGS84 latitude for the pixel
lon
  The WGS84 longitude for the pixel
data-path
  URL or local path to the NetCDF file
variable
  Name of the variable to retrieve data from
variable-name
  User specified name for the variable
  If return_JSON = True 
    The JSON object data has a property of user specified variable name
      data.variable-name
      data.myVariableName

#Optional URL parameters for /get-netcdf-data
positive-east-longitude
  True or False
  Default = True
download-csv
  True or False
  Returns the data formated a .csv file
  Default = False
decimal-precision
  Integer Number  0 - 10
  Sets the number of digitals after the decimal
  Default = 6
request-JSON
  True of False
  Returns the data as a JSON object
  Default = False
start-date
  yyyy-mm-dd
  Must also declare with end-date
  Used to filter data by date range
  1950-01-01
end-date
  yyyy-mm-dd
  Must also declare with start-date
  Used to filter data by date range
  1955-01-01
filter-month
  Must be an integer 0-11
  Used to filter data by month
  0 = Jan
  2 = Mar
  11 = Dec


#Required URL parameters for /get-gcm-scatterplot-data
sw-lat
  ex. 45
sw-lon
  ex. -115
ne-lat
  ex. 47
ne-lon
  ex. -116
start-year
  ex. 2006
end-year
  ex. 2099
start-month
  ex. 12 for December
end-month
  ex. 3 Up to but not including March
calculation
  ex. sum
variable
  ex. precipitation
time-frame
  ex. rcp85
get-gcm-scatterplot-data/?sw-lat=45&sw-lon=-115&ne-lat=47&ne-lon=-116&start-year=2006&end-year=2099&start-month=11&end-month=2&calculation=sum&variable=precipitation&time-frame=rcp85


#Required URL parameters for /get-streamflow-data
outlet
  ex. EASW 
variable
  ex. streamflow
product
  ex. ULM
scenario
  ex. rcp85
model
  ex. CCSM4

get-streamflow-data/?outlet=EASW&variable=streamflow&product=ULM&scenario=rcp85&model=CCSM4

#Optional URL parameters for /get-streamflow-data
start-date
  1900-01-01
end-date
  2000-01-01

</pre>