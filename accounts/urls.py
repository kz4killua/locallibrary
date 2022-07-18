from re import template
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register', views.register, name='register'),
]