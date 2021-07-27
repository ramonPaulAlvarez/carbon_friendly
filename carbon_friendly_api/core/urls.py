from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    path('ch4', views.Ch4MetricView.as_view()),
    path('co2', views.Co2MetricView.as_view()),
    path('temperature_anomaly', views.TemperatureAnomalyMetricView.as_view()),
]
