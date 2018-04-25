from django.shortcuts import render, redirect
from . import models
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
import time
from django.contrib.auth.models import Group, User


def index_view(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	else:
		return redirect("/contests/")


def registration_view(request):
	if request.method == "POST":
		try:
			user_check = models.Member.objects.get(user_id=request.POST["id"])
		except:
			user_check = None
		if user_check:
			messages.error(request, "User already exists!")
			return redirect("/registration/")
		elif request.POST["password1"] != request.POST["password2"]:
			messages.error(request, "Password did not match!")
			return redirect("/registration/")
		elif request.POST["id"][4] != '3':
			print(request.POST["id"][4])
			messages.error(request, "You're not from CSE department")
			return redirect("/registration/")
		else:
			print(request.POST)
			new_member = models.Member.objects.create(
				first_name=request.POST["f_name"],
				last_name=request.POST["l_name"],
				user_id=request.POST["id"],
				recovery_id=request.POST["recovery_id"]
			)
			print(new_member.password)
			new_member.password = request.POST["password1"]
			group = Group.objects.get(name="participant")
			group.save()
			new_member.save()
			return redirect("/login/")

	return render(request, "contest/registration.html", {})


def login_view(request):
	if request.session.get("user_id"):
		return redirect("/contests/")
	if request.method == "POST":
		try:
			user = models.Member.objects.get(user_id=request.POST["id"])
		except:
			user = None
		if user and user.password == request.POST["password"]:
			request.session["user_id"] = user.user_id
			return redirect("/contests/")
		else:
			messages.error(request, "Login error!")
			return redirect("/login/")

	return render(request, "contest/login.html", {})


def logout_view(request):
	del request.session["user_id"]
	return redirect("/login/")

def recovery_view(request):
	if request.method == "POST":
		try:
			user = models.Member.objects.get(recovery_id=request.POST["recovery_id"])
			messages.success(request, "Your password is: " + user.password)
		except:
			messages.error(request, "Id not found!")
	return render(request, "contest/recovery.html", {})


def contest_list(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	contests = models.Contest.objects.all()
	return render(request, "contest/contestlist.html", {"contests": contests})


def question_detail(request, id):
	if not request.session.get("user_id"):
		return redirect("/login/")
	question = models.Question.objects.get(pk=id)
	return render(request, "contest/question_detail.html", {"question": question})


def contest_detail(request, id):
	if not request.session.get("user_id"):
		return redirect("/login/")

	now = time.ctime()
	print(now)
	contest = models.Contest.objects.get(id=id)
	contest_time = contest.contest_date
	print(contest_time)
	questions = models.Question.objects.filter(contest_id=contest.id)
	return render(request, "contest/contest_detail.html", {"questions": questions, "contest_name": contest.name})

def account_detail(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	user = models.Member.objects.get(user_id=request.session["user_id"])
	#contests = user.contests.values_list("pk", flat=True)
	solutions = models.Solution.objects.filter(participant_id=user.id)
	#print(contests)
	contests = user.contestpoint_set.count()
	print(contests)
	return render(request, "contest/account_detail.html", {"user": user})

def ranking_list(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	users = models.Member.objects.all().order_by("-total_point")
	return render(request, "contest/ranking_list.html", {"users": users})

def ranking_list_contest(request, id):
	if not request.session.get("user_id"):
		return redirect("/login/")
	contest = models.Contest.objects.get(pk=id)
	users = contest.member_set.count()
	a = models.ContestPoint.objects.filter(contest=contest).order_by("-point").order_by("-submission_date")
	return render(request, "contest/ranking_list_contest.html", {"contest_data": a, "contest": contest})

def report_generate(request, id):
	contest = models.Contest.objects.get(pk=id)
	a = models.ContestPoint.objects.filter(contest=contest).order_by("-point").order_by("-submission_date")
	return render(request, "contest/report.html", {"contest_data": a, "contest": contest})

def submit_solution(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	question = models.Question.objects.get(pk=request.POST["question_id"])
	participant = models.Member.objects.get(user_id=request.session["user_id"])
	contest = models.Contest.objects.get(pk=question.contest_id)
	print(request.session["user_id"])
	try:
		solution_check = models.Solution.objects.get(question_id=question.id, participant_id=participant.id)
	except:
		solution_check = None

	if solution_check:
		messages.error(request, "Sorry, you already submitted the solution!")
		return redirect(request.META["HTTP_REFERER"])

	else:
		solution = models.Solution.objects.create(
			question=question,
			participant=participant,
			body=request.POST["solution"]
		)
		a = models.ContestPoint.objects.create(contest=contest, member=participant)
		#contest.member_set.add(participant)
		if request.POST["solution"] == question.correct_ans:
			a.point = question.point
			participant.total_point += question.point
			a.save()
			participant.save()
	messages.success(request, "Your solution submitetd successfully")
	return redirect(request.META["HTTP_REFERER"])












