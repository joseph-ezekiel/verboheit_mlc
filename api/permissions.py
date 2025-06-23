"""
Custom DRF permission classes for fine-grained access control.

Includes role-based access (e.g., staff, candidate, league-specific),
object-level access, and read-only constraints.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCandidate(BasePermission):
    """
    Grants access if the authenticated user has a related Candidate profile.
    """

    def has_permission(self, request, view):
        return hasattr(request.user, "candidate")


class IsStaff(BasePermission):
    """
    Grants access if the authenticated user has a related Staff profile.
    """

    def has_permission(self, request, view):
        return hasattr(request.user, "staff")


class StaffWithRole(BasePermission):
    """
    Grants access to staff users with specific roles.

    Example:
        @permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])

    Args:
        roles (list[str]): List of allowed staff roles (e.g., ['admin', 'owner']).
    """

    def __init__(self, roles):
        self.roles = roles

    def has_permission(self, request, view):
        return hasattr(request.user, "staff") and request.user.staff.role in self.roles

    def __call__(self):
        # Makes this class usable as a decorator argument
        return self


class IsOwnerOrStaff(BasePermission):
    """
    Object-level permission: grants access if the user is the object's owner (obj.user)
    or has a staff profile.
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or hasattr(request.user, "staff")


class IsLeagueCandidate(BasePermission):
    """
    Grants access only to candidates whose role is 'league'.
    Useful for league-restricted actions like viewing the leaderboard.
    """

    def has_permission(self, request, view):
        return (
            hasattr(request.user, "candidate")
            and request.user.candidate.role == "league"
        )


class IsLeagueCandidateOrStaff(BasePermission):
    """
    Grants access if the user is a league candidate or a staff with elevated role.
    Combines `IsLeagueCandidate` and `StaffWithRole(['moderator', 'admin', 'owner'])`.
    """

    def has_permission(self, request, view):
        return IsLeagueCandidate().has_permission(request, view) or StaffWithRole(
            ["moderator", "admin", "owner"]
        )().has_permission(request, view)


class ReadOnly(BasePermission):
    """
    Grants access only for safe methods (GET, HEAD, OPTIONS).
    Blocks POST, PUT, PATCH, DELETE.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
