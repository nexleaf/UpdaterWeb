from django.conf.urls import patterns, url, include
from django.views.generic.base import RedirectView
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

import uapp
#from UpdaterServer import uapp

urlpatterns = patterns('uapp.views',
	# (r'^uapp/add_app/(?P<app_str>\w*)$', 'add_app'),
	# (r'^uapp/listClients/$', 'listClients'),
	# (r'^uapp/listApps/$', 'listApps'),
	# (r'^uapp/listAppNames/$', 'listAppNames'),
	# (r'^uapp/listGroups/$', 'listGroups'),
	(r'^uapp/getClientApps/(?P<imei>\w*)$', 'getClientApps'),
	(r'^uapp/getClientTags/(?P<imei>\w*)$', 'getClientTags'),
	(r'^uapp/getClientLogs/(?P<imei>\w*)$', 'getClientLogs'),
	# (r'^uapp/deleteClients/$', 'deleteClients'),
	# (r'^uapp/delete_app_version/$', 'delete_app_version'),
	(r'^uapp/getGroupApps/(?P<groupname>\w*)$', 'getGroupApps'),
	(r'^uapp/getAppGroups/(?P<appname>\w*)/(?P<release>[a-zA-Z0-9_\-.]*)/(?P<version>\w*)$', 'getAppGroups'),
	(r'^uapp/batchEditClients/(?P<validated>\w*)$', 'batchEditClients'),
	(r'^updater/uapp/get/(?P<imei>\w*)$', 'get'),
	(r'^updater/uapp/get1/(?P<imei>\w*)$', 'get1'),
	(r'^uapp/register/', 'register'),
	# (r'^uapp/getAppDetails/$', 'getAppDetails'),
	
	(r'^clients/add/$', 'add_client'),
	(r'^clients/edit/$', 'edit_client'),
	(r'^clients/details/(?P<imei>\w*)$', 'client_details'),
	(r'^clients/delete/$', 'delete_client'),
	(r'^getGroupClients/(?P<groupname>\w*)$', 'getGroupClients'),
	(r'^clients/search/imeis_groups$','search_imeis_groups'),
	(r'^clients/search/imeis$','search_imeis'),
	(r'^clients/$', 'show_clients'),
	(r'^clients/extra_info/(?P<imei>\w*)$', 'client_extra_info'),
	
    
	(r'^groups/add/$', 'add_group'),
	(r'^groups/edit/$', 'edit_group'),
	(r'^groups/details/(?P<groupname>\w*)$', 'group_details'),
	(r'^groups/delete/$', 'delete_group'),
	(r'^groups/$', 'show_groups'),
    
	(r'^apps/add_app$', 'add_app'),
	(r'^apps/add_release$', 'add_release'),
	(r'^apps/add_version$', 'add_version'),
	(r'^apps/details/', 'app_details'),
	(r'^apps/edit/', 'edit_app'),
	(r'^apps/delete/$', 'delete_app_version'),
	(r'^getAppReleases/(?P<appname>\w*)$', 'getAppReleases'),
	(r'^getReleaseVersions/(?P<appname>\w*)/(?P<release>[a-zA-Z0-9_\-.]*)$', 'getReleaseVersions'),
	(r'^apps/$', 'show_applications'),
    
    (r'^logs/$', 'show_logs'),
	(r'^client_logs_details/(?P<imei>\w*)$', 'client_logs_details'),
	(r'^client_logs/(?P<imei>\w*)$', 'final_client_logs'),
	(r'^group_logs/(?P<groupname>\w*)$', 'final_group_logs'),
	
	(r'^group_logs_details/(?P<group>\w*)$', 'group_logs_details'),
	(r'^showAllClients/$', 'show_all_clients'),
	(r'^showAllGroups/$', 'show_all_groups'),
	
	(r'^global/$', 'show_global_attributes'),
	(r'^global/geturls$', 'get_global_urls'),
	(r'^global/add$', 'set_global_urls'),
	



)

urlpatterns += patterns('',
    (r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login1.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'login1.html','next_page': '/login/'}),
    (r'^$', RedirectView.as_view(url="/clients/")),

)
