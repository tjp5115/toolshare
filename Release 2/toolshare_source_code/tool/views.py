from django.http import HttpResponse, HttpRequest
from django.template import RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django import forms
from tool import models
from django.contrib.auth import authenticate, login,logout
from django.forms.util import ErrorList
from django.views.generic.edit import UpdateView

import userProfile

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
            #deal with invalid form
            pass
    else:
        form = toolForm()
    return render(request,template,{
            'form':form,    
            'user':request.user,
        })
def deleteTool(request,username,toolID):
    #Form to delete tool is need that will ask user the quantity to delete.
    fail = models.Tool.deleteTool(request,toolID)
    #print (fail)
    if fail == 1:
        return HttpResponse("Deleted tool")
    elif fail == 2:
        return HttpResponse("Tool has future reservations and cannot be deleted") 
    elif fail == 4:
        return HttpResponse("You Can not delete Tool if it is the last tool in the shed.")
    else:
        return HttpResponse("Tool is not with it's current user and cannot be deleted")
        
"""
update Tool with post request

quantity will be a problem  -- need to make > 0 
"""
def updateTool(request,username,toolID):
    template = 'updateTool.html'
    tool = models.Tool.objects.get(pk=toolID)
    if (tool.ownerID != tool.currentOwnerID):
        return HttpResponse("You can't modify somebody else's tool.")
    #has the sent been sent previously 
    if request.method == 'POST':
        form =toolForm(request.POST)
        #validate form
        if form.is_valid():
            #tool is valid -- enter into database
            models.Tool.update(request,toolID)
            return render(request,template,{
                'toolUpdateSuccess': True,
                'user':username,
                'toolID' : toolID
                })
        
    else:
        form = toolForm(initial={
            'name':tool.name,            
            'description':tool.description,
            })
    return render(request,template,{
            'form':form,    
            'user':username,
            'tool' : tool,
            'toolID': toolID,
        })



"""
display a tool
"""
def displayTool(request, username, toolID):
    tool = get_object_or_404(models.Tool, pk=toolID)
    context = {
        'tool':tool
    }
    return render(request, 'contentTool.html', context)

# Form used for adding a tool to the database
class toolForm(forms.Form):
    css = {
        'type':"text",
        'name':"name",
        'autocomplete':"off",
        'class':"txtinput"
    }

    css['placeholder'] = "Tool name"
    css['tabindex'] = 1
    cssName = forms.TextInput(attrs=css)
    css['tabindex'] = 2
    css['placeholder'] = "Tool description"
    cssDesc = forms.Textarea(attrs=css)

    name                = forms.CharField(max_length = 200,widget=cssName)
    description         = forms.CharField(max_length = 300,widget=cssDesc)

        