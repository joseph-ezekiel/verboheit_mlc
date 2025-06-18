from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.reverse import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.decorators.cache import cache_page

from ..serializers import (
    CandidateRegistrationSerializer,
    StaffRegistrationSerializer,
    UserSerializer
)

# === API ROOT ===
@cache_page(60 * 15)  # 15 minutes cache
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, version='v1', format=None):
    """API entry point with discoverable endpoints"""
    
    # Helper to generate URL with placeholder
    def dynamic_url(name, placeholder, param):
        try:
            url = reverse(name, kwargs={param: 0}, request=request, format=format, version=version)
            return url.replace("0", placeholder)
        except NoReverseMatch:
            return None
    
    # Helper to safely generate URLs
    def safe_url(name, **kwargs):
        try:
            return reverse(name, request=request, format=format, version=version, **kwargs)
        except NoReverseMatch:
            return None
    
    # Organized resource structure
    resources = {
        "authentication": {
            "login": safe_url('api-login'),
            "register": {
                "candidate": safe_url('api-register-candidate'),
                "staff": safe_url('api-register-staff'),
            },
            "token": {
                "obtain": safe_url('token-obtain-pair'),
                "refresh": safe_url('token-refresh'),
            }
        },
        "candidates": {
            "collection": safe_url('api-candidate-list'),
            "me": safe_url('api-candidate-me'),
            "detail": dynamic_url('api-candidate-detail', "<candidate_id>", "candidate_id"),
            "actions": {
                "assign_role": dynamic_url('api-candidate-role-assign', "<candidate_id>", "candidate_id"),
                "scores": dynamic_url('api-candidate-scores', "<candidate_id>", "candidate_id"),
                "exam_history": dynamic_url('api-candidate-exam-history', "<candidate_id>", "candidate_id"),
            }
        },
        "staff": {
            "collection": safe_url('api-staff-list'),
            "me": safe_url('api-staff-me'),
            "detail": dynamic_url('api-staff-detail', "<staff_id>", "staff_id"),
            "actions": {
                "assign_role": dynamic_url('api-staff-role-assign', "<staff_id>", "staff_id"),
            }
        },
        "exams": {
            "collection": safe_url('api-exam-list'),
            "detail": dynamic_url('api-exam-detail', "<exam_id>", "exam_id"),
            "questions": dynamic_url('api-exam-questions', "<exam_id>", "exam_id"),
            "scores": {
                "submit": dynamic_url('api-exam-score-submit', "<exam_id>", "exam_id"),
            }
        },
        "questions": {
            "collection": safe_url('api-question-list'),
            "detail": dynamic_url('api-question-detail', "<question_id>", "question_id"),
        },
        "dashboard": {
            "candidate": safe_url('api-candidate-dashboard'),
            "staff": safe_url('api-staff-dashboard'),
        },
        "leaderboard": safe_url('api-leaderboard'),
    }
    
    # Remove any None values (unresolved URLs)
    def clean_none(obj):
        if isinstance(obj, dict):
            return {k: clean_none(v) for k, v in obj.items() if v is not None}
        return obj
    
    return Response({
        "VML_competition_api": {
            "version": version,  # Dynamic version from request
            "documentation": "https://api.example.com/docs/",
            "resources": clean_none(resources)
        }
    })

# ========== REGISTER ==========
@api_view(['POST'])
@permission_classes([AllowAny])
def register_candidate_api(request):
    serializer = CandidateRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_staff_api(request):
    serializer = StaffRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== LOGIN ==========

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# ========== ACCOUNT INFO ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_info_api(request):
    user_data = UserSerializer(request.user).data
    role_data = None

    try:
        if hasattr(request.user, 'candidate'):
            from ..serializers import CandidateDetailSerializer
            role_data = CandidateDetailSerializer(request.user.candidate).data
        elif hasattr(request.user, 'staff'):
            from ..serializers import StaffDetailSerializer
            role_data = StaffDetailSerializer(request.user.staff).data
    except Exception:
        pass

    return Response({
        'user': user_data,
        'profile': role_data
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_account_info_api(request):
    user_serializer = UserSerializer(request.user, data=request.data.get('user', {}), partial=True)
    
    if user_serializer.is_valid():
        user_serializer.save()
    else:
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    role_data = request.data.get('role', {})
    if hasattr(request.user, 'candidate'):
        from ..serializers import CandidateDetailSerializer
        role_serializer = CandidateDetailSerializer(request.user.candidate, data=role_data, partial=True)
    elif hasattr(request.user, 'staff'):
        from ..serializers import StaffDetailSerializer
        role_serializer = StaffDetailSerializer(request.user.staff, data=role_data, partial=True)
    else:
        return Response({'error': 'User has no associated profile'}, status=status.HTTP_400_BAD_REQUEST)

    if role_serializer.is_valid():
        role_serializer.save()
        return Response({
            'user': user_serializer.data,
            'profile': role_serializer.data
        })
    return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)