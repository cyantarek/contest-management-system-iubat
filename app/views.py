from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
import time
import re
import redis
from django.db import connection
from .tasks import email_service
from .utils import uuid_gen

cur = connection.cursor()

r = redis.Redis(host="localhost", port="6379", db="1")


def registration_participant(request, user_type):
	if user_type == "judge":
		if request.method == "POST":
			password = request.POST["password1"]
			password2 = request.POST["password2"]
			if len(password) < 8:
				messages.error(request, "Password should be at least 8 characters")
			else:
				if password != password2:
					messages.error(request, "Password did not match")
				else:
					if re.search(r'[A-Z]{1,3}', password) and \
							re.search(r'[a-z]{1,3}', password) and \
							re.search(r'[0-9]{1,3}', password) and \
							re.search(r'[!@$&]{1,3}', password):
						cur.execute("SELECT * FROM judge WHERE user_id='%s' OR email='%s'" % (
						request.POST["user_id"], request.POST["email"]))
						user_check = cur.fetchall()
						cur.execute("SELECT * FROM participant WHERE versity_id='%s' OR email='%s'" % (
							request.POST["user_id"], request.POST["email"]))
						user_check2 = cur.fetchall()
						if len(user_check) > 0 or len(user_check2) > 0:
							messages.error(request, "User already exists")
						else:
							cur.execute(
								"INSERT INTO judge(f_name, l_name, user_id, password, join_date, is_admin, approved, email) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
									request.POST["f_name"], request.POST["l_name"], request.POST["user_id"],
									request.POST["password1"], time.ctime(), 0, 0, request.POST["email"]))

							full_name = request.POST["f_name"] + " " + request.POST["l_name"]
							confirm_id = uuid_gen()
							cur.execute(
								"INSERT INTO email_activation(confirm_id, is_used, email) VALUES('%s', '%s', '%s')" % (
								confirm_id, 0, request.POST["email"]))
							email_service(request.POST["email"], full_name, user_type, confirm_id)
							return redirect("/registration/success/")
					else:
						messages.error(request, "Password weak! Please follow the hint")
		return render(request, "contest/registration_judge.html")
	else:
		if request.method == "POST":
			password = request.POST["password1"]
			password2 = request.POST["password2"]
			if len(password) < 8:
				messages.error(request, "Password should be at least 8 characters")
			else:
				if password != password2:
					messages.error(request, "Password did not match")
				else:
					if re.search(r'[A-Z]{1,3}', password) and \
							re.search(r'[a-z]{1,3}', password) and \
							re.search(r'[0-9]{1,3}', password) and \
							re.search(r'[!@$&]{1,3}', password):
						cur.execute("SELECT * FROM participant WHERE versity_id='%s' OR email='%s'" % (
						request.POST["versity_id"], request.POST["email"]))
						user_check = cur.fetchall()
						if len(user_check) > 0:
							messages.error(request, "User already exists")
						else:
							cur.execute(
								"INSERT INTO participant(f_name, l_name, password, versity_id, email) VALUES('%s', '%s', '%s', '%s', '%s')" % (
									request.POST["f_name"], request.POST["l_name"], request.POST["password1"],
									request.POST["versity_id"], request.POST["email"]))
							full_name = request.POST["f_name"] + " " + request.POST["l_name"]
							confirm_id = uuid_gen()
							cur.execute(
								"INSERT INTO email_activation(confirm_id, is_used, email) VALUES('%s', '%s', '%s')" % (
									confirm_id, 0, request.POST["email"]))
							email_service(request.POST["email"], full_name, user_type, confirm_id)
							return redirect("/registration/success/")
					else:
						messages.error(request, "Password weak! Please follow the hint")
		return render(request, "contest/registration_participant.html")


def login_view(request):
	if request.method == "POST":
		if request.POST["user_type"] == "admin":
			cur.execute("SELECT * FROM judge WHERE user_id='%s' OR email='%s'" % (
			request.POST.get("id"), request.POST.get("id")))
			admin_check = cur.fetchone()
			if not admin_check:
				messages.error(request, "Not registered")
			else:
				if admin_check[6] != 1:
					messages.error(request, "You're not an admin")
				else:
					if admin_check[4] != request.POST["password"]:
						messages.error(request, "Password error")
					else:
						# login and store session [user_id, user_type]
						pass
		elif request.POST["user_type"] == "judge":
			cur.execute("SELECT * FROM judge WHERE user_id='%s' OR email='%s'" % (
			request.POST.get("id"), request.POST.get("id")))
			judge_check = cur.fetchone()
			if not judge_check:
				messages.error(request, "Not registered as judge")
			else:
				if judge_check[4] != request.POST["password"]:
					messages.error(request, "Password error")
				else:
					if judge_check[7] != 1:
						messages.error(request, "Account not confirmed")
					else:
						request.session["user_id"] = judge_check[0]
						request.session["user_type"] = "judge"
						return redirect("/contests/")

		elif request.POST["user_type"] == "participant":
			cur.execute("SELECT * FROM participant WHERE versity_id='%s' OR email='%s'" % (
			request.POST.get("id"), request.POST.get("id")))
			parti_check = cur.fetchone()
			if not parti_check:
				messages.error(request, "Not registered as participant")
			else:
				if parti_check[4] != request.POST["password"]:
					messages.error(request, "Password error")
				else:
					if parti_check[6] != 1:
						messages.error(request, "Account not confirmed")
					else:
						request.session["user_id"] = parti_check[0]
						request.session["user_type"] = "participant"
						return redirect("/contests/")

	return render(request, "contest/Login.html")


def logout_view(request):
	del request.session["user_id"]
	del request.session["user_type"]
	return redirect("/login/")


def success_view(request):
	return render(request, "contest/registration_success.html")


def resend_email(request):
	if request.method == "POST":
		if request.POST["user_type"] == "judge":
			cur.execute("SELECT * FROM judge WHERE email='%s'" % (request.POST["email"]))
			email_check = cur.fetchall()
			if len(email_check) < 1:
				messages.error(request, "Email not registered")
			else:
				messages.error(request, "Email sent again successfully!")
				# resend_email
				pass
		elif request.POST["user_type"] == "participant":
			cur.execute("SELECT * FROM participant WHERE email='%s'" % (request.POST["email"]))
			email_check = cur.fetchall()
			if len(email_check) < 1:
				messages.error(request, "Email not registered")
			else:
				# resend_email
				messages.error(request, "Email sent again successfully!")
				pass
	return render(request, "contest/email_resend.html")


def registration_confirmation(request, user_type, confirm_id):
	if user_type == "judge":
		cur.execute("SELECT * FROM email_activation WHERE confirm_id='%s'" % confirm_id)
		email_check = cur.fetchone()
		if email_check[2] == 1:
			return HttpResponse("Already confirmed")
		else:
			cur.execute("UPDATE judge SET approved=1 WHERE email='%s'" % email_check[0])
			cur.execute("UPDATE email_activation SET is_used=1 WHERE email='%s'" % email_check[0])
			return HttpResponse("Confirmed")

	elif user_type == "participant":
		cur.execute("SELECT * FROM email_activation WHERE confirm_id='%s'" % confirm_id)
		email_check = cur.fetchone()
		if email_check[2] == 1:
			return HttpResponse("Already confirmed")
		else:
			cur.execute("UPDATE participant SET is_approved=1 WHERE email='%s'" % email_check[0])
			cur.execute("UPDATE email_activation SET is_used=1 WHERE email='%s'" % email_check[0])
			return HttpResponse("Confirmed")


def contest_list(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	contests = None
	return render(request, "contest/contestlist.html", {"contests": contests})

