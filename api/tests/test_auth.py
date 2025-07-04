import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def valid_candidate_data():
    return {
        "user": {
            "username": "patrick",
            "first_name": "Patrick",
            "last_name": "Star",
            "email": "patrickstar@gmail.com",
        },
        "password1": "bikinibottom",
        "password2": "bikinibottom",
        "phone": "08033353762",
        "school": "Bikini Bottom College",
    }

@pytest.fixture
def valid_staff_data():
    return {
        "user": {
            "username": "patrick",
            "first_name": "Patrick",
            "last_name": "Star",
            "email": "patrickstar@gmail.com",
        },
        "password1": "bikinibottom",
        "password2": "bikinibottom",
        "phone": "08033353762",
        "occupation": "SpongeBob's bestfriend",
    }

@pytest.fixture
def candidate_registration_url():
    return reverse("v1:api-register-candidate")

@pytest.fixture
def staff_registration_url():
    return reverse("v1:api-register-staff")

@pytest.fixture
def login_url():
    return reverse("v1:api-login")

@pytest.fixture
def logout_url():
    return reverse("v1:api-logout")

@pytest.fixture
def create_logged_in_user(api_client):
    def do_create(username="patrick", password="password123"):
        user = User.objects.create_user(username=username, password=password)
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        api_client.force_authenticate(user=user)
        return user, str(refresh), str(refresh.access_token)
    return do_create

@pytest.mark.django_db
class TestCandidateRegistration:
    def test_success(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        assert response.status_code == 201
        assert "Registration successful" in response.data["message"]
        assert User.objects.filter(username="patrick").exists()

    def test_invalid(self, api_client, candidate_registration_url):
        data = {}
        response = api_client.post(candidate_registration_url, data, format="json")
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_duplicate_username(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        User.objects.create_user(username="patrick", email="existing@test.com")
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_duplicate_email(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        User.objects.create_user(username="existing", email="patrickstar@gmail.com")
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_invalid_email(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        valid_candidate_data["user"]["email"] = "not-an-email"
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_weak_password(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        valid_candidate_data["password1"] = "123"
        valid_candidate_data["user"]["email"] = "patrickstar@gmail.com"
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_long_username(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        valid_candidate_data["user"]["username"] = "a" * 15
        valid_candidate_data["user"]["email"] = "patrickstar@gmail.com"
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_missing_user_fields(self, api_client, candidate_registration_url):
        data = {
            "user": {"username": "patrick"},
            "password1": "bikinibottom",
        }
        response = api_client.post(candidate_registration_url, data, format="json")
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_wrong_method(self, api_client, candidate_registration_url):
        response = api_client.get(candidate_registration_url)
        assert response.status_code == 405

    def test_authenticated_user(self, api_client, candidate_registration_url):
        user = User.objects.create_user(username="existing", email="test@test.com")
        api_client.force_authenticate(user=user)
        data = {
            "user": {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@test.com",
            },
            "password1": "bikinibottom",
            "password2": "bikinibottom",
            "phone": "08033353762",
            "school": "Test School",
        }
        response = api_client.post(candidate_registration_url, data, format="json")
        assert response.status_code == 400

    def test_missing_password(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        del valid_candidate_data["password1"]
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        assert response.status_code == 400

    def test_missing_phone(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        del valid_candidate_data["phone"]
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        # Add your assertion based on your requirements

    def test_unicode_data(
        self, api_client, candidate_registration_url, valid_candidate_data
    ):
        valid_candidate_data["user"]["first_name"] = "José"
        valid_candidate_data["user"]["last_name"] = "García"
        response = api_client.post(
            candidate_registration_url, valid_candidate_data, format="json"
        )
        assert response.status_code == 201


@pytest.mark.django_db
class TestStaffRegistration:
    def test_success(self, api_client, staff_registration_url, valid_staff_data):
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        assert response.status_code == 201
        assert "Registration successful" in response.data["message"]
        assert User.objects.filter(username="patrick").exists()

    def test_invalid(self, api_client, staff_registration_url):
        response = api_client.post(staff_registration_url, {}, format="json")
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_duplicate_username(
        self, api_client, staff_registration_url, valid_staff_data
    ):
        User.objects.create_user(username="patrick", email="existing@test.com")
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_duplicate_email(
        self, api_client, staff_registration_url, valid_staff_data
    ):
        User.objects.create_user(username="existing", email="patrickstar@gmail.com")
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_invalid_email(self, api_client, staff_registration_url, valid_staff_data):
        valid_staff_data["user"]["email"] = "not-an-email"
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_weak_password(self, api_client, staff_registration_url, valid_staff_data):
        valid_staff_data["password1"] = "123"
        valid_staff_data["user"]["email"] = "patrickstar@gmail.com"
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_long_username(self, api_client, staff_registration_url, valid_staff_data):
        valid_staff_data["user"]["username"] = "a" * 15
        valid_staff_data["user"]["email"] = "patrickstar@gmail.com"
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_missing_user_fields(self, api_client, staff_registration_url):
        data = {
            "user": {
                "username": "patrick",
            },
            "password1": "bikinibottom",
        }
        response = api_client.post(staff_registration_url, data, format="json")
        assert response.status_code == 400
        assert "Registration failed" in response.data["error"]

    def test_wrong_method(self, api_client, staff_registration_url):
        response = api_client.get(staff_registration_url)
        assert response.status_code == 405

    def test_authenticated_user(self, api_client, staff_registration_url):
        user = User.objects.create_user(username="existing", email="test@test.com")
        api_client.force_authenticate(user=user)
        data = {
            "user": {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@test.com",
            },
            "password1": "bikinibottom",
            "password2": "bikinibottom",
            "phone": "08033353762",
            "school": "Test School",
        }
        response = api_client.post(staff_registration_url, data, format="json")
        assert response.status_code == 400

    def test_missing_password(
        self, api_client, staff_registration_url, valid_staff_data
    ):
        del valid_staff_data["password1"]
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        assert response.status_code == 400

    def test_missing_phone(self, api_client, staff_registration_url, valid_staff_data):
        del valid_staff_data["phone"]
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        # Add your assertion based on your requirements (is phone required or optional?)

    def test_unicode_data(self, api_client, staff_registration_url, valid_staff_data):
        valid_staff_data["user"]["first_name"] = "José"
        valid_staff_data["user"]["last_name"] = "García"
        response = api_client.post(
            staff_registration_url, valid_staff_data, format="json"
        )
        assert response.status_code == 201


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, login_url):
        User.objects.create_user(username="patrick", password="safepassword123")
        data = {"username": "patrick", "password": "safepassword123"}
        response = api_client.post(login_url, data, format="json")
        assert response.status_code == 200
        assert "tokens" in response.data
        assert response.data["user"]["username"] == "patrick"

    def test_login_wrong_password(self, api_client, login_url):
        User.objects.create_user(username="patrick", password="safepassword123")
        data = {"username": "patrick", "password": "wrongpass"}
        response = api_client.post(login_url, data, format="json")
        assert response.status_code == 401
        assert "error" in response.data

    def test_login_missing_fields(self, api_client, login_url):
        response = api_client.post(login_url, {}, format="json")
        assert response.status_code == 400

    def test_login_inactive_user(self, api_client, login_url):
        User.objects.create_user(
            username="patrick",
            email="patrick@test.com",
            password="safepassword123",
            is_active=False,
        )
        data = {"username": "patrick", "password": "safepassword123"}
        response = api_client.post(login_url, data, format="json")
        assert response.status_code == 401
        assert "Invalid credentials" in response.data["error"]

    def test_login_short_username(self, api_client, login_url):
        data = {"username": "pa", "password": "somepassword"}
        response = api_client.post(login_url, data, format="json")
        assert response.status_code == 400
        assert "at least 3 characters" in response.data["error"]

    def test_login_wrong_method(self, api_client, login_url):
        response = api_client.get(login_url)
        assert response.status_code == 405


@pytest.mark.django_db
class TestLogout:
    def test_logout_success(self, api_client, logout_url, create_logged_in_user):
        user, refresh, access = create_logged_in_user()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(
            logout_url, {"refresh_token": refresh}, format="json"
        )
        assert response.status_code == 200
        assert "Logout successful" in response.data["message"]

    def test_logout_missing_token(self, api_client, logout_url, create_logged_in_user):
        _, _, access = create_logged_in_user()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(logout_url, {}, format="json")
        assert response.status_code == 400
        assert "Refresh token is required" in response.data["error"]

    def test_logout_invalid_token(self, api_client, logout_url, create_logged_in_user):
        _, _, access = create_logged_in_user()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(
            logout_url, {"refresh_token": "invalidtoken"}, format="json"
        )
        assert response.status_code == 400
        assert "Invalid" in response.data["error"]

    def test_logout_auth_required(self, api_client, logout_url):
        response = api_client.post(
            logout_url, {"refresh_token": "sometoken"}, format="json"
        )
        assert response.status_code == 401