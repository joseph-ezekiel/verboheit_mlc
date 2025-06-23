"""
Authentication-related API views for login, logout, and registration.
"""

import logging

from django.contrib.auth import authenticate
from django.urls.exceptions import NoReverseMatch
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers import (
    CandidateRegistrationSerializer,
    StaffRegistrationSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


# === API ROOT ===
@cache_page(60 * 15)  # 15 minutes cache
@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request, response_format=None):
    """API entry point with discoverable endpoints"""

    def generate_url_with_placeholder(name, placeholder, param):
        """Generate URL with placeholder for dynamic endpoints"""
        try:
            dummy_id = 99999
            url = reverse(
                name,
                kwargs={param: dummy_id},
                request=request,
                response_format=response_format,
            )
            return url.replace(str(dummy_id), placeholder)
        except NoReverseMatch:
            return None

    def safe_reverse(name, **kwargs):
        """Safely generate URLs, return None if route doesn't exist"""
        try:
            return reverse(
                name, request=request, response_format=response_format, **kwargs
            )
        except NoReverseMatch:
            return None

    return Response(
        {
            "authentication": {
                "login": safe_reverse("v1:api-login"),
                "logout": safe_reverse("v1:api-logout"),
                "register": {
                    "candidate": safe_reverse("v1:api-register-candidate"),
                    "staff": safe_reverse("v1:api-register-staff"),
                },
                "token": {
                    "obtain": safe_reverse("v1:token-obtain-pair"),
                    "refresh": safe_reverse("v1:token-refresh"),
                },
            },
            "candidates": {
                "collection": safe_reverse("v1:api-candidate-list"),
                "me": safe_reverse("v1:api-candidate-me"),
                "detail": generate_url_with_placeholder(
                    "v1:api-candidate-detail", "<candidate_id>", "candidate_id"
                ),
                "actions": {
                    "assign_role": generate_url_with_placeholder(
                        "v1:api-candidate-role-assign", "<candidate_id>", "candidate_id"
                    ),
                    "scores": generate_url_with_placeholder(
                        "v1:api-candidate-scores", "<candidate_id>", "candidate_id"
                    ),
                    "exam_history": generate_url_with_placeholder(
                        "v1:api-candidate-exam-history",
                        "<candidate_id>",
                        "candidate_id",
                    ),
                },
            },
            "staff": {
                "collection": safe_reverse("v1:api-staff-list"),
                "me": safe_reverse("v1:api-staff-me"),
                "detail": generate_url_with_placeholder(
                    "v1:api-staff-detail", "<staff_id>", "staff_id"
                ),
                "actions": {
                    "assign_role": generate_url_with_placeholder(
                        "v1:api-staff-role-assign", "<staff_id>", "staff_id"
                    ),
                },
            },
            "exams": {
                "collection": safe_reverse("v1:api-exam-list"),
                "detail": generate_url_with_placeholder(
                    "v1:api-exam-detail", "<exam_id>", "exam_id"
                ),
                "questions": generate_url_with_placeholder(
                    "v1:api-exam-questions", "<exam_id>", "exam_id"
                ),
                "scores": {
                    "submit": generate_url_with_placeholder(
                        "v1:api-exam-score-submit", "<exam_id>", "exam_id"
                    ),
                },
            },
            "questions": {
                "collection": safe_reverse("v1:api-question-list"),
                "detail": generate_url_with_placeholder(
                    "v1:api-question-detail", "<question_id>", "question_id"
                ),
            },
            "dashboard": {
                "candidate": safe_reverse("v1:api-candidate-dashboard"),
                "staff": safe_reverse("v1:api-staff-dashboard"),
            },
            "user_accounts": {
                "account-management": safe_reverse("v1:api-account-management"),
                "account-management-detail": generate_url_with_placeholder(
                    "v1:api-account-management-detail", "<user_id>", "user_id"
                ),
            },
            "leaderboard": safe_reverse("v1:api-leaderboard"),
        }
    )


class BaseRegistrationView(CreateAPIView):
    """Base registration view with common logic"""

    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Registration successful", "user_id": user.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": "Registration failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CandidateRegistrationView(BaseRegistrationView):
    """Register a new candidate"""

    serializer_class = CandidateRegistrationSerializer


class StaffRegistrationView(BaseRegistrationView):
    """Register a new staff member"""

    serializer_class = StaffRegistrationSerializer


class LoginRateThrottle(AnonRateThrottle):
    """Throttle class for limiting anonymous login attempts."""

    scope = "login"


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_api(request):
    """Authenticate user and return tokens + user info"""
    # Input validation
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(username) < 3:
        return Response(
            {"error": "Username must be at least 3 characters long"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)

    if user is not None:
        if not user.is_active:
            return Response(
                {"error": "Account is deactivated"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Determine user type and route
        user_type = None
        user_route = None

        try:
            if hasattr(user, "candidate"):
                user_type = "candidate"
                user_route = reverse("v1:api-candidate-me", request=request)
            elif hasattr(user, "staff"):
                user_type = "staff"
                user_route = reverse("v1:api-staff-me", request=request)
        except NoReverseMatch:
            # Handle case where routes don't exist
            user_route = None

        logger.info("User %s logged in successfully as %s", username, user_type)

        return Response(
            {
                "message": "Login successful",
                "tokens": {"access": str(access_token), "refresh": str(refresh)},
                "user": UserSerializer(user).data,
                "user_type": user_type,
                "user_route": user_route,
            },
            status=status.HTTP_200_OK,
        )

    logger.warning("Failed login attempt for username: %s", username)
    return Response(
        {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """
    Logout user by blacklisting the refresh token
    Client should send refresh token in request body
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()

        logger.info("User %s logged out successfully", request.user.username)

        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

    except TokenError as e:
        logger.warning(
            "Token error during logout for user %s: %s", request.user.username, str(e)
        )
        return Response(
            {"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST
        )

    except InvalidToken as e:
        logger.warning(
            "Invalid token during logout for user %s: %s", request.user.username, str(e)
        )
        return Response(
            {"error": "Invalid token format"}, status=status.HTTP_400_BAD_REQUEST
        )

    except Exception:
        logger.error(
            "Unexpected error during logout for user %s",
            request.user.username,
            exc_info=True,
            extra={"action": "logout"},
        )
        return Response(
            {"error": "Logout failed due to server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
