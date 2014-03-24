from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.models import User
from userProfile.models import UserProfile
from django.http import HttpResponse, Http404

"""
index page for the Sheds -- very similar tot he shareZone
"""
def index(request, username):
	template = 'contentShed.html'
	context = RequestContext(request, {
		'request' : request,
		'user' : request.user,
		'isCoordinator' :request.user.get_profile().isCoordinator(),
		'shedCoordinators' : request.user.get_profile().getShedCoordinators(),
		}
	)
	return render(request,template,context)

#toggles the current status of the user as shedCorrdinator
def toggleCoordinator(request,username):
	user = request.user.get_profile()
	template = 'toggleCoordinator.html'
	toolList = user.getAddToShedToolList()
	if user.isCoordinator():
		context = RequestContext(request,{
			'removeCoordinator' : True
			})
		user.removeCoordinatorStatus()
	else:
		return addTools(request,username,username)

	return render(request,template,context)

#adds tools from a form to the shed
def addTools(request,username,coordinator):
	user = request.user.get_profile()
	template = 'addRemoveToolsToShed.html'
	toolList = user.getAddToShedToolList()
	
	if request.method == 'POST':
		if len(request.POST) < 2:
			context = RequestContext(request,{
				'toolList' : toolList,	
				'coordinator': coordinator,
				'noToolsSelected' : True
			})
		else:
			coordinator = User.objects.get(username=coordinator).get_profile()
			coordinator.addToolsToShed(request.POST)
			context = RequestContext(request,{
				'toolAddSuccess' : True,
				'coordinator': coordinator
			})	
	else:
		if toolList.count() < 1:
			return HttpResponse("You must currently own at least one tool to continue.")
		else:
			context = RequestContext(request,{
				'toolList' : toolList,	
				'coordinator': coordinator
			})
	return render(request,template,context)

#remove tools from a shed
def removeTools(request,username,coordinator):
	user = request.user.get_profile()
	template = 'addRemoveToolsToShed.html'
	coordinator = User.objects.get(username=coordinator).get_profile()
	toolList = user.getToolsInShed(coordinator.user)
	if request.method == 'POST':
		if len(request.POST) < 2:
			context = RequestContext(request,{
				'toolList' : toolList,	
				'coordinator': coordinator.user.username,
				'noToolsSelected' : True
			})
		else:
			coordinator.removeToolsFromShed(request.POST)
			context = RequestContext(request,{
				'toolRemoveSuccess' : True,
				'coordinator': coordinator.user.username,
				'remove': True
			})
	else:

		if toolList.count() < 1:
			return HttpResponse("You have no tools to Remove")
		context = RequestContext(request,{
			'toolList' : toolList,
			'coordinator': coordinator.user.username,
			'remove': True
		})


	return render(request,template,context)

#view the people/tools in your shed
def viewShed(request,username):
	template = 'yourShed.html'
	context = RequestContext(request, {
		'request' : request,
		'user' : request.user,
		'isCoordinator' :request.user.get_profile().isCoordinator(),
		'shedCoordinators' : {request.user.get_profile()}
		}
	)
	return render(request,template,context)
	