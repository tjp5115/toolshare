from django.conf.urls import patterns, include, url
from shareZone import views 


urlpatterns = patterns('',
	url(r'^',views.index, name='shareZone'),
)