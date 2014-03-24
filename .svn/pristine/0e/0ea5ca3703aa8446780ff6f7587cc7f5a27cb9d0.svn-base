from django.conf.urls import patterns,  url
from notifications import views

urlpatterns = patterns('',
	url(r'^(?P<toolID>\d+)$',views.borrowTool,name='borrowTool'),
	url(r'^(?P<requestID>\d+)/accept',views.respondRequest,{'accept':True},name="respondRequestAccept"),
	url(r'^(?P<requestID>\d+)/request/deny',views.respondRequest,{'accept':False},name="respondRequestDeny"),
	url(r'^(?P<requestID>\d+)/delete',views.deleteResponse,name="deleteResponse"),
	url(r'^(?P<requestID>\d+)/return$',views.respondAwaitingReturnRequestAccept,name="respondAwaitingReturnRequestAccept"),
	url(r'^(?P<requestID>\d+)/return/confirm',views.respondConfirmReturn,name="respondConfirmReturn"),
	url(r'^(?P<requestID>\d+)/return/deny',views.respondDenyReturn,name="respondDenyReturn"),
	url(r'^(?P<requestID>\d+)/(?P<toolID>\d+)',views.displayNotification,name="displayNotification"),
	
)