from django.conf.urls import patterns, url, include
from django.views.generic.base import RedirectView
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

import uapp

urlpatterns = patterns('uapp.views',
	(r'^uapp/add_app/(?P<app_str>\w*)$', 'add_app'),
	(r'^add_user/', 'add_user'),
	(r'^uapp/listClients/$', 'listClients'),
	(r'^uapp/listApps/$', 'listApps'),
	(r'^uapp/listAppNames/$', 'listAppNames'),
	(r'^uapp/listGroups/$', 'listGroups'),
	(r'^uapp/getClientApps/(?P<imei>\w*)$', 'getClientApps'),
	(r'^uapp/getClientTags/(?P<imei>\w*)$', 'getClientTags'),
	(r'^uapp/getClientLogs/(?P<imei>\w*)$', 'getClientLogs'),
	(r'^uapp/deleteClients/$', 'deleteClients'),
	(r'^uapp/getGroupApps/(?P<groupname>\w*)$', 'getGroupApps'),
	(r'^getGroupClients/(?P<groupname>\w*)$', 'getGroupClients'),
	(r'^getClientInfo/(?P<imei>\w*)$', 'getClientInfo'),
	
	
	(r'^add_group/$', 'add_group'),
	(r'^edit_group/$', 'edit_group'),
	(r'^edit_client/$', 'edit_client'),
	(r'^group_details/(?P<groupname>\w*)$', 'group_details'),
	(r'^client_details/(?P<imei>\w*)$', 'client_details'),
	(r'^app_details/', 'app_details'),
	
	(r'^groups/delete/$', 'delete_group'),
	(r'^apps/delete/$', 'delete_app_version'),
	(r'^uapp/delete_app_version/$', 'delete_app_version'),
	(r'^getAppReleases/(?P<appname>\w*)$', 'getAppReleases'),
	(r'^getReleaseVersions/(?P<appname>\w*)/(?P<release>[a-zA-Z0-9_\-.]*)$', 'getReleaseVersions'),
	(r'^uapp/getAppDetails/$', 'getAppDetails'),
	(r'^uapp/getAppGroups/(?P<appname>\w*)/(?P<release>[a-zA-Z0-9_\-.]*)/(?P<version>\w*)$', 'getAppGroups'),
	(r'^uapp/batchEditClients/(?P<validated>\w*)$', 'batchEditClients'),
	(r'^uapp/get/(?P<imei>\w*)$', 'get'),
	(r'^uapp/register/', 'register'),

	
	# Needs to be re-written for data model change
	(r'^uapp/logs/$', 'logs'),
        (r'^uapp/logs/(?P<imei>\w+)$', 'logs_imei'),
        (r'^uapp/logs/group/(?P<group>\w+)$', 'logs_group'),
        (r'^clients/search/imeis_groups$','search_imeis_groups'),
        (r'^clients/search/imeis$','search_imeis'),
)

urlpatterns += patterns('',
    (r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login1.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'login1.html','next_page': '/login/'}),
    (r'^$', RedirectView.as_view(url="http://localhost:8000/clients/")),
    (r'^clients/$', 'uapp.views.show_clients'),
    (r'^groups/$', 'uapp.views.show_groups'),
    (r'^applications/$', 'uapp.views.show_applications'),
    (r'^logs/$', 'uapp.views.show_logs'),
    
)
