from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..serializers import CandidateDetailSerializer, StaffDetailSerializer, User, UserSerializer

from ..utils.auth_helpers import get_candidate_from_request, get_staff_from_request
from ..utils.dashboard_utils import get_candidate_dashboard_data, get_staff_dashboard_data
from ..permissions import StaffWithRole

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView

# ========== DASHBOARD ==========
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def candidate_dashboard_api(request):
    candidate, error_response = get_candidate_from_request(request)
    if error_response:
        return error_response

    data = get_candidate_dashboard_data(candidate)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, StaffWithRole(['moderator', 'admin', 'owner'])])
def staff_dashboard_api(request):
    staff, error_response = get_staff_from_request(request)
    if error_response:
        return error_response

    data = get_staff_dashboard_data(staff)
    return Response(data)

# ========== ACCOUNT MANAGEMENT ==========
class AccountManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        user = self._get_target_user(request, user_id)
        if isinstance(user, Response):  # early return if permission denied
            return user

        return Response({
            'user': UserSerializer(user).data,
            'profile': self._get_user_profile_data(user)
        })

    def put(self, request, user_id=None):
        return self._update_account(request, partial=False, user_id=user_id)

    def patch(self, request, user_id=None):
        return self._update_account(request, partial=True, user_id=user_id)

    def _update_account(self, request, partial=False, user_id=None):
        user = self._get_target_user(request, user_id)
        if isinstance(user, Response):
            return user

        user_data = request.data.get('user', {})
        profile_data = request.data.get('profile', {})

        user_serializer = UserSerializer(user, data=user_data, partial=partial)
        profile_serializer = self._get_profile_serializer(user, profile_data, partial)

        if not user_serializer.is_valid():
            return Response({'error': 'Invalid user data', 'details': user_serializer.errors}, status=400)
        if not profile_serializer or not profile_serializer.is_valid():
            return Response({'error': 'Invalid profile data', 'details': getattr(profile_serializer, 'errors', {})}, status=400)

        user_serializer.save()
        profile_serializer.save()

        return Response({
            'message': 'Account updated successfully',
            'user': user_serializer.data,
            'profile': profile_serializer.data
        })

    def _get_target_user(self, request, user_id):
        if not user_id or user_id == request.user.id:
            return request.user

        # Allow only admins and owners to access other users' accounts
        if not hasattr(request.user, 'staff') or request.user.staff.role not in ['admin', 'owner']:
            return Response({'error': 'You are not authorized to manage other users.'}, status=403)

        return get_object_or_404(User, id=user_id)

    def _get_user_profile_data(self, user):
        try:
            if hasattr(user, 'candidate'):
                return CandidateDetailSerializer(user.candidate).data
            elif hasattr(user, 'staff'):
                return StaffDetailSerializer(user.staff).data
        except Exception:
            pass
        return None

    def _get_profile_serializer(self, user, data, partial=False):
        if hasattr(user, 'candidate'):
            return CandidateDetailSerializer(user.candidate, data=data, partial=partial)
        elif hasattr(user, 'staff'):
            return StaffDetailSerializer(user.staff, data=data, partial=partial)
        return None