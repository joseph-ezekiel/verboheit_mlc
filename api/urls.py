"""
URL configuration for the API endpoints of the application.

This module defines URL patterns for all API routes, including:
- Authentication and JWT token handling
- User registration (candidates and staff)
- Candidate and staff management
- Exams and questions
- Dashboard and account operations
- Leaderboard

All views are organized and grouped by functionality for clarity.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    auth_views,
    candidate,
    staff,
    exam,
    question,
    score,
    leaderboard,
    dashboard,
)

APP_NAME = "api"

urlpatterns = [
    # === ROOT & AUTH ===
    path("", auth_views.api_root, name="api-root"),
    path("auth/login/", auth_views.login_api, name="api-login"),
    path("auth/logout/", auth_views.logout_api, name="api-logout"),
    path(
        "auth/register/candidate/",
        auth_views.CandidateRegistrationView.as_view(),
        name="api-register-candidate",
    ),
    path(
        "auth/register/staff/",
        auth_views.StaffRegistrationView.as_view(),
        name="api-register-staff",
    ),
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # === CANDIDATES ===
    path(
        "candidates/", candidate.CandidateListView.as_view(), name="api-candidate-list"
    ),
    path("candidates/me/", candidate.candidate_me_api, name="api-candidate-me"),
    path(
        "candidates/<int:candidate_id>/",
        candidate.CandidateDetailView.as_view(),
        name="api-candidate-detail",
    ),
    path(
        "candidates/<int:candidate_id>/roles/assign/",
        candidate.AssignCandidateRoleView.as_view(),
        name="api-candidate-role-assign",
    ),
    path(
        "candidates/<int:candidate_id>/scores/",
        score.candidate_scores_api,
        name="api-candidate-scores",
    ),
    path(
        "candidates/<int:candidate_id>/exam-history/",
        exam.ExamHistoryView.as_view(),
        name="api-candidate-exam-history",
    ),
    # === STAFF ===
    path("staff/", staff.StaffListView.as_view(), name="api-staff-list"),
    path("staff/me/", staff.staff_me_api, name="api-staff-me"),
    path(
        "staff/<int:staff_id>/",
        staff.StaffDetailView.as_view(),
        name="api-staff-detail",
    ),
    path(
        "staff/<int:staff_id>/roles/assign/",
        staff.AssignStaffRoleView.as_view(),
        name="api-staff-role-assign",
    ),
    # === EXAMS ===
    path("exams/", exam.ExamListView.as_view(), name="api-exam-list"),
    path("exams/<int:exam_id>/", exam.ExamDetailView.as_view(), name="api-exam-detail"),
    path(
        "exams/<int:exam_id>/questions/",
        exam.ExamQuestionsView.as_view(),
        name="api-exam-questions",
    ),
    path(
        "exams/<int:exam_id>/scores/",
        score.submit_score_api,
        name="api-exam-score-submit",
    ),
    # === QUESTIONS ===
    path("questions/", question.question_list_api, name="api-question-list"),
    path(
        "questions/<int:question_id>/",
        question.question_detail_api,
        name="api-question-detail",
    ),
    # === DASHBOARDS ===
    path(
        "dashboard/candidate/",
        dashboard.candidate_dashboard_api,
        name="api-candidate-dashboard",
    ),
    path("dashboard/staff/", dashboard.staff_dashboard_api, name="api-staff-dashboard"),
    # === ACCOUNT MANAGEMENT ===
    path(
        "account-management/",
        dashboard.AccountManagementView.as_view(),
        name="api-account-management",
    ),
    path(
        "account-management/<int:user_id>/",
        dashboard.AccountManagementView.as_view(),
        name="api-account-management-detail",
    ),
    # === LEADERBOARD ===
    path("leaderboard/", leaderboard.leaderboard_api, name="api-leaderboard"),
]
