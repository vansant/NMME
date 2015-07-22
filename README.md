# NMME

# Setup SECRET_KEY for setting.py
Create a file called local_settings.py
Inside local_settings.py create a variable called SECRET_KEY and assign a string (long, random key).

# Add in local_settings.py
FORCE_SCRIPT_NAME = '/Services'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

<pre>
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
</pre>