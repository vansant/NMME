from django.conf.urls import patterns, include, url
from django.contrib import admin

import views

urlpatterns = patterns('',
        url(r'^$', 'NMME.views.index', name='index'),
        url(r'^get-netcdf-data/', 'NMME.views.get_netcdf_data', name='get_netcdf_data'),
        url(r'^chart-netcdf-data/', 'NMME.views.chart_netcdf_data', name='chart_netcdf_data'),
        url(r'^get-streamflow-data/', 'streamflow.views.streamflow', name='get_streamflow_data'),
        url(r'^get-gcm-scatterplot-data/', 'gcm.views.get_scatterplot_data', name='get_scatterplot_data'),
        url(r'^get-local-gcm-scatterplot-data/', 'gcm.views2.get_scatterplot_data', name='get_scatterplot_data'),
        url(r'^get-summary-gcm-scatterplot-data/', 'gcm.views3.get_scatterplot_data', name='get_scatterplot_data'),
)

