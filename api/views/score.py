from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Candidate, CandidateScore, Exam
from ..serializers import CandidateScoreSerializer
from ..permissions import StaffWithRole

# === Get Candidate Score ===
@api_view(['GET'])
@permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
def candidate_scores_api(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    scores = CandidateScore.objects.filter(candidate=candidate)
    serializer = CandidateScoreSerializer(scores, many=True)
    return Response(serializer.data)

# === Submit Score ===
@api_view(['POST'])
@permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
def submit_score_api(request, exam_id):
    try:
        candidate_id = request.data.get("candidate_id")
        score = request.data.get("score")

        if candidate_id is None or score is None:
            return Response({"error": "candidate_id and score are required."}, status=400)

        candidate = get_object_or_404(Candidate, pk=candidate_id)
        exam = get_object_or_404(Exam, pk=exam_id)
        staff = request.user.staff

        # Create or update the score
        score_obj, created = CandidateScore.objects.update_or_create(
            candidate=candidate,
            exam=exam,
            defaults={
                'score': score,
                'submitted_by': staff,
            }
        )

        return Response({
            "message": "Score submitted." if created else "Score updated.",
            "data": {
                "candidate": candidate.user.get_full_name(),
                "exam": exam.title,
                "score": float(score)
            }
        })

    except AttributeError:
        return Response({"error": "Only staff users can submit scores."}, status=403)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
