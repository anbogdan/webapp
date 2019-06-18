from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import RegisterForm, LoginForm, AddAppForm, AllocateAppForm, AddSshKey
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from my_models.models import Application, SshKey


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

    applications = Application.objects.filter(user=request.user)
    return render(request, "dashboard.html", {'applications':applications})

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

def add_application_view(request, *args, **kwargs):
    template = 'addapplication.html'
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddAppForm(request.POST)
            if form.is_valid():
                if Application.objects.filter(name=form.cleaned_data['name'].capitalize(), user=request.user).exists():
                    return render(request, template, {
                        'form': form,
                        'error_message': 'Application already exists.'
                    })
                else:
                    entry = Application(
                        name=form.cleaned_data['name'].capitalize(),
                        flv=form.cleaned_data['flv'],
                        user=request.user,
                        allocated=False,
                        ip='none',
                        repo=form.cleaned_data['repo'],
                        status='no status'
                    )
                    entry.save()
                    return redirect('dashboard')
        else:
            form = AddAppForm()
        return render(request, template, {'form': form})

def allocate_app_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AllocateAppForm(request.POST)
            if form.is_valid():
                entry = Application.objects.get(name=form.cleaned_data['app_name'].capitalize(), user=request.user)
                entry.status = 'pending'
                entry.save()
                return redirect('dashboard')
    return HttpResponse('DENIED')

def add_sshkey_view(request, *args, **kwargs):
    template = 'addsshkey.html'
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddSshKey(request.POST)
            if form.is_valid():
                if SshKey.objects.filter(user=request.user).exists():
                    entry = SshKey.objects.get(user=request.user)
                    entry.sshkey = form.cleaned_data['sshkey']
                    entry.save()
                    return redirect('dasboard')
                entry = SshKey(
                    sshkey=form.cleaned_data['sshkey'],
                    user=request.user
                )
                entry.save()
                return redirect('dashboard')
        else:
            form = AddSshKey()
        return render(request, template, {'form': form})