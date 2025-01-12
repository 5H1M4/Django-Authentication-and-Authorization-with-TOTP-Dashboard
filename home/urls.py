from django.urls import path
from . import views  # Import views from the same directory
from django.contrib.auth import views as auth_views
from .views import otp_setup, otp_verify
from django.shortcuts import redirect
from .models import UserProfile



def profile_redirect(request):
    if request.user.is_authenticated:  # Check if user is logged in
        profile, _ = UserProfile.objects.get_or_create(user=request.user)  # Ensure profile exists

        if not request.user.last_login:  # First-time login detected
            print(f"INFO: First-time login for '{request.user.username}'. Redirecting to OTP setup.")
            return redirect('otp_setup')

        elif not profile.otp_setup_complete:  # OTP not set up yet
            print(f"INFO: OTP not set up for '{request.user.username}'. Redirecting to OTP setup.")
            return redirect('otp_setup')

        else:  # Subsequent login with OTP already set up
            print(f"INFO: Subsequent login for '{request.user.username}'. Redirecting to OTP check.")
            return redirect('otp_check')

    else:  # If user is not logged in, redirect to login page
        print("ERROR: User is not authenticated. Redirecting to login.")
        return redirect('login')


urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'),  # Login page

    path('home/', views.home, name='home'),        # Home page URL
    path('login/', auth_views.LoginView.as_view(), name='login'),  # Login page
    
    
     path('accounts/profile/', profile_redirect, name='profile_redirect'),


    #path('accounts/profile/', lambda request: redirect('')),


    path('add/',views.add,name='add'), #add html page
    #path('signMember',views.signMember, name='signMember'),
    path('addMember',views.addMember, name='addMember'), #redirect after adding member
    path('home/delete/<int:id>/', views.delete, name='delete'),
    path('home/update/<int:id>/',views.update, name='update'),
    path('home/update/uprec/<int:id>/', views.uprec, name='uprec'),
    path('signup/', views.signup,name='signup'),
    path('otp-setup/', views.otp_setup, name='otp_setup'),
    path('otp_verify/', views.otp_verify, name='otp_verify'),
    path('otp-check/' , views.otpCheck, name='otp_check'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout')


     
     #path('login/', auth_views.LoginView.as_view(), name='login'), #login route 
    #path('', views.home, name='home'),  # Route for the homepage
]
