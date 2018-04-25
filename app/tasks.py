from celery import shared_task
from django.core.mail import send_mail
import os

#email, user_full_name, user_type, uid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "contest.settings")

def email_service(email, user_full_name, user_type, uid):
	print("Called")
	print(user_type)
	msg = """
	Hello {0},
	Thanks for registration as {1}. Please confirm your registration by following the link below.
	This is one time only. And it will not work after 24 hours.
	
	Confirmation link: http://127.0.0.1:8000/registration/{1}/confirm/{2}/
	
	Thanks
	IUBAT Beta Team
	""".format(user_full_name, user_type, uid)
	send_mail("Account confirmation", msg, from_email="logformat4@gmail.com",recipient_list=[email])
	return "Email sent successfully"