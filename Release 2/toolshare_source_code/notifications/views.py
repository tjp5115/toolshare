from notifications import models
from userProfile import models
from tool.models import Tool
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

def displayNotification(request,username, toolID):
    notification = get_object_or_404(models.Tool, pk=toolID)
    context = {
        'notification' : notification
    }
    return render(request, 'contentNotification.html', context)

"""
creates a notification in the database if sucessful
steps for validation:
1) looks for a post from the request 
	no post: returns empty borrow tool form
2) if there is a post it checks if the borrow tool form is valid 
	not valid: returns the form with the invalid data sent marked as invalid
3) creates a notification in the database and tells the user it was sucessful
"""
#print(request.POST['reason'])       # This is how we access the data in the form
#print(request.POST['timePeriod'])
#print(request.POST['quantity'])
def borrowTool(request, username, toolID):
    #return HttpResponse("best page na")
    template = 'borrowTool.html'
    tool = Tool.objects.get(pk=toolID)   
    #has the sent been sent previously 
    if request.method == 'POST':
        form = borrowToolForm(request.POST)
        #validate form
        if form.is_valid():
            #tool is valid -- enter into database
            print("receiver  id: "+str(tool.ownerID))
            print("requester id: "+str(request.user.id))

            if tool.isInShed():
                print("tool is in shed")
                receiverID = tool.getCoordinator().pk

            else:
                receiverID = tool.ownerID

            if models.Notification.insert(request,toolID,receiverID):
                return render(request,template,{
                    'toolBorrowSuccess': True,
                    'user': request.user,
                    'toolOwner': tool.getOwner()
                    })
            else:
                # The date range was invalid
                print("date was conflicted yo")
                print("this means that the user selected a date range that completely covers a reserved period")
                print("e.g. reserved the second through the fifth, and you requested the first through the sixth")
                print("or they just didn't use datepicker")
                print("we should validate input format beforehand if they dont use datepicker")

    else:
        form = borrowToolForm()
    return render(request,template,{
            'form':form,    
            'user':request.user,
            'tool':tool,
    })

"""
evaluates the response to the request
if the user accepts the tool to be borrowed:   
        notification is marked as reserved
if the user denys the request:
        tool is marked as archived
"""
def respondRequest(request,username,requestID,accept):
    template = 'respondRequest.html'
    response = models.Notification.objects.get(pk=requestID)
    context = {'accept':accept,'responseID':requestID,'username':username}
    # Set the response's status to accepted or rejected based on accept
    if accept:
        # Here we should check if accepting will reject other requests, and
        # warn the user accordingly
        response.setAccepted()
    else:
        if request.method == 'POST':
            form = denyRequestForm(request.POST)
            #validate form
            if form.is_valid():
                
                context.update({'userRejectRequestValid': True})
                response.setRejected(request.POST['denyReason'])
                return render(request,template,context)
        else:
            form = denyRequestForm()
        context['form'] = form
    return render(request,template,context)

"""
confirms the tool has been returned
the user comfirms the tool returned the tool:   
        notification is marked as awaitingConfirmation

"""
def respondConfirmReturn(request,username,requestID):
    template = 'respondRequest.html'
    response = models.Notification.objects.get(pk=requestID)
    response.setArchived()
    return render(request,template,{
        'toolReturnConfimation': True
    })
"""
confirms the tool has been returned
the user comfirms the tool returned the tool:   
        notification is marked as awaitingConfirmation

"""
def respondDenyReturn(request,username,requestID):
    template = 'respondRequest.html'
    response = models.Notification.objects.get(pk=requestID)
    response.setAwaitingReturn()
    return render(request,template,{
       'toolDenyReturn': True
    })
"""
evaluates the response to the request
the user comfirmed to have returned the tool:   
        notification is marked as awaitingConfirmation

"""
def respondAwaitingReturnRequestAccept(request,username,requestID):
    template = 'respondRequest.html'
    response = models.Notification.objects.get(pk=requestID)
    response.setAwaitingConfirmation()
    return render(request,template,{
        'awatingConfimation': True
    })
"""
removes the response from the user's notifications
makes the status of the tool as 'archived' for statistical purposes
"""
def deleteResponse(request,username,requestID):
    template = 'deleteResponse.html'
    response = models.Notification.objects.get(pk=requestID)
    # If the response was accepted, set it to the waiting state
    # Otherwise, archive it
    print(response.status)
    if response.status == 'accepted':
        response.setWaiting()
    else:
        response.setArchived()
    return render(request,template)

"""
a form class that extends the django form class for easy validation of forms
"""
class denyRequestForm(forms.Form):
    css = {
        'type':"text",
        'name':"name",
        'autocomplete':"off",
        'class':"txtinput"
    }
    
    css['placeholder'] = "Reason for denying"
    cssReason= forms.Textarea(attrs=css)

    denyReason = forms.CharField(widget=cssReason)

class borrowToolForm(forms.Form):
    css = {
        'type':"text",
        'name':"name",
        'autocomplete':"off",
        'class':"txtinput"
    }
    
    css['placeholder'] = "Reason for borrowing"
    cssReason= forms.Textarea(attrs=css)

    css['placeholder'] = "Start time"
    css['class'] = "timeStart txtinput"
    cssTimeStart = forms.TextInput(attrs=css) 

    css['placeholder'] = "End time"
    css['class'] = "timeEnd txtinput"
    cssTimeEnd= forms.TextInput(attrs=css) 

    reason          = forms.CharField(max_length = 500,widget=cssReason)
    timeStart       = forms.DateField(widget=cssTimeStart)
    timeEnd         = forms.DateField(widget=cssTimeEnd)
