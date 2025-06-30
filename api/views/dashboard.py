"""
Dashboard and account management views for candidates and staff members.
"""

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from ..utils.auth_helpers import get_candidate_from_request, get_staff_from_request
from ..permissions import StaffWithRole, IsCandidate, IsStaff
from ..serializers import (
    CandidateDetailSerializer,
    StaffDetailSerializer,
    User,
    UserSerializer,
)
from ..utils.dashboard_utils import (
    get_candidate_dashboard_data,
    get_staff_dashboard_data,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCandidate])
def candidate_dashboard_api(request):
    """
    Retrieve dashboard data for the currently authenticated candidate.

    Returns:
        JSON response with candidate-specific dashboard stats and profile data.
    """
    candidate, error_response = get_candidate_from_request(request)
    if error_response:
        return error_response

    data = get_candidate_dashboard_data(candidate)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, StaffWithRole(["moderator", "admin", "owner"])])
def staff_dashboard_api(request):
    """
    Retrieve dashboard data for the currently authenticated staff member.

    Returns:
        JSON response with staff-specific dashboard metrics and profile data.
    """
    staff, error_response = get_staff_from_request(request)
    if error_response:
        return error_response

    data = get_staff_dashboard_data(staff)
    return Response(data)


class AccountManagementView(APIView):
    """
    Retrieve or update user account and profile information.

    - GET: Retrieve account and profile information.
    - PUT/PATCH: Update account and profile.
    - DELETE not supported here (ownership check implied).

    Only users with `admin` or `owner` roles can manage other users' accounts.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        """
        Retrieve the account and profile data of the target user.

        If `user_id` is not provided, retrieves the current user's account data.

        Args:
            user_id (int, optional): ID of the user to fetch.

        Returns:
            JSON response with `user` and `profile` data.
        """
        user = self._get_target_user(request, user_id)
        if isinstance(user, Response):
            return user

        return Response(
            {
                "profile": self._get_user_profile_data(user),
            }
        )

    def put(self, request, user_id=None):
        """
        Fully update both user and profile data.

        Args:
            user_id (int, optional): ID of the user to update.

        Returns:
            JSON response with updated user and profile data.
        """
        return self._update_account(request, partial=False, user_id=user_id)

    def patch(self, request, user_id=None):
        """
        Partially update user and/or profile data.

        Args:
            user_id (int, optional): ID of the user to update.

        Returns:
            JSON response with updated user and profile data.
        """
        return self._update_account(request, partial=True, user_id=user_id)

    def _update_account(self, request, partial=False, user_id=None):
        """
        Handles the update logic for both user and profile data.

        Args:
            partial (bool): Whether the update is partial.
            user_id (int, optional): Target user ID.

        Returns:
            JSON response or error message.
        """
        user = self._get_target_user(request, user_id)
        if isinstance(user, Response):
            return user

        user_data = request.data.get("user", {})
        profile_data = request.data.get("profile", {})

        user_serializer = UserSerializer(user, data=user_data, partial=partial)
        profile_serializer = self._get_profile_serializer(user, profile_data, partial)

        if not user_serializer.is_valid():
            return Response(
                {"error": "Invalid user data", "details": user_serializer.errors},
                status=400,
            )
        if not profile_serializer or not profile_serializer.is_valid():
            return Response(
                {
                    "error": "Invalid profile data",
                    "details": getattr(profile_serializer, "errors", {}),
                },
                status=400,
            )

        user_serializer.save()
        profile_serializer.save()

        return Response(
            {
                "message": "Account updated successfully",
                "user": user_serializer.data,
                "profile": profile_serializer.data,
            }
        )

    def _get_target_user(self, request, user_id):
        """
        Get the target user for account actions.

        - If `user_id` is None or matches current user, return self.
        - Else, only staff with admin/owner role can manage others.

        Returns:
            User object or error Response.
        """
        if not user_id or user_id == request.user.id:
            return request.user

        if not hasattr(request.user, "staff") or request.user.staff.role not in [
            "admin",
            "owner",
        ]:
            return Response(
                {"error": "You are not authorized to manage other users."}, status=403
            )

        return get_object_or_404(User, id=user_id)

    def _get_user_profile_data(self, user):
        """
        Get serialized profile data for candidate or staff.

        Args:
            user (User): User instance.

        Returns:
            Dict or None: Serialized profile data.
        """
        try:
            if hasattr(user, "candidate"):
                return CandidateDetailSerializer(user.candidate).data
            if hasattr(user, "staff"):
                return StaffDetailSerializer(user.staff).data
        except Exception as e:
            print(f"Error serializing profile: {e}")
        return None

    def _get_profile_serializer(self, user, data, partial=False):
        """
        Return appropriate serializer for profile data.

        Args:
            user (User): Target user.
            data (dict): Profile data.
            partial (bool): Whether the update is partial.

        Returns:
            Serializer or None.
        """
        if hasattr(user, "candidate"):
            return CandidateDetailSerializer(user.candidate, data=data, partial=partial)
        if hasattr(user, "staff"):
            return StaffDetailSerializer(user.staff, data=data, partial=partial)
        return None
