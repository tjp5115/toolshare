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
    template = 'deleteFailOwn.html'
    fail = models.Tool.deleteTool(request,toolID)
    print (fail)
    if fail == 1:
        #return redirect('/'+username+'/tools/')
        template = 'deleteSuccess.html'
        return render(request,template)
    elif fail == 2:
        template = 'deleteFailRes.html'
        return render(request,template)
    else:
        return render(request,template)
"""
update Tool with post request

quantity will be a problem  -- need to make > 0 
"""
def updateTool(request,username,toolID):
    template = 'updateTool.html'
    tool = models.Tool.objects.get(pk=toolID)
    if (tool.ownerID != tool.currentOwnerID):
        template = 'dontEditTool.html'
        return render (request,template)
    #has the sent been sent previously 
    if request.method == 'POST':
        form =updateToolForm(request.POST,my_arg=tool)
        #validate form
        if form.is_valid():
            #tool is valid -- enter into database
            models.Tool.update(request,toolID)
            return render(request,template,{
                'toolUpdateSuccess': True,
                'user':request.user,
                'toolID' : toolID
                })
        
    else:
        form = updateToolForm(my_arg=tool)
    return render(request,template,{
            'form':form,    
            'user':request.user,
            'toolID' : toolID
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
    css                 = forms.TextInput(attrs={'class':'text'})
    name                = forms.CharField(max_length = 200,widget=css)
    description         = forms.CharField(max_length = 300,widget=css)
    #picture            = forms.CharField(max_length = 100) #add later -- too hard
    quantityMax         = forms.IntegerField(widget=css)
    specialInstructions = forms.CharField(max_length = 300,required=False,widget=css)
    availability        = forms.BooleanField(required=False, initial=False)

# Form used for updating a tool
class updateToolForm(forms.Form):
    def __init__(self, *args, **kwargs):
        tool = kwargs.pop('my_arg')
        super(updateToolForm, self).__init__(*args, **kwargs)

        self.fields['name']                 = forms.CharField(max_length = 200,widget=forms.TextInput(attrs={'class':'text','value':tool.name}))
        self.fields['description']          = forms.CharField(max_length = 300,widget=forms.TextInput(attrs={'class':'text','value':tool.description}))
        self.fields['pickupArrangements']    = forms.CharField(max_length = 300, widget=forms.TextInput(attrs={'class':'text','value':tool.pickupArrangements}))
        self.fields['quantityMax']          = forms.IntegerField(widget=forms.TextInput(attrs={'class':'text','value':tool.quantityMax}))
        self.fields['specialInstructions']  = forms.CharField(max_length = 300,required=False,widget=forms.TextInput(attrs={'class':'text','value':tool.specialInstructions}))
        self.fields['availability']         = forms.BooleanField(required=False, initial=tool.availability)

        