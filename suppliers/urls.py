from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='list'),
    path('search/', views.supplier_search, name='search'),
    path('<int:supplier_id>/', views.supplier_detail, name='detail'),
]