import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Candidate, Staff, Exam

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def candidate_dashboard_url():
    return reverse("v1:api-candidate-dashboard")

@pytest.fixture
def staff_dashboard_url():
    return reverse("v1:api-staff-dashboard")

@pytest.fixture
def create_logged_in_candidate(api_client):
    def do_create(username="patrick", email="patrick@test.com", password="password123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        candidate = Candidate.objects.create(user=user, role="league")
        refresh = RefreshToken.for_user(candidate.user)
        api_client.force_authenticate(user=candidate.user)
        return candidate, str(refresh), str(refresh.access_token)
    return do_create

@pytest.fixture
def create_logged_in_staff(api_client):
    def do_create(username="staff", email="staff@test.com", password="password123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        staff = Staff.objects.create(user=user, role="admin")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)
    return do_create

@pytest.mark.django_db
class TestDashboard:
    def test_candidate_dashboard_by_candidate_success(
        self, api_client, candidate_dashboard_url, create_logged_in_candidate
    ):
        _, _, access = create_logged_in_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_dashboard_url)
        assert response.status_code == 200

    def test_candidate_dashboard_by_staff_fail(
        self, api_client, candidate_dashboard_url, create_logged_in_staff
    ):
        _, _, access = create_logged_in_staff()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_dashboard_url)
        assert response.status_code == 403
        
    def test_staff_dashboard_by_staff_success(
        self, api_client, staff_dashboard_url, create_logged_in_staff
    ):
        _, _, access = create_logged_in_staff()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_dashboard_url)
        assert response.status_code == 200

    def test_staff_dashboard_by_candidate_fail(
        self, api_client, staff_dashboard_url, create_logged_in_candidate
    ):
        _, _, access = create_logged_in_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_dashboard_url)
        assert response.status_code == 403