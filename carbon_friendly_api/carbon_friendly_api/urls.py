"""Carbon Tracker API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

handler404 = "core.views.error_404"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
