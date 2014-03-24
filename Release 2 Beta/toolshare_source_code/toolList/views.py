from django.template.response import TemplateResponse
# Create your views here.
from django.shortcuts import render
from tool.models import Tool
from tool.views import toolForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

#display toollist page with a list of of owned tool
def toolListAll(request,username):
	print('we made it to All')
	response = index(request,username)
	response.context_data['toolList'] = request.user.get_profile().getToolList()
	response.context_data['numTools'] = len(request.user.get_profile().getToolList())
	response.context_data['typeOfDisplay'] = 'All'	
	return response

#display toollist page with a list of of owned tool
def toolListBorrowed(request,username):
	print('we made it to borrowed')
	response = index(request,username)
	response.context_data['toolList'] = request.user.get_profile().getBorrowedTools()
	response.context_data['numTools'] = len(request.user.get_profile().getBorrowedTools())
	response.context_data['typeOfDisplay'] = 'Borrowed'
	response.context_data['displayExplaination'] = '- Tools you currently are borrowing'
	return response

#display toollist page with a list of of owned tool
def toolListOwned(request,username):
	response = index(request,username)
	response.context_data['toolList'] = request.user.get_profile().getOwnedTools()
	response.context_data['numTools'] = len(request.user.get_profile().getOwnedTools())
	response.context_data['typeOfDisplay'] = 'Owned'	
	response.context_data['displayExplaination'] = '- Tools you permanently own'
	return response
	
#display toollist page with a list of of owned tool
def toolListLent(request,username):
	response = index(request,username)
	response.context_data['toolList'] = request.user.get_profile().getLentTools()
	response.context_data['numTools'] = len(request.user.get_profile().getLentTools())
	response.context_data['typeOfDisplay'] = 'Lent'
	response.context_data['displayExplaination'] = '- Tools you currently are lending'
	return response

#default index render
def index(request,username):
	get_object_or_404(User, username=username)
	template = 'contentToolList.html'
	context = {
		'user' : request.user,
		'form': toolForm(),
	}
	return TemplateResponse(request,template,context)

