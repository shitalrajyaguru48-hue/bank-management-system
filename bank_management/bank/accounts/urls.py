from django.urls import path
from accounts import views

urlpatterns = [
    path('', views.home, name='home'),                          # Home page
    path('register/', views.register, name='register'),         # Register page
    path('login/', views.login, name='login'),                  # Login page
    path('dashboard/customer/', views.customer_dash, name='customer_dash'),  # Customer dashboard
    path('logout/', views.logout_page, name='logout'),   # Logout
    path('profile/edit/', views.profile_edit, name='profile_edit'),         # Edit profile
    path('open-accounts/', views.open_accounts_redirect, name='open_accounts'),
    path('customer/send-message/', views.send_message, name='send_message'),

]
