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
def load_leaderboard_url():
    return reverse("v1:api-load-leaderboard")

@pytest.fixture
def publish_leaderboard_url():
    return reverse("v1:api-publish-leaderboard")

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
def create_logged_in_league_candidate(api_client):
    def do_create(username="patrick", email="patrick@test.com", password="password123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        candidate = Candidate.objects.create(user=user, role="league")
        refresh = RefreshToken.for_user(candidate.user)
        api_client.force_authenticate(user=candidate.user)
        return candidate, str(refresh), str(refresh.access_token)
    return do_create

@pytest.fixture
def create_logged_in_volunteer(api_client):
    def do_create(username="volunteer", email="volunteer@test.com", password="password123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        staff = Staff.objects.create(user=user, role="volunteer")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)
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

@pytest.fixture
def create_logged_in_owner(api_client):
    def do_create(username="owner", email="owner@test.com", password="password123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        staff = Staff.objects.create(user=user, role="owner")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)
    return do_create

@pytest.fixture
def published_leaderboard(api_client, create_logged_in_owner, publish_leaderboard_url):
    _, _, owner_access = create_logged_in_owner()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {owner_access}")
    response = api_client.post(publish_leaderboard_url)
    assert response.status_code == 200

@pytest.mark.django_db
class TestNoLeaderboard:
    def test_load_leaderboard_by_league_candidate_fail(
        self, api_client, load_leaderboard_url, create_logged_in_league_candidate
    ):
        _, _, access = create_logged_in_league_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 404
        
    def test_load_leaderboard_by_moderator_fail(
        self, api_client, load_leaderboard_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 404

    def test_load_leaderboard_by_admin_fail(
        self, api_client, load_leaderboard_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 404

    def test_load_leaderboard_by_owner_fail(
        self, api_client, load_leaderboard_url, create_logged_in_owner
    ):
        _, _, access = create_logged_in_owner()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 404

@pytest.mark.django_db
class TestPublishLeaderboard:
    def test_publish_leaderboard_by_owner_success(
        self, api_client, publish_leaderboard_url, create_logged_in_owner
    ):
        _, _, access = create_logged_in_owner()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(publish_leaderboard_url)
        assert "Leaderboard published!" in response.data["message"]
        assert response.status_code == 200

    def test_publish_leaderboard_by_admin_success(
        self, api_client, publish_leaderboard_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(publish_leaderboard_url)
        assert "Leaderboard published!" in response.data["message"]
        assert response.status_code == 200
        
    def test_publish_leaderboard_by_moderator_fail(
        self, api_client, publish_leaderboard_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(publish_leaderboard_url)
        assert response.status_code == 403

    def test_publish_leaderboard_by_volunteer_fail(
        self, api_client, publish_leaderboard_url, create_logged_in_volunteer
    ):
        _, _, access = create_logged_in_volunteer()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(publish_leaderboard_url)
        assert response.status_code == 403
    
@pytest.mark.django_db
class TestLoadLeaderboard:

    def test_load_leaderboard_by_screening_candidate_fail(
        self, api_client, load_leaderboard_url, create_logged_in_screening_candidate, published_leaderboard
    ):
        _, _, access = create_logged_in_screening_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 403

    def test_load_leaderboard_by_league_candidate_success(
        self, api_client, load_leaderboard_url, create_logged_in_league_candidate, published_leaderboard
    ):
        _, _, access = create_logged_in_league_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 200
        
    def test_load_leaderboard_by_volunteer_fail(
        self, api_client, load_leaderboard_url, create_logged_in_volunteer, published_leaderboard
    ):
        _, _, access = create_logged_in_volunteer()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 403
        
    def test_load_leaderboard_by_moderator_success(
        self, api_client, load_leaderboard_url, create_logged_in_moderator, published_leaderboard
    ):
        _, _, access = create_logged_in_moderator()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 200
        
    def test_load_leaderboard_by_admin_success(
        self, api_client, load_leaderboard_url, create_logged_in_admin, published_leaderboard
    ):
        _, _, access = create_logged_in_admin()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(load_leaderboard_url)
        assert response.status_code == 200