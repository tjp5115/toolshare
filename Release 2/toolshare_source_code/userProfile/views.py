from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django import forms
from userProfile.models import UserProfile
from django.contrib.auth import authenticate, login,logout
from django.forms.util import ErrorList
from django.contrib import messages
from userProfile import models


"""
Process the index page request
if the user is logged in, display their home page
else diplay register page
"""
def index(request):
    #check if user logged in
    #logout(request) #temp line for dbug  -- lets have no one every log in
    if  request.user.is_authenticated():
        return homepage_user(request,request.user)

    #check to see if the user has submited a form from a previous register
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            #process form 
            #1) insert into DB 
            if not UserProfile.insert(request.POST):
                errors = form._errors.setdefault("username", ErrorList())
                errors.append("Username already taken.")
                return homepage_register(request,form)      
            #2)log user in 
            user = authenticate(username=request.POST['username'],password=request.POST['password'])
            login(request,user)
            #3) show new index page
            return homepage_user(request,request.user)
    else:
        form = RegisterForm()
    
    return homepage_register(request,form)
    

"""
logged in index page 
display tools and other fun stuff --
main page of the site
"""
def homepage_user(request,username ):
    user = get_object_or_404(User,username=username) 
    usernameID = User.objects.get(username=username).id;
    if(str(username) != str(request.user)):
        template = 'contentUserGuest.html'
    else:
        template = 'contentUser.html'
    # Check if any notifications change state today
    request.user.get_profile().checkForNotificationChanges()

    context = RequestContext(request, {
        'request' : request,
        'user' : user,     
        'username' : user,     
        'toolList' : models.Tool.objects.all().filter(ownerID= usernameID),
        'responses' : User.objects.get(username=username).get_profile().getResponses(),
        'pendingRequests' : User.objects.get(username=username).get_profile().getPendingRequests(),
        'receivedRequests' : User.objects.get(username=username).get_profile().getReceivedRequests(),
        'activeRequests' : User.objects.get(username=username).get_profile().getActiveRequests(),
        'getWaitingRequests' : User.objects.get(username=username).get_profile().getWaitingRequests(),
        'getAwaitingReturnRequests' : User.objects.get(username=username).get_profile().getAwaitingReturnRequests(),
        'getAwaitingConfirmationRequests' : User.objects.get(username=username).get_profile().getAwaitingConfirmationRequests(),

    })
    return render(request,template,context)
    
"""
default home page
register user / login 
"""
def homepage_register(request,form):
    template = 'contentRegister.html'
    return render(request,template, { 
            'form': form, 
        })
"""
log user in and redirect to his/her page
"""
def login_user(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        if user.is_active:
            login(request, user)

            #return homepage_user(request,request.user)
            return redirect('/')
        else:
            # Return a 'disabled account' error message
            pass
    else:
        template = 'contentRegister.html'
        return render(request,template,{
            'loginError': True,
            'form':RegisterForm()
            
            })
        
    
"""
logout and return to the registration page
"""
def logout_user(request):
    logout(request)
    return redirect('userProfile.views.index')

"""
update user's profile
"""
def updateUser(request, username):
    template = 'updateUser.html'
    user = UserProfile.objects.get(user=request.user)  
    #has the sent been sent previously 
    if request.method == 'POST':
        form = updateUserForm(request.POST)
        #validate form
        if form.is_valid():
            print("user is valid")
            #user is valid -- enter into database
            models.UserProfile.update(user, request)
            return render(request,template,{
                'userUpdateSuccess': True,
                'user':request.user,
                })

        else:
            print("what happend")
        
    else:
        form = updateUserForm({
            'nameFirst': user.nameFirst,
            'nameLast': user.nameLast,
            'home_address': user.home_address,
            'email': user.email,
            'shareZone': user.user.groups.all()[0]
    })
    #user = User.objects.all().filter(id=request.user.id)[0].username
    return render(request,template,{
            'form':form,    
            'user':request.user,
        })
#change password
def changePass(request, username):
    template = 'changePass.html'
    user = UserProfile.objects.get(user=request.user)  
    #has the sent been sent previously 
    if request.method == 'POST':
        form = changePassForm(request.POST)
        #form = PasswordChangeForm(request.POST)
        #validate form
        
        if form.is_valid():
            print("user is valid")
            #user is valid -- enter into database
            models.UserProfile.changeP(user, request)
            #user.set_password(form.cleaned_data['newPass'])
            #print('MADEIT')
            return render(request,template,{
                'changePassSuccess': True,
                })

        else:
            print("what happend")
        
    else:
        #form = PasswordChangeForm({
        form = changePassForm({
            #'newPass': '',
            #'nameLast': user.nameLast,
            #'home_address': user.home_address,
            #'email': user.email,
            #'shareZone': user.user.groups.all()[0]
        })
    #user = User.objects.all().filter(id=request.user.id)[0].username
    return render(request,template,{
            'form':form,    
            'user':request.user,
       })
#change password form
class changePassForm(forms.Form):
    css = {
    'class':"txtinput",
    'type':'password',
    
    }
    
    css['placeholder'] = "New Password"
    newPass  = forms.CharField(max_length = 200,widget=forms.TextInput(attrs=css))
    
    css['placeholder'] = "Verify Password"
    css['type'] = 'password'
    verifyNewPass = forms.CharField(max_length = 200,widget=forms.TextInput(attrs=css))

    def clean_verifyNewPass(self):
        
        password = self.cleaned_data['newPass']
        verify_password = self.cleaned_data['verifyNewPass']
        
        if password != verify_password:
            raise forms.ValidationError("Your passwords do not match")
            
        return verify_password
# Form used for updating a user
class updateUserForm(forms.Form):
    css = {
    'type':"text",
    'name':"name",
    'autocomplete':"off",
    'class':"txtinput"
    }
    css['placeholder'] = "First Name"
    nameFirst  = forms.CharField(max_length = 200,widget=forms.TextInput(attrs=css))

    css['placeholder'] = "Last Name"
    nameLast = forms.CharField(max_length = 200,widget=forms.TextInput(attrs=css))

    css['placeholder'] = "Home Address"
    home_address = forms.CharField(max_length = 200,widget=forms.TextInput(attrs=css) )

    css['placeholder'] = "Email"
    email = forms.EmailField(max_length = 200,widget=forms.TextInput(attrs=css))

    css['placeholder'] = "Zip Code"
    shareZone  = forms.IntegerField(min_value=0, max_value=99999, error_messages={'max_value': 'Please enter a valid 5 digit zip code.','min_value': 'Please enter a valid 5 digit zip code.'},widget=forms.TextInput(attrs=css) )
    
"""
loginform
"""
class LoginForm(forms.Form):
    username= forms.CharField(max_length=100)
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
 
"""
registration form
"""
class RegisterForm(forms.Form):
    
    css = forms.TextInput(attrs={'class':'text'})
    #url = forms.CharField(max_length=100)
    nameFirst = forms.CharField(max_length=100,widget=css)
    nameLast = forms.CharField(max_length=100,widget=css) 
    home_address = forms.CharField(max_length=100,widget=css)
    zipCode = forms.IntegerField(min_value=0, max_value=99999, error_messages={'max_value': 'Please enter a valid 5 digit zip code.','min_value': 'Please enter a valid 5 digit zip code.'}, widget=css)
    email = forms.EmailField(max_length=100,widget = css)
    password = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'class':'text','type':'password'}))
    verify_password = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'class':'text','type':'password'}))
    username= forms.CharField(max_length=100,widget = css)
    
    def clean_verify_password(self):
        
        password = self.cleaned_data.get('password')
        verify_password = self.cleaned_data.get('verify_password')
        
        if password != verify_password:
            raise forms.ValidationError("Your passwords do not match")
            
        return verify_password


