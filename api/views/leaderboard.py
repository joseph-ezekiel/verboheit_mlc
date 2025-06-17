from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

from ..models import Candidate
from ..serializers import CandidateListSerializer
from ..permissions import IsLeagueCandidateOrStaff

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLeagueCandidateOrStaff])
def leaderboard_api(request):
    league_candidates = Candidate.candidates_by_role('league').annotate(
        total_score=Sum('candidatescore__score')
    ).order_by('-total_score')

    leaderboard = [
        {
            'candidate': CandidateListSerializer(candidate).data,
            'total_score': candidate.total_score or 0
        }
        for candidate in league_candidates
    ]

    return Response(leaderboard)