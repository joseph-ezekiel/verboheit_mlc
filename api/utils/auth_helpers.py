from rest_framework.response import Response
from rest_framework import status

def get_candidate_from_request(request):
    try:
        return request.user.candidate, None
    except Exception:
        return None, Response({'error': 'User is not a candidate'}, status=status.HTTP_404_NOT_FOUND)

def get_staff_from_request(request):
    try:
        return request.user.staff, None
    except Exception:
        return None, Response({'error': 'User is not a staff member'}, status=status.HTTP_404_NOT_FOUND)
