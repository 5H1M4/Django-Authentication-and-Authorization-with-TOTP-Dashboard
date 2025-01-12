from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Member(models.Model):
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    #otp_setup_complete = models.BooleanField(default=False) 
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    #otp_setup_complete = models.BooleanField(default=False)  # New field
    #id = models.CharField(max_length=50, primary_key=True)  # Custom ID field

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_setup_complete = models.BooleanField(default=False)




