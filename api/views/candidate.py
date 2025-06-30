"""
API views specific to candidates.
"""
import logging

from django.db.models import Prefetch
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.settings import api_settings

from ..models import Candidate, CandidateScore
from ..permissions import StaffWithRole
from ..serializers import CandidateDetailSerializer, CandidateListSerializer
from ..utils.user import validate_role
from ..utils.query_filters import filter_candidates
from ..utils.helpers import get_candidate_with_scores

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def candidate_me_api(request):
    """
    Retrieve the authenticated candidate's own profile.

    Returns:
        200 OK with candidate data if the user is a candidate,
        403 FORBIDDEN otherwise.
    """
    try:
        candidate = request.user.candidate
        serializer = CandidateListSerializer(candidate)
        return Response(serializer.data)
    except AttributeError:
        return Response({"error": "Not a candidate"}, status=status.HTTP_403_FORBIDDEN)


class CandidateListView(ListAPIView):
    """
    List all candidates.

    Accessible by staff users with roles: moderator, admin, or owner.
    Supports pagination and query param filtering.
    """

    permission_classes = [
        IsAuthenticated,
        StaffWithRole(["moderator", "admin", "owner"]),
    ]
    serializer_class = CandidateListSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_queryset(self):
        """
        Returns a filtered queryset of candidates based on request query parameters.
        """
        return filter_candidates(Candidate.objects.all().order_by('-date_created'), self.request.query_params)


class CandidateDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific candidate profile.

    Only accessible to staff with 'owner' or 'admin' roles.
    """

    permission_classes = [IsAuthenticated, StaffWithRole(["owner", "admin"])]
    serializer_class = CandidateDetailSerializer
    queryset = Candidate.objects.all()
    lookup_url_kwarg = "candidate_id"

    def get_queryset(self):
        """
        Returns a queryset with prefetch optimization for candidate scores,
        including related exams and submitters.
        """
        return Candidate.objects.with_scores().prefetch_related(
            Prefetch(
                "scores",
                queryset=CandidateScore.objects.select_related("exam", "submitted_by"),
            )
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves candidate profile along with detailed score information.
        """
        candidate = self.get_object()
        return Response(get_candidate_with_scores(candidate))

    def perform_update(self, serializer) -> None:
        """
        Save updates to candidate and log the action.
        """
        logger.info(
            f"Updating candidate {serializer.instance.pk}",
            extra={"user": self.request.user.id},
        )
        serializer.save(updated_by=self.request.user.staff)

    def perform_destroy(self, instance) -> None:
        """
        Soft-delete staff by setting `is_active` to False.
        """
        logger.info(
            f"Soft-deleting candidate {instance.pk}", extra={"user": self.request.user.id}
        )
        instance.is_active = False
        instance.save()

class AssignCandidateRoleView(UpdateAPIView):
    """
    Assign a new role to a candidate.

    Only staff with 'owner' or 'admin' roles are permitted.
    """

    permission_classes = [IsAuthenticated, StaffWithRole(["owner", "admin"])]
    serializer_class = CandidateDetailSerializer
    queryset = Candidate.objects.all()
    lookup_url_kwarg = "candidate_id"
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        """
        Updates the role of the specified candidate.

        Returns:
            - 200 OK with updated candidate data if role is valid.
            - 400/403 response if invalid or unauthorized.
        """
        candidate = self.get_object()
        new_role = request.data.get("role")

        if error := validate_role(new_role, Candidate):
            return error

        candidate.role = new_role
        candidate.save()
        return Response(self.get_serializer(candidate).data)
