from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'candidate')

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'staff')

class StaffWithRole(BasePermission):
    """
    Custom permission to allow only specific staff roles.
    Use like: @permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
    """
    def __init__(self, roles):
        self.roles = roles

    def has_permission(self, request, view):
        return (
            hasattr(request.user, 'staff') and
            request.user.staff.role in self.roles
        )

    def __call__(self):
        return self

class IsOwnerOrStaff(BasePermission):
    """
    Object-level permission: owner or staff can access.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or hasattr(request.user, 'staff')

class IsLeagueCandidate(BasePermission):
    """
    League candidates only (used for leaderboard).
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'candidate') and request.user.candidate.role == 'league'

class IsLeagueCandidateOrStaff(BasePermission):
    def has_permission(self, request, view):
        return (IsLeagueCandidate().has_permission(request, view) or 
                StaffWithRole(['moderator', 'admin', 'owner'])().has_permission(request, view))
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
