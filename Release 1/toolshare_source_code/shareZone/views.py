from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.models import User


"""
TODO::
	make it so if > x amount of people in the sharezone are index only
	a specific amount are displayed with the ability to hit the next button
	to the rest

"""
def index(request, username):
	template = 'contentShareZone.html'
	u = request.user

	# Do we have a shareZone?
	if len(u.groups.all()) > 0:
		context = RequestContext(request, {
		'request' : request,
		'user' : u,
		'shareZone' : User.objects.all().filter(groups__name=u.groups.all()[0])
			}
		
		)
		#print ("hi "+str(User.objects.all().filter(groups__name=u.groups.all()[0])))
	else:
		context = RequestContext(request, {
		'request' : request,
		'user' : u,
		'shareZone' : 'No ShareZone for you! Nice try, admin.'
			}
		)
	return render(request,template,context)
