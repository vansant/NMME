import datetime as dt
import json
import csv 
from multiprocessing import Pool

import numpy as np
from django.http import HttpResponse

import models

def filter_dates_by_month(dates, months):
    """" Takes a list of date strings (01-01-1900)  and returns the filtered month(s)
        dates:
            A list of lists containing dates and csv data to filter over
        months:
            A list of months to filter over
            0 is Jan where 11 is Dec
    """

   # Used to map month index to month string value    
    month_dictionary = {0: '01', 1: '02', 2: '03', 3: '04', 4: '05', 5: '06',
         6: '07', 7: '08', 8: '09', 9: '10', 10: '11', 11: '12'}

    # Dictionary to hold monthly data
    month_data_dictionary = {}

    # Add a list for each month to hold data
    for m in months:
        month_data_dictionary[m] = []
 
    # Process each date
    for date in dates:

        # Process each month in the months list
        for month in months:
            #print month_dictionary[month], date[0][5:7]
            if date[0][5:7] == month_dictionary[month]:
                #print date
                month_data_dictionary[month].append(date)
            # else:
            #      print month_dictionary[month], date[0][5:7]

    return  month_data_dictionary     

# This sets the NumPy array threshold to infinity so it does not truncate with ...
np.set_printoptions(threshold=np.inf)

def index(request):
    return HttpResponse("Services Page")

def clean_list_string(input_string):
    """ Removes [ ] and ' characters from a string"""
    i = input_string.replace("'", '')
    i = i.replace('[', '')
    i = i.replace(']', '')
    return i

# Pack parameters
def allow_mulitple_parameters(args):
    return models.get_netcdf_data(*args)

def get_netcdf_data(request):
    errors = []

    # Filter Month
    filter_month = None
    if 'filter-month' in request.GET:
        try:
            filter_month = int(request.GET['filter-month'])
        except:
            errors.append("Enter an integer for the correct month. 0 is January 11 is December")
    # Start date
    start_date = ''
    if 'start-date' in request.GET:
        try:
            start_date = str(request.GET['start-date'])
        except:
            errors.append("Enter  a start-date in yyyy-mm-dd format")
        try:
            dt.datetime.strptime(start_date, "%Y-%m-%d")
        except:
            errors.append("Enter  a start-date in yyyy-mm-dd format")

    # End date
    end_date = ''
    if 'end-date' in request.GET:
        try:
            end_date = str(request.GET['end-date'])
        except:
            errors.append("Enter an end-date in yyyy-mm-dd format")
        try:
            dt.datetime.strptime(end_date, "%Y-%m-%d")
        except:
            errors.append("Enter  a end-date in yyyy-mm-dd format")

    if not start_date == '' or not end_date == '':
        if start_date >= end_date:
            return HttpResponse("start_date can not be greater than or equal to end_date")

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

    positive_east_longitude = "True"
    # Positive east longitude
    if 'positive-east-longitude' in request.GET:
        positive_east_longitude = request.GET['positive-east-longitude']
        if positive_east_longitude == "True" or positive_east_longitude == "False":
            pass
        else:
            errors.append("positive-east-longitude paramater should be either True or False")
    
    # Variable
    if 'variable' in request.GET:
        variable_list = request.GET.getlist('variable')
        #print "got the variables", variable_list

        for variable in variable_list:
            if str(variable).isdigit():
                errors.append("variable paramaters must be a a variable name not a number")
            else:
                str(variable)
    else:
        errors.append("You need to specify a variable parameter")

    # Variable Name
    if 'variable-name' in request.GET:
        variable_name_list = request.GET.getlist('variable-name')
        #print "got the variables names list", variable_name_list

        for variable_name in variable_name_list:
            if str(variable_name).isdigit():
                errors.append("variable names must be a a variable name string not a number")
            else:
                str(variable_name)
    else:
        errors.append("You need to specify a variable-name parameter")

    # Data Path
    if 'data-path' in request.GET:
        data_path_list = request.GET.getlist('data-path')
        #print "got the data paths", data_path_list

        for url in data_path_list:
            if str(url).isdigit():
                errors.append("data-path paramaters must be a a url not a number")
            else:
                str(url)
    else:
        errors.append("You need to specify a data-path parameter")

    # Request JSON parameter
    request_JSON = "False"
    if 'request-JSON' in request.GET:
        request_JSON = request.GET['request-JSON']
        if request_JSON == "True" or request_JSON == "False":
            pass
        else:
            errors.append("You need to specify a request_JSON parameter as True or False")
      

    # Decimal Precision
    decimal_precision = 6
    if 'decimal-precision' in request.GET:
        decimal_precision = request.GET['decimal-precision']
        try:
            decimal_precision = int(decimal_precision)
            if decimal_precision >= 0 and decimal_precision <= 10:

                pass
            else:
                errors.append("You need to specify a decimal_precision parameter as an integer between 0-10")
        except:
            errors.append("You need to specify a decimal_precision parameter as an integer between 0-10")
    # Precision string used to set the number of decimals places after the decimal dynamically
    precision_string = "{0:.%sf}" % decimal_precision   

    # CSV Download
    download_csv = "False"
    if 'download-csv' in request.GET:
        download_csv = request.GET["download-csv"]
        if download_csv == "True" or download_csv == "False":
            pass
        else:
            errors.append("You need to specify a download-csv parameter as True or False")      

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

        # Set request lat lon variable
        request_lat_lon = False
        # List to hold  function parameters as tuples
        # Each set of parameters is for one URL call
        function_parameters = [] 

        # List for all returned netcdf data
        netcdf_data_list = []


        # Get the dates data
        request_dates = "True"
        netcdf_time_list, netcdf_time_index = models.get_netcdf_data(lat, lon, positive_east_longitude, variable_list[0], request_dates, start_year, start_month, start_day, time_metric,time_units, data_path_list[0], request_lat_lon=False, start_date=start_date, end_date=end_date, start_date_index='', end_date_index='' )

        #print netcdf_time_list
        if netcdf_time_list[0] == 'error':
            return HttpResponse("There was an error: " + netcdf_time_list[1] )
        # Index of times that have been filtered
        netcdf_start_date_index = netcdf_time_index[0]
        netcdf_end_date_index = netcdf_time_index[1]
        #print netcdf_start_time_index
        #print netcdf_end_time_index


        # Set as false until request is made later for just the dates
        request_dates = "False"

        # List to hold Metadata items
        metadata_list = []
        metadata_column_list = []

        # Process each variable from the variable list
        #### for url in url LIST

        #print variable_list
        for i in range(len(variable_list)):
            #print i
            function_parameters.append((lat,lon,positive_east_longitude,variable_list[i],request_dates, start_year, start_month, start_day, time_metric,time_units, data_path_list[i], request_lat_lon, start_date, end_date, netcdf_start_date_index, netcdf_end_date_index))
            
            # m returns variable long name, variable units
            m = models.get_netcdf_metadata(lat,lon,positive_east_longitude,variable_list[i],request_dates, start_year, start_month, start_day, time_metric,time_units, data_path_list[i])

            # Contains long names of variables
            metadata_list.append(m[0])

            # Contains user defined variable names and units from metadata
            metadata_column_list.append(variable_name_list[i] + ' (' + m[1] + ')')

        # Map to pool - this gets netcdf data into a workable list
        netcdf_data_list.append ( p.map(allow_mulitple_parameters, function_parameters) )


        #print netcdf_time_list.index("1960-01-01")

        #  After getting all data successfully set request dates false and request_lat_lon true
        request_dates = "False"
        request_lat_lon = "True"
        actual_lat_lon = models.get_netcdf_data(lat, lon, positive_east_longitude, variable_list[0], request_dates, start_year, start_month, start_day, time_metric,time_units, data_path_list[0], request_lat_lon, start_date='', end_date='', start_date_index='', end_date_index='' )
    
        # Converts from U'' to ''
        metadata_column_list = [str(x) for x in metadata_column_list]
        metadata_list = [str(x) for x in metadata_list]

        # Convert metadata colum list to string and clean it up
        metadata_columns_string = str(metadata_column_list)
        metadata_columns_string = clean_list_string(metadata_columns_string)

        #metadata_column_list = [str(x) for x in metadata_column_list]

        # URL data was requested with
        request_path = request.META['HTTP_HOST'] + request.get_full_path()

        # List containing the clean string names of the NetCDF filenames 
        netcdf_filenames_list = [str(x.split('/')[-1]) for x in data_path_list] 
        netcdf_filenames_list = [clean_list_string(x.split('/')[-1]) for x in netcdf_filenames_list] 

        # String to list
        metadata_columns_string_split = metadata_columns_string.split(',')
         

        column_format_csv = [['yyyy-mm-dd']]

        for i in metadata_columns_string_split:
            
            column_format_csv[0].append(i)

        #print column_format_csv

        # Metadata header section
        metadata_header = """#Variables:<br />""" 
        for i in range(len(metadata_list)):
            #print i
            metadata_header +=  "#" + metadata_columns_string_split[i] + ":" + str(metadata_list[i]) + "<br />"

        #print netcdf_filenames_list

        # Add Lat/Lon to Metadata header
        metadata_header += "#Data Extracted for Point Location: %.4f Latitude, %.4f Longitude (closest value to Latitude:%s, Longitude:%s)" % (actual_lat_lon[0], actual_lat_lon[1], lat,lon )
 
        metadata_variable_string = ""
        for i in netcdf_filenames_list:
            metadata_variable_string += "#%s <br />" % i

        if download_csv == "False":
            # Get metadata
            metadata = "%s <br />#Original Data File(s):<br />%s#===============================================<br />yyyy-mm-dd,%s<br />" %  (metadata_header, metadata_variable_string, metadata_columns_string)
        else:
            metadata = "%s <br />#Original Data File(s):<br />%s#===============================================<br />" %  (metadata_header, metadata_variable_string)

        metadata_rows = metadata.split("<br />")
        #for r in metadata_rows:
            #print type(r), r

        #print metadata_rows
        # Write CSV style response
        response_string = ""
        response_rows = []
        variable_columns = []

        for variable_dataset in netcdf_data_list[0]:
            # Convert to float and truncate to decimal precision variable
            variable_dataset = [precision_string.format(float(i)) for i in variable_dataset]
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

        if filter_month >=0 or filter_month <= 11:
            # Concatenate lists to stings
            response_rows_strings = [[','.join(x)] for x in response_rows]
            #print response_rows_strings
            filtered_dates = filter_dates_by_month(dates=response_rows_strings, months=[filter_month])

            #print filtered_dates
            response_rows = [x[0].split(',') for x in filtered_dates[int(filter_month)]]

        response_metadata_rows = []
        # Create metadata rows
        for i in range(len(metadata_rows)):
            new_row = []
            new_row.append(metadata_rows[i])
            response_metadata_rows.append(new_row)

        def rows_to_JSON(column_names, row_data):
            """ Process rows into dictionary objects (columns) to convert to JSON"""

            #Dictionary of JSON rows
            JSON_dictionary = {"metadata": metadata_rows
            }

            # Loop through each column and set the colunm name for JSON and assign data
            for i in range(len(column_names)):
                column_data = [row[i] for row in response_rows]
                JSON_dictionary[column_names[i].split(" ")[0]] = column_data
                object_for_JSON = {"data":
                        [
                            JSON_dictionary,
                        ]
                    }
            return object_for_JSON

        # Get JSON Data
        if request_JSON == "True":
            # Convert the data to dictionary to get converted into JSON
            object_for_JSON = rows_to_JSON(column_format_csv[0], response_rows)
            #print JSON_dictionary
            response = json.dumps(object_for_JSON)
            return HttpResponse(response, content_type="application/json")

        # Download CSV Data
        if download_csv == "True":
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            writer = csv.writer(response)
            
            # Get Metadata rows
            for row in response_metadata_rows:
                writer.writerow(row)
            
            for row in column_format_csv:
                writer.writerow(row)

            # Get data rows
            for row in response_rows:
                #print row
                writer.writerow(row)
            return response
        else:

            # convert rows to string
            for r in response_rows:
                # Convert list to string
                r = str(r)

                # Remove square bracket
                response_string += r
                
                response_string += "<br //>"

            response_string = clean_list_string(response_string)   

            #return HttpResponse([(response_string + "%s," % i) for i in netcdf_data_list])
            return HttpResponse(metadata+response_string)

def chart_netcdf_data(request):
    response = """
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8">
  <title> NetCDF highcharts demo</title>
  <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
  <meta charset="utf-8">
  <style>
      html, body {
        height: 100%;
        width: 100%;
        margin: 0;
        padding: 0;
      }

      #map-canvas, #chart-container, #form-container, #data-container {
        height: 50%;
        width: 50%;
        float: left;
      }

      #form-container{
              clear: left;
      }


  </style>
  <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&signed_in=true"></script>
  <script type='text/javascript' src='//code.jquery.com/jquery-1.9.1.js'></script>
  <script type='text/javascript'>

    function load_chart_data(){
    //alert('calling function');
    var jqxhr = $.ajax({
                url: "/get-netcdf-data",
                method: "GET",
                data: $("#my_form").serialize(),
            })
            .done(function(response) {
                //console.log(data);
                //alert( data.metadata );

                // Assign data from JSON notice the different formats??
                var myVar = response.data[0]['tasmax'];
                var dates = response.data[0]['yyyy-mm-dd'];

                //Remove old data if it's there
                $("#data-container").removeData();

                // Set the data
                $("#data-container").append(dates);
                $("#data-container").append(myVar);

                //ar asdf = JSON.parse(dates);
                var dates_arr = jQuery.makeArray(dates);
                var myVar_arr = jQuery.makeArray(myVar);
                console.log(typeof(myVar_arr));

                // Map over each data value and convert it to a float
                var myVar_arr = myVar_arr.map(function(i) {
                    return parseFloat(i)
                });

                $('#chart-container').highcharts({
                    title: {
                        text: 'Title of the chart',
                        x: -20 //center
                    },
                    subtitle: {
                        text: 'Source: climate.nkn.uidaho.edu',
                        x: -20
                    },
                    xAxis: {
                        type: 'datetime',
                        categories: dates_arr,
                        turboThreshold: 0
                    },
                    yAxis: {
                        title: {
                            text: 'Variable (units)'
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    tooltip: {
                        valueSuffix: 'variable units'
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        borderWidth: 0
                    },
                    series: [{
                        name: $('#variable-name').val(),
                        data: myVar_arr,
                        turboThreshold: 0
                    }]
                }); // end highchart

            }) // successfully got JSON response

        //.fail(function() {
        //    alert("Did not load resource");
        //})

        $("#cancel_button").click(function() {
            jqxhr.abort()
            alert("Handler for .click() called. Ignoring AJAX call");
        }); // Cancel the request

    }

    $( document ).ready(function() {

$('#chart-container').highcharts({
                    title: {
                        text: 'Title of the chart',
                        x: -20 //center
                    },
                    subtitle: {
                        text: 'Source: climate.nkn.uidaho.edu',
                        x: -20
                    },
                    xAxis: {
                        type: 'datetime',
                        turboThreshold: 0
                    },
                    yAxis: {
                        title: {
                            text: 'Variable (units)'
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    tooltip: {
                        valueSuffix: 'variable units'
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        borderWidth: 0
                    },
                    series: [{
                        name: 'Example',
                        turboThreshold: 0
                    }]
                }); // end highchart


        $("#submit_button").click(function(event) {
            event.preventDefault();
            load_chart_data();
            //alert($("#my_form").serialize());
            //window.open("http://localhost:8000/get-netcdf-data/?" + $("#my_form").serialize());
        }); // Submit the request


    
    });
</script>

    <script>
function initialize() {
  var mapOptions = {
    zoom: 4,
    center: new google.maps.LatLng(41, -100)
  };

  var map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);

  var marker = new google.maps.Marker({
    position: map.getCenter(),
    draggable: true,
    map: map,
    title: 'Click to zoom'
  });



  google.maps.event.addListener(marker, 'drag', function(event) {
    //alert(event.latLng);
    //map.setZoom(8);
    //map.setCenter(marker.getPosition());
    $("#lat").val(event.latLng.lat());
    $("#lon").val(event.latLng.lng());
  });

  google.maps.event.addListener(marker, 'dragend', function(event) {
    //alert(event.latLng);
    //map.setZoom(8);
    //map.setCenter(marker.getPosition());
    $("#lat").val(event.latLng.lat());
    $("#lon").val(event.latLng.lng());
  });
}

google.maps.event.addDomListener(window, 'load', initialize);

    </script>

</head>
<body>
<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/modules/exporting.js"></script>
<div id="map-canvas"></div>
<div id="chart-container" style="min-width: 310px; height: 400px; margin: 0 auto"></div>
<div id="form-container">
<form id="my_form">
</br>
lat: <input type="text" value="41" id="lat" name="lat">
</br>
lon: <input type="text" value="-100" id="lon" name="lon">
</br>
Data path: <input type="text"  name="data-path"value="http://inside-dev1.nkn.uidaho.edu:8080/thredds/dodsC/agg_macav2metdata_tasmax_bcc-csm1-1_r1i1p1_historical_1950_2005_CONUS_daily.nc
" id="data-path">
</br>
variable: <input type="text" id="variable" value="air_temperature" name="variable">
</br>
variable name: <input type="text" id="variable-name" value="tasmax" name="variable-name">
</br>
start date: <input type="date" id="start-date" value="1980-01-01" name="start-date">
</br>
end date: <input type="date" id="end-date" value="1980-02-02" name="end-date">
</br>
request as JSON: <input type="text" id="request-JSON" value="True" name="request-JSON">
<br/>
Filter by Month: <input type="text" id="filter-month" value="0" name="filter-month">
<br/>
<input type="submit" value="Request chart" id="submit_button">
<input type="submit" value="Cancel request" id="cancel_button">
</form>
</div>
<div id="data-container"></div>
</body>
</html>
    """

    return HttpResponse(response)