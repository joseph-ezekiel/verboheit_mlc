from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Candidate, CandidateScore
from ..serializers import CandidateScoreSerializer
from ..permissions import StaffWithRole

@api_view(['GET'])
@permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
def candidate_scores_api(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    scores = CandidateScore.objects.filter(candidate=candidate)
    serializer = CandidateScoreSerializer(scores, many=True)
    return Response(serializer.data)
