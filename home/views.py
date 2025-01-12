from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required  # Correct
from django.views.decorators.cache import never_cache
from .models import Member
from .models import UserProfile
from django_otp.plugins.otp_totp.models import TOTPDevice
import pyotp
import qrcode
import logging
from io import BytesIO
from base64 import b64encode

logger = logging.getLogger(__name__)

#new sign up with FTL(first time login otp setup)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)  # Create user profile
            print(f"User {user.username} signed up successfully.")  # Debug print
            print("Redirecting to login page after signup.")  # Debug print
            return redirect('login')
        else:
            print("Signup form is invalid. Errors:", form.errors)  # Debug print
            return render(request, 'home/signup.html', {'form': form, 'error_message': 'Form is invalid. Please correct the errors.'})
    else:
        form = UserCreationForm()
        print("Rendering signup form.")  # Debug print
        return render(request, 'home/signup.html', {'form': form})

#@login_required(login_url='/login/')






#def home(request):
 #   return HttpResponse("Hello world!")  # Simple response for the homepage




@login_required#(login_url='/login/')
@never_cache
def home(request):
    mem = Member.objects.all()  # Fetch all member data from the database
    return render(request, 'home.html', {'mem': mem})  # Correct dictionary syntax

@login_required
def add(request):
    return render(request,'add.html')

#def home(request):
 #   mem=Member.objects.all()
  #  return render(request, 'home.html',{{'mem':mem}})


@login_required(login_url='/login/')
def addMember(request):
    x=request.POST['first']
    y=request.POST['last']
    z=request.POST['country']
    mem=Member(firstname=x,lastname=y,country=z)
    mem.save()
    return redirect("home/")

@login_required(login_url='/login/')
def delete(request,id):
 mem=Member.objects.get(id=id)
 mem.delete()
 return redirect("home")

@login_required(login_url='/login/')
def update(request,id):
    mem=Member.objects.get(id=id)
    return render(request,'update.html',{'mem':mem})

@login_required(login_url='/login/')
def uprec(request, id):
    if request.method == 'POST':
        x = request.POST['first']
        y = request.POST['last']
        z = request.POST['country']
        mem = Member.objects.get(id=id)
        mem.firstname = x
        mem.lastname = y
        mem.country = z
        mem.save()
        return redirect('home')  # Redirect to home after updating
    else:
        mem = Member.objects.get(id=id)
        return render(request, 'update.html', {'mem': mem})   

@login_required(login_url='/login/')
def addMember(request):
    if request.method == 'POST':
        x = request.POST['first']
        y = request.POST['last']
        z = request.POST['country']
        mem = Member(firstname=x, lastname=y, country=z)
        mem.save()
        return redirect('home')  # Redirect to the named URL 'home'
    else:
        return render(request, 'add.html')  # Render add.html for GET requests





#latest user login

def userLogin(request):
    print("DEBUG: Entering userLogin view.")
    if request.method == 'POST':
        print("DEBUG: Received POST request for login.")

        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"INFO: Attempting login for username '{username}'.")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"SUCCESS: User '{user.username}' authenticated successfully.")
            
            # Clear previous session data to avoid session conflicts
            print("INFO: Flushing session data.")
            request.session.flush()

            # Log the user in
            login(request, user)
            print(f"INFO: User '{user.username}' logged in successfully.")

            # Check for or create UserProfile
            try:
                profile, created = UserProfile.objects.get_or_create(user=user)
                if created:
                    print(f"INFO: New UserProfile created for '{user.username}'.")
                else:
                    print(f"INFO: Existing UserProfile found for '{user.username}'.")

                print(f"DEBUG: User '{user.username}' - OTP Setup Complete: {profile.otp_setup_complete}")

                if not profile.otp_setup_complete:
                    print(f"INFO: Redirecting user '{user.username}' to 'otp_setup' for first login.")
                    return redirect('otp_setup')
                else:
                    print(f"INFO: Redirecting user '{user.username}' to 'otp_check' for subsequent login.")
                    return redirect('otp_check')
            except Exception as e:
                print(f"ERROR: Failed to retrieve or create UserProfile for '{user.username}'. Exception: {e}")
        else:
            print(f"ERROR: Invalid login attempt for username '{username}'.")
    
    print("INFO: Rendering login form.")
    return render(request, 'login.html')


     









#


#@login_required(login_url='/login/')

#def otp_setup(request):
 #   return render(request, 'otp_setup.html')


#def otp_setup(request):
 #   user = request.user
  #  if not user.otp_secret:
   #     user.otp_secret = pyotp.random_base32()
    #    user.save()
    #totp = pyotp.TOTP(user.otp_secret)
    #otp_url = totp.provisioning_uri(name=user.username, issuer_name="Your App Name")
    #qr = qrcode.make(otp_url)
    #buffer = io.BytesIO()
    #qr.save(buffer, format='PNG')
    #buffer.seek(0)
    #return HttpResponse(buffer, content_type="image/png")

#def otp_setup(request):
 #   user = request.user
  #  if not user.otp_secret:
   #     user.otp_secret = pyotp.random_base32()
    #    user.save()

    #totp = pyotp.TOTP(user.otp_secret)
    #otp_url = totp.provisioning_uri(name=user.username, issuer_name="Your App Name")
    #qr = qrcode.make(otp_url)
    #buffer = io.BytesIO()
    #qr.save(buffer, format='PNG')
    #buffer.seek(0)
    
    #return HttpResponse(buffer, content_type="image/png")


@login_required(login_url='/login/')
def otp_setup(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Generate or retrieve the OTP device and QR code URL
    device, created = TOTPDevice.objects.get_or_create(user=user, name='default')
    qr_code_url = device.config_url
    
    # Mark OTP setup as complete
    profile.otp_setup_complete = True
    profile.save()

    context = {'qr_code_url': qr_code_url}
    return render(request, 'otp_setup.html', context)

@login_required(login_url='/login/')
def otp_verify(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user = request.user
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if device and device.verify_token(otp):
            # OTP is correct, redirect to home or desired page
            return redirect('home')
        else:
            # OTP is incorrect, reload the OTP check page with an error message
            context = {
                'error_message': 'Invalid OTP. Please try again.',
                'qr_code_url': device.config_url,  # Provide the QR code URL again if needed
            }
            return render(request, 'registration/otp_check.html', context)

    # If the request method is not POST, redirect back to the OTP check page
    return redirect('otp_check')



def otpCheck(request):
    return render(request, 'registration/otp_check.html')  # Update the path to match your directory structure

