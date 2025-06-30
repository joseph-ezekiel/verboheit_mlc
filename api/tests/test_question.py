import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Candidate, Staff, Question

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def question_list_url():
    return reverse("v1:api-question-list")


@pytest.fixture
def question_detail_url():
    def _detail_url(question_id):
        return reverse("v1:api-question-detail", kwargs={"question_id": question_id})

    return _detail_url


@pytest.fixture
def create_logged_in_screening_candidate(api_client):
    def do_create(username="patrick", email="patrick@test.com", password="password123"):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        candidate = Candidate.objects.create(user=user, role="screening")
        refresh = RefreshToken.for_user(candidate.user)
        api_client.force_authenticate(user=candidate.user)
        return candidate, str(refresh), str(refresh.access_token)

    return do_create


@pytest.fixture
def create_logged_in_volunteer(api_client):
    def do_create(
        username="volunteer", email="volunteer@test.com", password="password123"
    ):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        staff = Staff.objects.create(user=user, role="volunteer")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)

    return do_create


@pytest.fixture
def create_logged_in_moderator(api_client):
    def do_create(
        username="moderator", email="moderator@test.com", password="password123"
    ):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        staff = Staff.objects.create(user=user, role="moderator")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)

    return do_create


@pytest.fixture
def create_logged_in_admin(api_client):
    def do_create(username="admin", email="admin@test.com", password="password123"):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        staff = Staff.objects.create(user=user, role="admin")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)

    return do_create


@pytest.fixture
def create_logged_in_owner(api_client):
    def do_create(username="owner", email="owner@test.com", password="password123"):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        staff = Staff.objects.create(user=user, role="owner")
        refresh = RefreshToken.for_user(staff.user)
        api_client.force_authenticate(user=staff.user)
        return staff, str(refresh), str(refresh.access_token)

    return do_create


@pytest.mark.django_db
class TestQuestionList:
    def test_question_list_by_candidate_fail(
        self, api_client, question_list_url, create_logged_in_screening_candidate
    ):
        _, _, access = create_logged_in_screening_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(question_list_url)
        assert response.status_code == 403

    def test_question_list_by_volunteer_fail(
        self, api_client, question_list_url, create_logged_in_volunteer
    ):
        _, _, access = create_logged_in_volunteer()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(question_list_url)
        assert response.status_code == 403

    def test_question_list_by_moderator_success(
        self, api_client, question_list_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(question_list_url)
        assert response.status_code == 200

    def test_question_list_by_admin_success(
        self, api_client, question_list_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(question_list_url)
        assert response.status_code == 200

    def test_question_list_by_owner_success(
        self, api_client, question_list_url, create_logged_in_owner
    ):
        _, _, access = create_logged_in_owner()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(question_list_url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestSetQuestion:
    def test_set_question_by_moderator_success(
        self, api_client, question_list_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        data = {
            "text": "How many Newton's laws of motion are there?",
            "option_a": "4",
            "option_b": "3",
            "option_c": "5",
            "option_d": "1",
            "correct_answer": "B",
            "difficulty": "easy",
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(question_list_url, data, format="json")
        assert response.status_code == 201

    def test_set_question_by_admin_success(
        self, api_client, question_list_url, create_logged_in_admin
    ):
        _, _, access = create_logged_in_admin()
        data = {
            "text": "How many Newton's laws of motion are there?",
            "option_a": "4",
            "option_b": "3",
            "option_c": "5",
            "option_d": "1",
            "correct_answer": "B",
            "difficulty": "easy",
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(question_list_url, data, format="json")
        assert response.status_code == 201

    def test_set_question_by_owner_success(
        self, api_client, question_list_url, create_logged_in_owner
    ):
        _, _, access = create_logged_in_owner()
        data = {
            "text": "How many Newton's laws of motion are there?",
            "option_a": "4",
            "option_b": "3",
            "option_c": "5",
            "option_d": "1",
            "correct_answer": "B",
            "difficulty": "easy",
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(question_list_url, data, format="json")
        assert response.status_code == 201


@pytest.mark.django_db
class TestQuestionDetail:
    def test_update_question_by_moderator_success(
        self, api_client, question_detail_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        data = {
            "text": "How many Newton's laws of motion are there?",
            "option_a": "4",
            "option_b": "3",
            "option_c": "5",
            "option_d": "1",
            "correct_answer": "B",
            "difficulty": "easy",
        }
        question = Question.objects.create(
            text=data["text"],
            option_a=data["option_a"],
            option_b=data["option_b"],
            option_c=data["option_c"],
            option_d=data["option_d"],
            correct_answer=data["correct_answer"],
            difficulty=data["difficulty"],
        )

        data2 = {"text": "What is 2 + 2?", "correct_answer": "A"}
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.patch(
            question_detail_url(question.id), data2, format="json"
        )
        assert response.status_code == 200

    def test_replace_question_by_moderator_success(
        self, api_client, question_detail_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        data = {
            "text": "How many Newton's laws of motion are there?",
            "option_a": "4",
            "option_b": "3",
            "option_c": "5",
            "option_d": "1",
            "correct_answer": "B",
            "difficulty": "easy",
        }
        question = Question.objects.create(
            text=data["text"],
            option_a=data["option_a"],
            option_b=data["option_b"],
            option_c=data["option_c"],
            option_d=data["option_d"],
            correct_answer=data["correct_answer"],
            difficulty=data["difficulty"],
        )

        data2 = {"text": "What is 2 + 2?", "correct_answer": "A"}
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.put(
            question_detail_url(question.id), data2, format="json"
        )
        assert response.status_code == 200

    def test_delete_question_by_moderator_success(
        self, api_client, question_detail_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        data = {
            "text": "How many Newton's laws of motion are there?",
            "option_a": "4",
            "option_b": "3",
            "option_c": "5",
            "option_d": "1",
            "correct_answer": "B",
            "difficulty": "easy",
        }
        question = Question.objects.create(
            text=data["text"],
            option_a=data["option_a"],
            option_b=data["option_b"],
            option_c=data["option_c"],
            option_d=data["option_d"],
            correct_answer=data["correct_answer"],
            difficulty=data["difficulty"],
        )
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.delete(question_detail_url(question.id))
        assert response.status_code == 200
        assert "Question deleted successfully" in response.data["message"]
