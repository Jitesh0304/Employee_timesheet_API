from django.core.mail import send_mail
import random
from django.conf import settings
from .models import Employee




## send the forgot password otp
def reset_pass_otp_email(email):
    subject = "Your account verification email.."
    # otp = random.randint(100000,999999)
    otp = 987654
    message = f"Your OTP for forgot password is {otp}"
    email_from = settings.EMAIL_HOST_USER
    ## send the required dat and parameters in the send_email function
    send_mail(subject, message, email_from, [email])
    user_obj = Employee.objects.get(email=email)
    ## save the otp in the user table for verification
    user_obj.otp = otp
    ## make the user unverified
    user_obj.is_verified = False
    user_obj.save()


