from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.models import User
from shareZone import models


"""
TODO::
	make it so if > x amount of people in the sharezone are index only
	a specific amount are displayed with the ability to hit the next button
	to the rest

"""
def index(request, username):
	template = 'contentShareZone.html'

	context = RequestContext(request, {
		'shareZoneUser' : request.user.get_profile().getShareZone(),
		'zipcode' : request.user.groups.all()[0],
		'shareZone' : models.ShareZone.objects.get(zipCode=request.user.groups.all()[0])
		}
	)
	return render(request,template,context)
