from django.core.mail import send_mail
import random
from django.conf import settings
from .models import Employee
import asyncio




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



# def department_change_email(receiver, changed_by ,change_employee, from_department, to_department, comments=None):
#     if not comments:
#         comments = "No message ..."
#     message = f"Hi {receiver}, \nThis mail is to inform you that {changed_by} moved {change_employee} from {from_department} department to {to_department}.\
#                 \nMessage : \n {comments}"
#     subject = "Department member change"
#     email_from = settings.EMAIL_HOST_USER
#     send_mail(subject, message, email_from, [receiver])


async def department_change_email_to_manager(receiver, changed_by ,change_employee, from_department, to_department, comments=None):
    if not comments:
        comments = "No message ..."
    message = f"Hi {receiver}, \nThis mail is to inform you that {changed_by} moved {change_employee} from {from_department} department to {to_department}.\
                \nMessage : \n {comments}"
    subject = "Department member change"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [receiver])



async def department_change_email_to_HR(receiver, change_employee, from_department, to_department, comments=None):
    if not comments:
        comments = "No message ..."
    message = f"Hi {receiver}, \nThis mail is to inform you that you moved {change_employee} from {from_department} department to {to_department}.\
                \nMessage : \n {comments}"
    subject = "Department member change"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [receiver])



async def department_change_email_to_employe(receiver, changed_by, to_department, comments=None):
    if not comments:
        comments = "No message ..."
    message = f"Hi {receiver}, \nThis mail is to inform you that your departement has been changed by {changed_by}.\
              \nFrom today onwards you will work with {to_department} department."
    subject = "Department change"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [receiver])



async def do_something():
    for i in range(0, 3):
        a = i
    print(a)


async def main_email(receiver, changed_by ,change_employee, from_department, to_department, comments=None):
    await department_change_email_to_manager(receiver, changed_by ,change_employee, from_department, 
                                             to_department, comments=None)
    await department_change_email_to_HR(receiver=changed_by, change_employee=change_employee, 
                                        from_department=from_department, to_department=to_department, comments=comments)
    await department_change_email_to_employe(receiver= change_employee, changed_by= changed_by, to_department=to_department,
                                             comments=comments)
    # await do_something()