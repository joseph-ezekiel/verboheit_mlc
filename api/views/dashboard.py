from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..utils.auth_helpers import get_candidate_from_request, get_staff_from_request
from ..utils.dashboard_utils import get_candidate_dashboard_data, get_staff_dashboard_data
from ..permissions import StaffWithRole

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