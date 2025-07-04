import pytest
from django.urls import reverse

@pytest.fixture
def load_leaderboard_url():
    return reverse("v1:api-load-leaderboard")

@pytest.fixture
def publish_leaderboard_url():
    return reverse("v1:api-publish-leaderboard")

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