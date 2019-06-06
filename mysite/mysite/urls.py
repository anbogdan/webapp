"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from pages.views import register_view, dashboard_view, login_view, logout_view, add_application_view, allocate_app_view
from my_apis.views import update_flavors, api_allocate_app
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('register/', register_view, name="register"),
    path('', login_view, name="login"),
    path('dashboard/', dashboard_view, name="dashboard"),
    path('logout/', logout_view, name="logout"),
    path('update/', update_flavors, name="flavors"),
    path('addapplication/', add_application_view, name="addapp"),
    path('api/allocateapp/', api_allocate_app, name="api_allocateapp"),
    path('allocateapp/', allocate_app_view, name="allocateapp"),
]

urlpatterns += staticfiles_urlpatterns()