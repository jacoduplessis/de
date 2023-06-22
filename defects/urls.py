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
    path("", views.index, name="index"),
    path("apps/", views.apps, name="apps"),
    path("home/", views.home, name="home"),
    path("incidents/", views.incident_list, name="incident_list"),
    path("incidents/create/", views.incident_create, name="incident_create"),
    path("incidents/demo/", views.incident_detail_demo, name="incident_detail_demo"),
    path("incidents/<int:pk>/", views.incident_detail, name="incident_detail"),
    path("incidents/notification/form/", views.incident_notification_form, name="incident_notification_form"),
    path("incidents/notification/approval/", views.incident_notification_approval_send, name="incident_notification_approval_send"),
    path("incidents/close/form/", views.incident_close_form, name="incident_close_form"),
    path("solutions/", views.solution_list, name="solution_list"),
    path("solutions/schedule/", views.solution_schedule, name="solution_schedule"),
    path("solutions/completion/", views.solution_completion, name="solution_completion"),
    path("about/", views.about, name="about"),
    path("anniversaries/", views.anniversary_list, name="anniversary_list"),
    path("compliance/", views.compliance_dashboard, name="compliance_dashboard"),
    path("value/", views.value_dashboard, name="value_dashboard"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
]
