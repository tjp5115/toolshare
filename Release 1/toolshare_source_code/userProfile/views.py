from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django import forms
from userProfile import models
from django.contrib.auth import authenticate, login,logout
from django.forms.util import ErrorList
from django.contrib import messages
"""
Process the index page request
if the user is logged in, display their home page
else diplay register page
"""
def index(request):
		
	#check if user logged in
	#logout(request) #temp line for dbug  -- lets have no one every log in
	if  request.user.is_authenticated():
		#print("lolreg")
		#this is temp junk to see who is logged in
		#from django.contrib.sessions.models import Session
		#session = Session.objects.get(session_key = request.session.session_key)
		#uid = session.get_decoded().get('_auth_user_id')
		#show home page
		return homepage_user(request,request.user)

	#check to see if the user has submited a form from a previous register
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			#process form 
			#1) insert into DB 
			if not models.UserProfile.insert(request.POST):
				errors = form._errors.setdefault("username", ErrorList())
				errors.append("Name already taken.")
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
    template = 'contentUser.html'

    context = RequestContext(request, {
    'request' : request,
	'user' : user 
		})
    print("did you render this homepage_user")
	#messages.add_message(request,messages.INFO,'Welcome '+username.last_login.now().strftime("%Y-%m-%d %H:%M:%S")+'was your last login')
	#messages.add_message(request,messages.INFO,'Welcome '+username+' was your last login')
    return render(request,template,context)
	
"""
default home page
register user / login 
"""
def homepage_register(request,form):
	##models.UserProfile.insert(request.REQUEST); #i dont know what you are
	template = 'contentRegister.html'
	return render(request,template, { 
			'form': form, 
		})
"""
log user in and redirect to his/her page
"""
def login_user(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			messages.add_message(request,messages.INFO,'Logged in at ' +user.last_login.now().strftime("%Y-%m-%d %H:%M:%S"),extra_tags='extra')
			return homepage_user(request,request.user)
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
	#messages.add_message(request,messages.INFO,'You last logged in at '+request.user.last_login.now().strftime("%Y-%m-%d %H:%M:%S"))
	return redirect('userProfile.views.index')

"""
edit user's preferences
"""	
def edit_user(request,username):
	template = 'contentEditUser.html'
	context={
					'user':request.user
					
					}
	return render(request,template,context)

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
	zipCode = forms.IntegerField(widget=css)
	email = forms.EmailField(max_length=100,widget = css)
	password = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'class':'text','type':'password'}))
	username= forms.CharField(max_length=100,widget = css)


