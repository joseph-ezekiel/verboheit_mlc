import pytest
from django.urls import reverse

@pytest.fixture
def candidate_dashboard_url():
    return reverse("v1:api-candidate-dashboard")

@pytest.fixture
def staff_dashboard_url():
    return reverse("v1:api-staff-dashboard")

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