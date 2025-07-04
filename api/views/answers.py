"""
Docstring...
"""

from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..utils.helpers import auto_score
from ..serializers import CandidateAnswerBulkSerializer
from ..permissions import IsCandidate
from ..models import (
    Exam,
    Question,
    CandidateScore,
    CandidateAnswer,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsCandidate])
def submit_exam_answers(request, exam_id):
    """
    Candidate submits answers for an exam.
    """
    try:
        candidate = request.user.candidate
        exam = Exam.objects.get(pk=exam_id)
    except (Exam.DoesNotExist, AttributeError):
        return Response(
            {"error": "Invalid exam or candidate."}, status=status.HTTP_400_BAD_REQUEST
        )

    candidate_score, _ = CandidateScore.objects.get_or_create(
        candidate=candidate,
        exam=exam,
    )

    if CandidateAnswer.objects.filter(candidate_score=candidate_score).exists():
        return Response(
            {"message": "You have already submitted answers for this exam."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = CandidateAnswerBulkSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    answers_data = serializer.validated_data["answers"]

    for answer_data in answers_data:
        question_obj = answer_data["question"]
        selected_option = answer_data["selected_option"]

        CandidateAnswer.objects.create(
            candidate_score=candidate_score,
            question=question_obj,
            selected_option=selected_option,
        )

    auto_score(candidate_score)

    return Response(
        {
            "message": "Answers submitted!",
        },
        status=status.HTTP_200_OK,
    )
