"""
API views for managing staff users, including profile retrieval,
listing, updating, deletion, and role assignment.
"""

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.settings import api_settings
from django.shortcuts import get_object_or_404

from ..models import Staff
from ..permissions import StaffWithRole, IsStaff
from ..serializers import StaffDetailSerializer, StaffListSerializer
from ..utils.user import handle_update_delete, validate_role
from ..utils.query_filters import filter_staffs
from ..utils.pagination_helpers import paginate_queryset

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStaff])
def staff_me_api(request):
    """
    Retrieve the authenticated staff member's own profile.

    Returns:
        200 OK with staff data if the user is a staff member.
        403 FORBIDDEN if user is not a staff member.
    """
    try:
        staff = request.user.staff
        serializer = StaffListSerializer(staff)
        return Response(serializer.data)
    except AttributeError:
        return Response(
            {"error": "Not a staff member"}, status=status.HTTP_403_FORBIDDEN
        )


class StaffListView(ListAPIView):
    """
    List all staff members with pagination and optional filtering.

    Permissions:
        - Only accessible to users with roles: moderator, admin, or owner.
    """

    permission_classes = [
        IsAuthenticated,
        StaffWithRole(["moderator", "admin", "owner"]),
    ]
    serializer_class = StaffDetailSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_queryset(self):
        """
        Apply query filters to the staff queryset.

        Returns:
            Filtered queryset of staff members.
        """
        return filter_staffs(Staff.objects.all().order_by('-date_created'), self.request.query_params)


class StaffDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or deactivate a specific staff member.

    Only owners are allowed to access this endpoint.

    - GET: Retrieve staff details.
    - PUT/PATCH: Update staff profile.
    - DELETE: Soft delete the staff (marks as inactive).
    """

    permission_classes = [IsAuthenticated, StaffWithRole(["owner"])]
    serializer_class = StaffDetailSerializer
    queryset = Staff.objects.all()
    lookup_url_kwarg = "staff_id"

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Return staff member's serialized data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer) -> None:
        """
        Save updates to staff member and log the action.
        """
        logger.info(
            f"Updating staff {serializer.instance.pk}",
            extra={"user": self.request.user.id},
        )
        serializer.save(updated_by=self.request.user.staff)

    def perform_destroy(self, instance) -> None:
        """
        Soft-delete staff by setting `is_active` to False.
        """
        logger.info(
            f"Soft-deleting staff {instance.pk}", extra={"user": self.request.user.id}
        )
        instance.is_active = False
        instance.save()


class AssignStaffRoleView(UpdateAPIView):
    """
    Assign a new role to a staff member.

    - Only owners can change roles.
    - Only accepts PUT requests.
    """

    permission_classes = [IsAuthenticated, StaffWithRole(["owner"])]
    serializer_class = StaffDetailSerializer
    queryset = Staff.objects.all()
    lookup_url_kwarg = "staff_id"
    http_method_names = ["put"]  # Restrict to PUT only

    def update(self, request, *args, **kwargs):
        """
        Update the role of a staff member.

        Returns:
            200 OK with updated staff data.
            400 BAD REQUEST if the role is invalid.
        """
        staff = self.get_object()
        new_role = request.data.get("role")

        if error := validate_role(new_role, Staff):
            return error

        staff.role = new_role
        staff.save()
        return Response(self.get_serializer(staff).data)
