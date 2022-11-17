"""defects URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('apps/', views.apps, name='apps'),
    path('home/', views.home, name='home'),
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/create/', views.incident_create, name='incident_create'),
    path('incidents/detail/', views.incident_detail, name='incident_detail'),
    path('solutions/', views.solution_list, name='solution_list'),
    path('about/', views.about, name='about'),
    path('anniversaries/', views.anniversary_list, name='anniversary_list'),
    path('compliance/', views.compliance_dashboard, name='compliance_dashboard'),
    path('value/', views.value_dashboard, name='value_dashboard'),
    path('login/', views.login, name='login'),
    path('admin/', admin.site.urls),
]

""""

"""
