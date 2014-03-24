from django.http import HttpResponse, HttpRequest
from django.template import RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django import forms
from tool import models
from django.contrib.auth import authenticate, login,logout
from django.forms.util import ErrorList
from django.contrib import messages
from django.views.generic.edit import UpdateView
#add a tool to a user
def addTool(request, username):
	template = 'addTool.html'
	
	#has the sent been sent previously 
	if request.method == 'POST':
		form = toolForm(request.POST)
		#validate form
		if form.is_valid():
			#tool is valid -- enter into database
			models.Tool.insert(request)
			return render(request,template,{
				'toolAddSuccess': True,
				'user':request.user,
				})
		
	else:
		form = toolForm()
	us = User.objects.all().filter(id=request.user.id)[0].username
	print(us)
	messages.add_message(request,messages.INFO,'You tried to add a tool, tool.',extra_tags='tool')
	return render(request,template,{
			'form':form,	
			'user':request.user,
		})

"""
update Tool with post request

quantity will be a problem  -- need to make > 0 
"""
def	updateTool(request,username,toolId):
	template = 'updateTool.html'
	tool = models.Tool.objects.get(pk=toolId)	
	#has the sent been sent previously 
	if request.method == 'POST':
		form =updateToolForm(request.POST,my_arg=tool)
		#validate form
		if form.is_valid():
			#tool is valid -- enter into database
			models.Tool.update(request,toolId)
			return render(request,template,{
				'toolUpdateSuccess': True,
				'user':request.user,
				})
		
	else:
		form = updateToolForm(my_arg=tool)
	us = User.objects.all().filter(id=request.user.id)[0].username
	print(us)
	messages.add_message(request,messages.INFO,'You tried to add a tool, tool.',extra_tags='tool')
	return render(request,template,{
			'form':form,	
			'user':request.user,
		})
"""
form for the Add tool
"""
class updateToolForm(forms.Form):
    def __init__(self, *args, **kwargs):
        tool = kwargs.pop('my_arg')
        super(updateToolForm, self).__init__(*args, **kwargs)

        self.fields['name']= forms.CharField(max_length = 200,widget=forms.TextInput(attrs={'class':'text','value':tool.name}))
        self.fields['description'] = forms.CharField(max_length = 300,widget=forms.TextInput(attrs={'class':'text','value':tool.description}))
        #picture = forms.CharField(max_length = 100) #add later -- too hard
        self.fields['quantityMax']= forms.IntegerField(widget=forms.TextInput(attrs={'class':'text','value':tool.quantityMax}))
        self.fields['specialInstructions'] = forms.CharField(max_length = 300,required=False,widget=forms.TextInput(attrs={'class':'text','value':tool.specialInstructions}))

class toolForm(forms.Form):
    css = forms.TextInput(attrs={'class':'text'})
    name= forms.CharField(max_length = 200,widget=css)
    description = forms.CharField(max_length = 300,widget=css)
    #picture = forms.CharField(max_length = 100) #add later -- too hard
    quantityMax= forms.IntegerField(widget=css)
    specialInstructions = forms.CharField(max_length = 300,required=False,widget=css)



