"""
API view for retrieving the leaderboard of league candidates.
"""

from django.db.models import Sum

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import Candidate, LeaderboardSnapshot
from ..serializers import MinimalCandidateSerializer
from ..permissions import IsLeagueCandidateOrStaff, StaffWithRole
from ..models import FeatureFlag


@api_view(["POST"])
@permission_classes([IsAuthenticated, StaffWithRole(["admin", "owner"])])
def publish_leaderboard(request):
    """
    Refreshes and publishes the leaderboard snapshot. Admin/Owner only.
    """
    staff = request.user.staff
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

    snapshot = LeaderboardSnapshot.objects.create(
        data=leaderboard,
        published_by=staff,
    )

    return Response(
        {"message": "Leaderboard published!", "published_at": snapshot.created_at}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsLeagueCandidateOrStaff])
def load_leaderboard_api(request):
    """
    Returns the most recently published leaderboard snapshot.
    """
    if not FeatureFlag.get_bool("leaderboard_open", default=True):
        return Response(
            {"detail": "Leaderboard is currently unavailable."}, status=status.HTTP_403_FORBIDDEN
        )
    snapshot = LeaderboardSnapshot.objects.order_by("-created_at").first()
    if not snapshot:
        return Response({"detail": "Leaderboard not published yet."}, status=404)
    return Response(snapshot.data)

@api_view(["POST"])
@permission_classes([StaffWithRole(["admin", "owner"])])
def toggle_leaderboard(request):
    """
    Toggle the leaderboard status for candidates and staff.

    Requires staff with 'admin' or 'owner' role.
    """
    open_flag = request.data.get("open", False)
    obj, created = FeatureFlag.objects.get_or_create(
        key="leaderboard_open",
        defaults={"value": open_flag}
    )
    if not created:
        obj.value = open_flag
        obj.save()
    return Response(
        {"message": f"leaderboard_open: {obj.value}"}
    )
        
    