"""
Authentication-related API views for login, logout, and registration.
"""

import logging

from django.contrib.auth import authenticate
from django.urls.exceptions import NoReverseMatch

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_api_key.permissions import HasAPIKey # type: ignore

from ..serializers import (
    UserSerializer,
)


logger = logging.getLogger(__name__)

class LoginRateThrottle(SimpleRateThrottle):
    """Throttle for login attempts to prevent brute force attacks."""

    scope = "login"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return self.cache_format % {
                "scope": self.scope,
                "ident": request.user.pk
            }
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request)
        }

@api_view(["POST"])
@permission_classes([HasAPIKey])
@throttle_classes([LoginRateThrottle])
def login_api(request):
    """Authenticate user and return tokens + user info"""

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
