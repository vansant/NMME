from django.conf.urls import patterns, include, url
from django.contrib import admin

import views

urlpatterns = patterns('',
        url(r'^$', 'NMME.views.index', name='index'),
        url(r'^get-netcdf-data/', 'NMME.views.get_netcdf_data', name='get_netcdf_data'),
        url(r'^chart-netcdf-data/', 'NMME.views.chart_netcdf_data', name='chart_netcdf_data'),
)

