import pytest
from django.urls import reverse

from api.models import Exam

@pytest.fixture
def exam_list_url():
    return reverse("v1:api-exam-list")

@pytest.fixture
def exam_detail_url():
    def _detail_url(exam_id):
        return reverse("v1:api-exam-detail", kwargs={"exam_id": exam_id})
    return _detail_url

@pytest.fixture
def exam_questions_url():
    def _questions_url(exam_id):
        return reverse("v1:api-exam-questions", kwargs={"exam_id": exam_id})
    return _questions_url

@pytest.fixture
def take_exam_url():
    def _take_exam_url(exam_id):
        return reverse("v1:api-take-exam", kwargs={"exam_id": exam_id})
    return _take_exam_url

@pytest.mark.django_db
class TestExamList:
    def test_exam_list_by_candidate_fail(self, api_client, exam_list_url, create_logged_in_screening_candidate):
        _, _, access = create_logged_in_screening_candidate()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(exam_list_url)
        assert response.status_code == 403

    def test_exam_list_by_volunteer_fail(self, api_client, exam_list_url, create_logged_in_volunteer):
        _, _, access = create_logged_in_volunteer()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(exam_list_url)
        assert response.status_code == 403

    def test_exam_list_by_moderator_fail(self, api_client, exam_list_url, create_logged_in_moderator):
        _, _, access = create_logged_in_moderator()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(exam_list_url)
        assert response.status_code == 403

    def test_exam_list_by_admin_success(self, api_client, exam_list_url, create_logged_in_admin):
        _, _, access = create_logged_in_admin()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(exam_list_url)
        assert response.status_code == 200

    def test_exam_list_by_owner_success(self, api_client, exam_list_url, create_logged_in_owner):
        _, _, access = create_logged_in_owner()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(exam_list_url)
        assert response.status_code == 200

@pytest.mark.django_db
class TestSetExam:
    def test_set_exam_by_moderator_fail(self, api_client, exam_list_url, create_logged_in_moderator):
        staff, _, access = create_logged_in_moderator()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": 12,
            "countdown_minutes": 60,
            "questions": []
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(exam_list_url, data, format="json")
        assert response.status_code == 403

    def test_set_exam_by_admin_success(self, api_client, exam_list_url, create_logged_in_admin):
        staff, _, access = create_logged_in_admin()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": 12,
            "countdown_minutes": 60,
            "questions": []
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(exam_list_url, data, format="json")
        assert response.status_code == 201

    def test_set_exam_by_owner_success(self, api_client, exam_list_url, create_logged_in_owner):
        staff, _, access = create_logged_in_owner()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
            "questions": []
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(exam_list_url, data, format="json")
        assert response.status_code == 201

@pytest.mark.django_db
class TestExamDetail:
    def test_update_exam_by_admin_success(self, api_client, exam_detail_url, create_logged_in_admin):
        staff, _, access = create_logged_in_admin()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": "2",
            "countdown_minutes": "60",
            "created_by": staff
        }
        exam = Exam.objects.create(**data)
        update_data = {
            "stage": "screening",
            "title": "Exam",
            "updated_by": staff.pk
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.patch(exam_detail_url(exam.id), update_data, format="json")
        assert response.status_code == 200

    def test_replace_exam_by_admin_success(self, api_client, exam_detail_url, create_logged_in_admin):
        staff, _, access = create_logged_in_admin()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
            "created_by": staff,
        }
        exam = Exam.objects.create(**data)
        replace_data = {
            "stage": "screening",
            "title": "Week 2",
            "description": "The second of six weeks of league competition",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
            "questions": []
        }
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.put(exam_detail_url(exam.id), replace_data, format="json")
        assert response.status_code == 200

    def test_delete_exam_by_admin_success(self, api_client, exam_detail_url, create_logged_in_admin):
        staff, _, access = create_logged_in_admin()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": "2",
            "countdown_minutes": "60",
            "created_by": staff
        }
        exam = Exam.objects.create(**data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.delete(exam_detail_url(exam.id))
        assert response.status_code in [200, 204]

@pytest.mark.django_db
class TestExamQuestions:
    def test_list_exam_questions_by_candidate_fail(
        self, api_client, exam_questions_url, create_logged_in_screening_candidate
    ):
        _, _, access = create_logged_in_screening_candidate()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": "2",
            "countdown_minutes": "60",
        }
        exam = Exam.objects.create(**data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        exam = Exam.objects.create()
        response = api_client.get(exam_questions_url(exam.id))
        assert response.status_code == 403

    def test_list_exam_questions_by_moderator_fail(
        self, api_client, exam_questions_url, create_logged_in_moderator
    ):
        _, _, access = create_logged_in_moderator()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": "2",
            "countdown_minutes": "60",
        }
        exam = Exam.objects.create(**data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        exam = Exam.objects.create()
        response = api_client.get(exam_questions_url(exam.id))
        assert response.status_code == 403

    def test_list_exam_questions_by_admin_success(
        self, api_client, exam_questions_url, create_logged_in_admin
    ):
        staff, _, access = create_logged_in_admin()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": "2",
            "countdown_minutes": "60",
        }
        exam = Exam.objects.create(**data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        exam = Exam.objects.create()
        response = api_client.get(exam_questions_url(exam.id))
        assert response.status_code == 200
    
    def test_list_exam_questions_by_owner_success(
        self, api_client, exam_questions_url, create_logged_in_owner
    ):
        staff, _, access = create_logged_in_owner()
        data = {
            "stage": "league",
            "title": "League Competition Week 1",
            "description": "The first of six weeks of league competition?",
            "is_active": True,
            "open_duration_hours": "2",
            "countdown_minutes": "60",
        }
        exam = Exam.objects.create(**data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        exam = Exam.objects.create()
        response = api_client.get(exam_questions_url(exam.id))
        assert response.status_code == 200

@pytest.mark.django_db
class TestCandidateTakeExam:
    def test_take_exam_by_screening_candidate_success(
        self, api_client, take_exam_url, create_logged_in_screening_candidate
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
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(take_exam_url(exam.id))
        assert response.status_code == 200

    def test_take_exam_by_screening_candidate_fail(
        self, api_client, take_exam_url, create_logged_in_screening_candidate
    ):
        candidate, _, access = create_logged_in_screening_candidate()
        exam_data = {
            "stage": "league",
            "title": "League Exam",
            "description": "League exam",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
        }
        exam = Exam.objects.create(**exam_data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(take_exam_url(exam.id))
        assert response.status_code == 403

    def test_take_exam_by_league_candidate_success(
        self, api_client, take_exam_url, create_logged_in_league_candidate
    ):
        candidate, _, access = create_logged_in_league_candidate()
        exam_data = {
            "stage": "league",
            "title": "League Exam",
            "description": "League exam",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
        }
        exam = Exam.objects.create(**exam_data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(take_exam_url(exam.id))
        assert response.status_code == 200
    
    def test_take_exam_by_league_candidate_fail(
        self, api_client, take_exam_url, create_logged_in_league_candidate
    ):
        candidate, _, access = create_logged_in_league_candidate()
        exam_data = {
            "stage": "screening",
            "title": "Screening Exam",
            "description": "Screening exam",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
        }
        exam = Exam.objects.create(**exam_data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(take_exam_url(exam.id))
        assert response.status_code == 403
    
    def test_take_exam_by_staff_fail(
        self, api_client, take_exam_url, create_logged_in_moderator
    ):
        staff, _, access = create_logged_in_moderator()
        exam_data = {
            "stage": "league",
            "title": "League Exam",
            "description": "League exam",
            "is_active": True,
            "open_duration_hours": 2,
            "countdown_minutes": 60,
        }
        exam = Exam.objects.create(**exam_data)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(take_exam_url(exam.id))
        assert response.status_code == 403