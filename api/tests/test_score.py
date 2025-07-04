import pytest
from django.urls import reverse

from api.models import CandidateScore, Exam

@pytest.fixture
def submit_exam_score_url():
    def _dynamic_url(exam_id):
        return reverse("v1:api-submit-exam-score", kwargs={"exam_id": exam_id})
    return _dynamic_url
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