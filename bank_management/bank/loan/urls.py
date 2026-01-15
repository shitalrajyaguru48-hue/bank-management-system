from django.urls import path
from . import views

urlpatterns = [
    path('home-loan/', views.home_loan, name='home_loan'),
]
