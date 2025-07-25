import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from api.models import Candidate
from api.tests.conftest import create_dummy_user

User = get_user_model()


@pytest.fixture
def candidate_me_url():
    return reverse("v1:api-candidate-me")


@pytest.fixture
def candidate_list_url():
    return reverse("v1:api-candidate-list")


@pytest.fixture
def candidate_detail_url():
    def _detail_url(candidate_id):
        return reverse("v1:api-candidate-detail", kwargs={"candidate_id": candidate_id})

    return _detail_url


@pytest.fixture
def candidate_role_assign_url():
    def _assign_role_url(candidate_id):
        return reverse(
            "v1:api-candidate-role-assign", kwargs={"candidate_id": candidate_id}
        )

    return _assign_role_url


@pytest.mark.django_db
class TestCandidateMe:
    def test_candidate_me_by_candidate_success(
        self, api_client, candidate_me_url, create_logged_in_screening_candidate
    ):
        _, _, access = create_logged_in_screening_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_me_url)
        assert response.status_code == 200

    def test_candidate_me_by_staff_fail(
        self, api_client, candidate_me_url, create_logged_in_staff
    ):
        _, _, access = create_logged_in_staff()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_me_url)
        assert response.status_code == 403
        assert "Not a candidate" in response.data["error"]


@pytest.mark.django_db
class TestCandidateList:
    def test_candidate_list_by_candidate_fail(
        self, api_client, candidate_list_url, create_logged_in_screening_candidate
    ):
        _, _, access = create_logged_in_screening_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_list_url)
        assert response.status_code == 403

    def test_candidate_list_by_moderator_success(
        self, api_client, candidate_list_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_list_url)
        assert response.status_code == 200

    def test_candidate_list_by_volunteer_fail(
        self, api_client, candidate_list_url, create_logged_in_volunteer
    ):
        _, _, access = create_logged_in_volunteer()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_list_url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestCandidateDetail:
    def test_get_candidate_detail_by_candidate_fail(
        self, api_client, candidate_detail_url, create_logged_in_screening_candidate
    ):
        _, _, access = create_logged_in_screening_candidate()
        user = create_dummy_user()
        candidate = Candidate.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_detail_url(candidate.user.id))
        assert response.status_code == 403

    def test_get_candidate_detail_by_moderator_fail(
        self, api_client, candidate_detail_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        user = create_dummy_user()
        candidate = Candidate.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_detail_url(candidate.user.id))
        assert response.status_code == 403

    def test_get_candidate_detail_by_admin_success(
        self, api_client, candidate_detail_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        user = create_dummy_user()
        candidate = Candidate.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(candidate_detail_url(candidate.user.id))
        assert response.status_code == 200

    def test_update_candidate_detail_by_admin_success(
        self, api_client, candidate_detail_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        user = create_dummy_user()
        candidate = Candidate.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        data = {
            "user": {"first_name": "Spongebob", "last_name": "Squarepants"},
            "phone": "08033353762",
            "school": "Bikini Bottom College",
        }
        response = api_client.patch(
            candidate_detail_url(candidate.user.id), data, format="json"
        )
        assert response.status_code == 200

    def test_delete_candidate_detail_by_admin_success(
        self, api_client, candidate_detail_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        user = create_dummy_user()
        candidate = Candidate.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.delete(candidate_detail_url(candidate.user.id))
        assert response.status_code == 204


@pytest.mark.django_db
class TestAssignCandidateRole:
    def test_assign_candidate_role_by_admin_success(
        self, api_client, candidate_role_assign_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        user = create_dummy_user()
        candidate = Candidate.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        data = {"role": "league"}
        response = api_client.put(
            candidate_role_assign_url(candidate.user.id), data, format="json"
        )
        assert response.status_code == 200

    def test_assign_candidate_role_by_moderator_fail(
        self, api_client, candidate_role_assign_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        user = create_dummy_user()
        candidate = Candidate.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        data = {"role": "league"}
        response = api_client.put(
            candidate_role_assign_url(candidate.user.id), data, format="json"
        )
        assert response.status_code == 403
        assert "You do not have permission" in response.data["detail"]
