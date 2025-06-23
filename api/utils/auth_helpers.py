"""
Utility functions for retrieving candidate or staff instances
from the authenticated request user.
"""

from rest_framework.response import Response
from rest_framework import status


def get_candidate_from_request(request):
    """
    Attempts to retrieve the candidate instance linked to the authenticated user.

    Args:
        request (HttpRequest): The HTTP request object containing the user.

    Returns:
        Tuple:
            - candidate (Candidate | None): The candidate instance if found, else None.
            - error_response (Response | None): An error Response if user is not a candidate, else None.
    """
    try:
        return request.user.candidate, None
    except Exception:
        return None, Response(
            {"error": "User is not a candidate"}, status=status.HTTP_404_NOT_FOUND
        )


def get_staff_from_request(request):
    """
    Attempts to retrieve the staff instance linked to the authenticated user.

    Args:
        request (HttpRequest): The HTTP request object containing the user.

    Returns:
        Tuple:
            - staff (Staff | None): The staff instance if found, else None.
            - error_response (Response | None): An error Response if user is not a staff member, else None.
    """
    try:
        return request.user.staff, None
    except Exception:
        return None, Response(
            {"error": "User is not a staff member"}, status=status.HTTP_404_NOT_FOUND
        )
