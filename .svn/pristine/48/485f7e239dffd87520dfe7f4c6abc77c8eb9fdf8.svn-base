from django.conf.urls import patterns, url

from userProfile import views

urlpatterns = patterns('',
    # ex: /user/
    url(r'^$', views.index, name='index'),
    # ex: /user/5/
    #url(r'^(?P<question_id>\d+)/$', views.detail, name='detail'),
	url(r'^(?P<username>\w+)$',	views.homepage_user,name='homepage_user'),
	#url(r'^usr/(?P<username>\w+)/tools/', include('tool.urls')),
	url(r'^s/login$', views.login_user, name='user_login'),
	url(r'^s/logout$', views.logout_user,name='user_logout'),
	
	url(r'^s/update$',views.updateUser,name='updateUser'),
	)
	
