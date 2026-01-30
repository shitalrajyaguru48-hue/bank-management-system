# statement/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('statement/', views.customer_statement, name='customer_statement'),
    path('statement/pdf/', views.download_statement_pdf, name='download_statement_pdf'),

]
