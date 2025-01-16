from data.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, RegisterForm

from django.http import HttpResponse, JsonResponse

def sign_in(request):
	if request.method == 'GET':
		if request.user.is_authenticated:
			return render(request, 'home/html')
		form = LoginForm()
		return render(request, 'users/login.html', {'form':form})
	
	elif request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(request,username=username,password=password)
			if user:
				login(request, user)
				messages.success(request,f'Hi {username.title()}, welcome back!')
				return redirect('game_server') #this should probably be home, also SPA?
	
	messages.error(request,f'Invalid username or password')
	return render(request, 'users/login.html',{'form': form})

def sign_out(request):
	logout(request)
	messages.success(request,f'You have been logged out')
	return redirect('sign_in')

def register(request):
	if request.method == 'GET': 
		form = RegisterForm()
		return render(request, 'users/register.html', {'form': form})
	
	if request.method == 'POST': 
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.username = user.username.lower()
			# TODO: store other info, create JWT token and send it insted of using login method
			# UserManager.create_user(UserManager, form.)
			user.save()
			messages.success(request, 'you have signed up sucesfully.')
			login(request, user)
			return redirect('post')
		else:
			return render(request, 'users/register.html', {'form: form'})

def home(request):
	return render(request, 'base.html')
