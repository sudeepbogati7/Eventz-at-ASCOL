
from django.contrib import admin
from django.urls import path, include
import authentication.views as auth_view

urlpatterns = [
    path('', auth_view.HomeView.as_view(), name='home'),
    path('register/', auth_view.RegisterView.as_view(), name='register'),
    path('login/', auth_view.LoginView.as_view(), name='login'),

    path('verify/', auth_view.VerifyOTPView.as_view(), name='verify-otp'),
    path('profile', auth_view.ProfileView.as_view(), name='profile'),
    path('logout', auth_view.LogoutView.as_view(), name='logout'),



]
