# statement/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('statement/', views.customer_statement, name='customer_statement'),
]
