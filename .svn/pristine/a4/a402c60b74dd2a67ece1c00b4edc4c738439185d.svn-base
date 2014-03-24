# Create your views here.
from django.shortcuts import render
from tool.models import Tool


def index(request,username):
	template = 'contentToolList.html'
	context = {
		'user' : request.user,
		'toolList' : Tool.objects.all().filter(currentOwnerID = request.user.id),
		'numTools' : len(Tool.objects.all().filter(currentOwnerID = request.user.id))
	}
	return render(request,template,context)
