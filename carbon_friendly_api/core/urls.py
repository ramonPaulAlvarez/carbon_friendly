from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('docs', views.docs, name='docs'),
    path('contact', views.contact, name='contact'),
    path('ch4', views.MethaneView.as_view()),
    path('co2', views.CarbonDioxideView.as_view()),
    path('n2o', views.NitrousOxideView.as_view()),
    path('temperature_change', views.TemperatureChangeView.as_view()),
]
