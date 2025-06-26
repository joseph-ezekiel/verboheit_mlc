"""
API view for retrieving the leaderboard of league candidates.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

from ..models import Candidate
from ..serializers import MinimalCandidateSerializer
from ..permissions import IsLeagueCandidateOrStaff


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsLeagueCandidateOrStaff])
def leaderboard_api(request):
    """
    Retrieve the leaderboard of league candidates based on total scores.

    - Accessible by league candidates and staff.
    - Calculates the total score for each league candidate by summing their exam scores.
    - Returns a list ordered by descending total score.

    Returns:
        200 OK with a list of candidates and their total scores.
    """
    league_candidates = (
        Candidate.candidates_by_role("league")
        .annotate(total_score=Sum("scores__score"))
        .order_by("-total_score")
    )

    leaderboard = [
        {
            "candidate": MinimalCandidateSerializer(candidate).data,
            "total_score": candidate.total_score or 0,
        }
        for candidate in league_candidates
    ]

    return Response(leaderboard)
