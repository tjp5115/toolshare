from django.conf.urls import patterns, include, url
from tool import views 


urlpatterns = patterns('',
	url(r'^$','toolList.views.toolListAll',name='toolListAll'),
	url(r'^borrowed','toolList.views.toolListBorrowed',name='toolListBorrowed'),
	url(r'^owned','toolList.views.toolListOwned',name='toolListOwned'),
	url(r'^lent','toolList.views.toolListLent',name='toolListLent'),
)
