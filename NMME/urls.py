from django.conf.urls import patterns, include, url
from django.contrib import admin

import views

from local_settings import DEBUG

if DEBUG == True:
    urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'NMME.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),
        #url(r'^admin/', include(admin.site.urls)),
        url(r'^$', 'NMME.views.index', name='index'),
        url(r'^get-netcdf-data/', 'NMME.views.get_netcdf_data', name='get_netcdf_data'),
)

# URLs to work with sub path in Production /Services
else:
    urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'NMME.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),
        #url(r'^admin/', include(admin.site.urls)),
        url(r'^$', 'NMME.views.index', name='index'),
        url(r'^/$', 'NMME.views.index', name='index'),
        url(r'^/get-netcdf-data/', 'NMME.views.get_netcdf_data', name='get_netcdf_data'),
)

