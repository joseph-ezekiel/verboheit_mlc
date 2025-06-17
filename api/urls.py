from django.urls import path

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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # === AUTH ===
    path('', auth_views.api_root, name='api_root'),
    path('auth/login/', auth_views.login_api, name='api_login'),
    path('auth/register/candidate/', auth_views.register_candidate_api, name='api_register_candidate'),
    path('auth/register/staff/', auth_views.register_staff_api, name='api_register_staff'),
    
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # === CANDIDATES ===
    path('candidates/', candidate.candidate_list_api, name='api_candidate_list'),
    path('candidates/<int:candidate_id>/', candidate.candidate_detail_api, name='api_candidate_detail'),
    path('candidates/<int:candidate_id>/assign-role/', candidate.assign_candidate_role_api, name='api_assign_candidate_role'),
    path('candidates/<int:candidate_id>/scores/', score.candidate_scores_api, name='api_candidate_scores'),

    # === STAFF ===
    path('staff/', staff.staff_list_api, name='api_staff_list'),
    path('staff/<int:staff_id>/', staff.staff_detail_api, name='api_staff_detail'),

    # === EXAMS ===
    path('exams/', exam.exam_list_api, name='api_exam_list'),
    path('exams/<int:exam_id>/', exam.exam_detail_api, name='api_exam_detail'),

    # === QUESTIONS ===
    path('questions/', question.question_list_api, name='api_question_list'),
    path('questions/<int:question_id>/', question.question_detail_api, name='api_question_detail'),

    # === DASHBOARDS ===
    path('dashboard/candidate/', dashboard.candidate_dashboard_api, name='api_candidate_dashboard'),
    path('dashboard/staff/', dashboard.staff_dashboard_api, name='api_staff_dashboard'),

    # === LEADERBOARD ===
    path('leaderboard/', leaderboard.leaderboard_api, name='api_leaderboard'),
]
