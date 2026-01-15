from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/admin/', views.admin_dash, name='admin_dash'),
    path('dashboard/manager/', views.manager_dash, name='manager_dash'),
    path('redirect/', views.branch_redirect, name='branch_redirect'),
    path('manager/edit-balance/<int:profile_id>/', views.edit_balance, name='edit_balance'),
    path('manager/reply/<int:profile_id>/', views.reply, name='reply'),
]
