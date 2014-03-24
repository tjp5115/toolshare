from django.conf.urls import patterns, include, url
from sheds	 import views 


urlpatterns = patterns('',
	url(r'^setcord/$',views.toggleCoordinator ,name='toggleCoordinator'),
	url(r'^addTools/(?P<coordinator>\w+)$',views.addTools,name='addToolsToShed'),
	url(r'^removeTools/(?P<coordinator>\w+)$',views.removeTools,name="removeToolsToShed"),
	url(r'^$',views.index, name='sheds'),
	url(r'^yours/$',views.viewShed, name='viewShed'),
)