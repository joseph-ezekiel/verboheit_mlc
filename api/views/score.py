"""
API views for retrieving and submitting candidate scores.
"""

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Candidate, CandidateScore, Exam
from ..serializers import CandidateScoreSerializer
from ..permissions import StaffWithRole


@api_view(["GET"])
@permission_classes([IsAuthenticated, StaffWithRole(["admin", "owner"])])
def candidate_scores_api(request, candidate_id):
    """
    Retrieve all scores for a given candidate.

    Args:
        candidate_id (int): ID of the candidate whose scores are to be fetched.

    Returns:
        200 OK with serialized score data.
        404 NOT FOUND if candidate does not exist.

    Permissions:
        - Only staff with 'admin' or 'owner' roles can access.
    """
    candidate = get_object_or_404(Candidate, id=candidate_id)
    scores = CandidateScore.objects.filter(candidate=candidate)
    serializer = CandidateScoreSerializer(scores, many=True)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, StaffWithRole(["admin", "owner"])])
def submit_exam_score_api(request, exam_id):
    """
    Submit or update a candidate's score for a specific exam.

    Expected PUT data:
        - candidate_id: ID of the candidate.
        - score: Score to submit or update.

    Args:
        exam_id (int): ID of the exam.

    Returns:
        200 OK with message and submitted score data.
        400 BAD REQUEST if required fields are missing or invalid.
        403 FORBIDDEN if user is not valid staff.

    Permissions:
        - Only staff with 'admin' or 'owner' roles can submit scores.
    """
    try:
        candidate_id = request.data.get("candidate_id")
        score = request.data.get("score")

        if candidate_id is None or score is None:
            return Response(
                {"error": "candidate_id and score are required."}, status=400
            )

        candidate = get_object_or_404(Candidate, pk=candidate_id)
        exam = get_object_or_404(Exam, pk=exam_id)
        staff = request.user.staff

        # Create or update the score
        _, created = CandidateScore.objects.update_or_create(
            candidate=candidate,
            exam=exam,
            defaults={"score": score, "submitted_by": staff, "auto_score": False},
        )

        return Response(
            {
                "message": "Score submitted." if created else "Score updated.",
                "data": {
                    "candidate": candidate.user.get_full_name(),
                    "exam": exam.title,
                    "score": float(score),
                },
            }
        )

    except AttributeError:
        return Response(
            {"error": "Only admin and owner staff members can submit scores."},
            status=403,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=400)
