import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Candidate, Staff, Exam, CandidateScore

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def submit_exam_score_url():
    def _dynamic_url(exam_id):
        return reverse("v1:api-submit-exam-score", kwargs={"exam_id": exam_id})
    return _dynamic_url

@pytest.fixture
def create_logged_in_screening_candidate(api_client):
    def do_create(username="patrick", email="patrick@test.com", password="password123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        candidate = Candidate.objects.create(user=user, role="screening")
        refresh = RefreshToken.for_user(candidate.user)
        api_client.force_authenticate(user=candidate.user)
        return candidate, str(refresh), str(refresh.access_token)
    return do_create

@pytest.fixture
def create_logged_in_moderator(api_client):
    def do_create(username="moderator", email="moderator@test.com", password="password123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        staff = Staff.objects.create(user=user, role="moderator")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)
    return do_create

@pytest.fixture
def create_logged_in_admin(api_client):
    def do_create(username="admin", email="admin@test.com", password="password123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        staff = Staff.objects.create(user=user, role="admin")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)
    return do_create

@pytest.mark.django_db
class TestSubmitExamScore:
    def test_submit_exam_score_by_candidate_fail(
        self, api_client, submit_exam_score_url, create_logged_in_screening_candidate
    ):
        candidate, _, access = create_logged_in_screening_candidate()
        exam_data = {
            "stage": "screening",
            "title": "Screening Exam",
            "description": "Screening exam",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
        }
        exam = Exam.objects.create(**exam_data)
        score_data = {
            "candidate_id": candidate.pk,
            "score": 5
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.put(submit_exam_score_url(exam.id), score_data, format="json")
        assert response.status_code == 403
    
    def test_submit_exam_score_by_moderator_fail(
        self, api_client, submit_exam_score_url, create_logged_in_moderator, create_logged_in_screening_candidate
    ):
        candidate, _, _ = create_logged_in_screening_candidate()
        moderator, _, access = create_logged_in_moderator()
        exam_data = {
            "stage": "screening",
            "title": "Screening Exam",
            "description": "Screening exam",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
        }
        exam = Exam.objects.create(**exam_data)
        score_data = {
            "candidate_id": candidate.pk,
            "score": 5
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.put(submit_exam_score_url(exam.id), score_data, format="json")
        assert response.status_code == 403
    
    def test_submit_exam_score_by_admin_success(
        self, api_client, submit_exam_score_url, create_logged_in_admin, create_logged_in_screening_candidate
    ):
        candidate, _, _ = create_logged_in_screening_candidate()
        admin, _, access = create_logged_in_admin()
        exam_data = {
            "stage": "screening",
            "title": "Screening Exam",
            "description": "Screening exam",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
        }
        exam = Exam.objects.create(**exam_data)
        score_data = {
            "candidate_id": candidate.pk,
            "score": 5
        }
        candidate_score, _ = CandidateScore.objects.get_or_create(
            candidate=candidate,
            exam=exam,
        )
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.put(submit_exam_score_url(exam.id), score_data, format="json")
        assert response.status_code == 200