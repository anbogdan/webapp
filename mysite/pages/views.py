from django.shortcuts import render, redirect
from .models import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

# Create your views here.

def register_view(request, *args, **kwargs):
    template = 'register.html'

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                return render(request, template, {
                    'form': form,
                    'error_message': 'Username already exists.'
                })
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                return render(request, template, {
                    'form': form,
                    'error_message': 'Email already exists.'
                })
            elif form.cleaned_data['password'] != form.cleaned_data['password_repeat']:
                return render(request, template, {
                    'form': form,
                    'error_message': 'Passwords do not match.'
                })
            elif form.cleaned_data['email'] != form.cleaned_data['email_repeat']:
                return render(request, template, {
                    'form': form,
                    'error_message': 'Emails do not match.'
                })
            else:
                user = User.objects.create_user(
                    form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['password']
                )
                user.save()

                login(request, user)
                return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, template, {'form': form})

def dashboard_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, "dashboard.html", {})

def login_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('dashboard')
    template = 'login.html'

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, template, {
                    'form': form,
                    'error_message': 'Incorrect username and / or password.'
                })
    else:
        # No post data availabe, let's just show the page to the user.
        form = LoginForm()
    return render(request, template, {'form': form})


def logout_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')