from django.conf.urls import patterns, include, url
from tool import views 


urlpatterns = patterns('',
	#url(r'^','tool.views.addTool',name='index_tool'),
	url(r'^add/','tool.views.addTool',name='addTool'),
	url(r'^update/(?P<toolId>\d+)/$',views.updateTool,name='updateTool'),
)
