from django.urls import path
from . import views

app_name = 'quality'

urlpatterns = [
    path('', views.quality_assurance, name='assurance'),
    path('report/', views.quality_report, name='report'),
]