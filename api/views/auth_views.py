from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..serializers import (
    CandidateRegistrationSerializer,
    StaffRegistrationSerializer,
    UserSerializer
)

# ========== LANDING ROUTE ==========

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        "auth_login": "/api/auth/login/",
        "register_candidate": "/api/auth/register/candidate/",
        "register_staff": "/api/auth/register/staff/",
        "candidates": "/api/candidates/",
        "staff": "/api/staff/",
        "exams": "/api/exams/",
        "questions": "/api/questions/",
        "leaderboard": "/api/leaderboard/",
        "dashboard_candidate": "/api/dashboard/candidate/",
        "dashboard_staff": "/api/dashboard/staff/",
    })

# ========== REGISTER ==========

@api_view(['POST'])
@permission_classes([AllowAny])
def register_candidate_api(request):
    serializer = CandidateRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        candidate = serializer.save()
        return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_staff_api(request):
    serializer = StaffRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        staff = serializer.save()
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