from django.urls import path
from . import views
from django.http import HttpResponseRedirect

urlpatterns = [
	path("", lambda x: HttpResponseRedirect("/login/")),
	path("registration/<user_type>/confirm/<confirm_id>/", views.registration_confirmation),
	path("registration/<user_type>/", views.registration_participant),
	path("registration/success/", views.success_view),
	path("login/", views.login_view),
	path("resend_email/", views.resend_email),
	path("logout/", views.logout_view),
	path("contests/", views.contest_list),
	# path("question/<id>/", views.question_detail),
	# path("contests/<id>/", views.contest_detail),
	# path("account/", views.account_detail),
	# path("ranking/", views.ranking_list),
	# path("ranking_contest/<id>/", views.ranking_list_contest),
	# path("submit_solution/", views.submit_solution),
	# path("report_generate/<id>/", views.report_generate)
]