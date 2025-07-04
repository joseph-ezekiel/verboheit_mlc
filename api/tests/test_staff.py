import pytest
from django.urls import reverse
from api.tests.conftest import create_dummy_user
from api.models import Staff, User

@pytest.fixture
def staff_me_url():
    return reverse("v1:api-staff-me")

@pytest.fixture
def staff_list_url():
    return reverse("v1:api-staff-list")

@pytest.fixture
def staff_detail_url():
    def _detail_url(staff_id):
        return reverse("v1:api-staff-detail", kwargs={"staff_id": staff_id})
    return _detail_url

@pytest.fixture
def staff_role_assign_url():
    def _assign_role_url(staff_id):
        return reverse("v1:api-staff-role-assign", kwargs={"staff_id": staff_id})
    return _assign_role_url

@pytest.mark.django_db
class TestStaffMe:
    def test_staff_me_by_candidate_fail(
        self, api_client, staff_me_url, create_logged_in_screening_candidate
    ):
        _, _, access = create_logged_in_screening_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_me_url)
        assert response.status_code == 403

    def test_staff_me_by_staff_success(
        self, api_client, staff_me_url, create_logged_in_staff
    ):
        _, _, access = create_logged_in_staff()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_me_url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestStaffList:
    def test_staff_list_by_candidate_fail(
        self, api_client, staff_list_url, create_logged_in_screening_candidate
    ):
        _, _, access = create_logged_in_screening_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_list_url)
        assert response.status_code == 403

    def test_staff_list_by_moderator_success(
        self, api_client, staff_list_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_list_url)
        assert response.status_code == 200

    def test_staff_list_by_volunteer_fail(
        self, api_client, staff_list_url, create_logged_in_volunteer
    ):
        _, _, access = create_logged_in_volunteer()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_list_url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestStaffDetail:
    def test_get_staff_detail_by_candidate_fail(
        self, api_client, staff_detail_url, create_logged_in_screening_candidate
    ):
        _, _, access = create_logged_in_screening_candidate()
        user = create_dummy_user()
        staff = Staff.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_detail_url(staff.user.id))
        assert response.status_code == 403

    def test_get_staff_detail_by_moderator_fail(
        self, api_client, staff_detail_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        user = create_dummy_user()
        staff = Staff.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_detail_url(staff.user.id))
        assert response.status_code == 403

    def test_get_staff_detail_by_admin_fail(
        self, api_client, staff_detail_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        user = create_dummy_user()
        staff = Staff.objects.create(user=user, role="moderator")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_detail_url(staff.user.id))
        assert response.status_code == 403

    def test_get_staff_detail_by_owner_success(
        self, api_client, staff_detail_url, create_logged_in_owner
    ):
        _, _, access = create_logged_in_owner()
        user = create_dummy_user()
        staff = Staff.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(staff_detail_url(staff.user.id))
        assert response.status_code == 200

    def test_update_staff_detail_by_owner_success(
        self, api_client, staff_detail_url, create_logged_in_owner
    ):
        _, _, access = create_logged_in_owner()
        user = create_dummy_user()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        staff = Staff.objects.create(user=user, role="volunteer")
        data = {
            "user": {"first_name": "Spongebob", "last_name": "Squarepants"},
            "phone": "08033353762",
            "occupation": "Krabby Patty chef",
            "role": "moderator",
        }
        response = api_client.patch(
            staff_detail_url(staff.user.id), data, format="json"
        )
        assert response.status_code == 200

    def test_delete_staff_detail_by_owner_success(
        self, api_client, staff_detail_url, create_logged_in_owner
    ):
        _, _, access = create_logged_in_owner()
        user = create_dummy_user()
        staff = Staff.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.delete(staff_detail_url(staff.user.id))
        assert response.status_code == 204


@pytest.mark.django_db
class TestAssignStaffRole:
    def test_assign_staff_role_by_admin_fail(
        self, api_client, staff_role_assign_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        user = create_dummy_user()
        staff = Staff.objects.create(user=user, role="volunteer")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        data = {"role": "moderator"}
        response = api_client.put(
            staff_role_assign_url(staff.user.id), data, format="json"
        )
        assert response.status_code == 403
        assert "You do not have permission" in response.data["detail"]

    def test_assign_staff_role_by_moderator_fail(
        self, api_client, staff_role_assign_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        user = create_dummy_user()
        staff = Staff.objects.create(user=user, role="volunteer")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        data = {"role": "moderator"}
        response = api_client.put(
            staff_role_assign_url(staff.user.id), data, format="json"
        )
        assert response.status_code == 403
        assert "You do not have permission" in response.data["detail"]

    def test_assign_staff_role_by_owner_success(
        self, api_client, staff_role_assign_url, create_logged_in_owner
    ):
        _, _, access = create_logged_in_owner()
        user = create_dummy_user()
        staff = Staff.objects.create(user=user, role="volunteer")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        data = {"role": "moderator"}
        response = api_client.put(
            staff_role_assign_url(staff.user.id), data, format="json"
        )
        assert response.status_code == 200
