from django.conf.urls import patterns, include, url
from tool import views 


urlpatterns = patterns('',
	#url(r'^','tool.views.addTool',name='index_tool'),
	url(r'^','toolList.views.index',name='indexTool'),
)
