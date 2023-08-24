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
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("apps/", views.apps, name="apps"),
    path("home/", views.home, name="home"),
    path("incidents/", views.incident_list, name="incident_list"),
    path("incidents/create/", views.incident_create, name="incident_create"),
    path("incidents/demo/", views.incident_detail_demo, name="incident_detail_demo"),
    path("incidents/<int:pk>/", views.incident_detail, name="incident_detail"),
    path("incidents/<int:pk>/edit/", views.incident_update, name="incident_update"),
    path("incidents/<int:pk>/images/", views.incident_images, name="incident_images"),
    path("incidents/<int:pk>/notification/", views.incident_notification, name="incident_notification"),
    path("incidents/<int:pk>/notification/approval/request/", views.incident_notification_approval_request, name="incident_notification_publish"),
    path("incidents/<int:pk>/notification/pdf/", views.incident_notification_pdf, name="incident_notification_pdf"),
    path("incidents/<int:pk>/history/", views.incident_history, name="incident_history"),
    path("incidents/notification/approval/", views.incident_notification_approval_send, name="incident_notification_approval_send"),
    path("incidents/<int:pk>/solutions/create/", views.incident_solution_create, name="incident_solution_create"),
    path("incidents/<int:pk>/rca/upload/", views.incident_rca_report_upload, name="incident_rca_report_upload"),
    path("incidents/close/form/", views.incident_close_form, name="incident_close_form"),
    path("incidents/<int:pk>/close/pdf/", views.incident_close_pdf, name="incident_close_pdf"),
    path("approvals/<int:pk>/", views.approval_detail, name="approval_detail"),
    path("solutions/", views.solution_list, name="solution_list"),
    path("solutions/schedule/", views.solution_schedule, name="solution_schedule"),
    path("solutions/completion/", views.solution_completion, name="solution_completion"),
    path("images/<int:pk>/delete/", views.image_delete, name="image_delete"),
    path("images/<int:pk>/edit/", views.image_update, name="image_update"),
    path("about/", views.about, name="about"),
    path("about/users/", views.about_users, name="about_users"),
    path("feedback/", views.feedback, name="feedback"),
    path("anniversaries/", views.anniversary_list, name="anniversary_list"),
    path("compliance/", views.compliance_dashboard, name="compliance_dashboard"),
    path("value/", views.value_dashboard, name="value_dashboard"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("search/equipment/", views.equipment_search, name="equipment_search"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
