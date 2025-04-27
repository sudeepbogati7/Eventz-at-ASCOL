import random
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.urls import reverse
# Create your views here.
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth import login
from event.models import Event

User = get_user_model()


class HomeView(View):
    def get(self , request):
        events = Event.objects.filter(status='upcoming')[:3]
        
        return render(request, 'home.html' ,{'events': events})
    

class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validation
        if not email or not password:
            return render(request, "login.html", {"error": "Email and password are required."})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "Invalid email or password."})

        if not user.check_password(password):
            return render(request, "login.html", {"error": "Invalid email or password."})

        if not user.is_active:
            return render(request, "login.html", {"error": "Your account is inactive. Please contact support."})

        # Log the user in
        login(request, user)
        messages.success(request, "Login successful!")
        return redirect('event_dashboard')

class RegisterView(View):
    template_name = 'register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Extract form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        roll_num = request.POST.get('roll_num')
        faculty = request.POST.get('faculty')
        password = request.POST.get('password')
        c_password = request.POST.get('c_password')

        # Validation
        if not all([full_name, email, faculty, password, c_password]):
            return render(request, 'login.html', {"error":"All fields are required.", "post_data": request.POST })

        if password != c_password:
            return render(request, 'login.html', {"error":"Passwords do not match.", "post_data": request.POST })

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'login.html', {"error":"Email is already registered.", "post_data": request.POST })

        # Validate faculty
        valid_faculties = ['science', 'humanities', 'education', 'masters', 'mit']
        if faculty not in valid_faculties:
            return render(request, 'login.html', {"error":"Invalid faculty selected", "post_data": request.POST })

        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                roll_num=roll_num if roll_num else None,
                faculty=faculty
            )
            user.save()
        except Exception as e:
            return render(request, 'login.html', {f"error":e, "post_data": request.POST })
      
        messages.success(request, "Registration successful! Please verify your OTP.")
        return redirect('event_dashboard')
    

class VerifyOTPView(View):
    def get(self, request):
        return render(request, 'verify-otp.html')
    


class ProfileView(View):
    def get(self, request):
        return render(request, 'profile.html')
    

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('login')