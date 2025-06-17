from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.reverse import reverse


from ..serializers import (
    CandidateRegistrationSerializer,
    StaffRegistrationSerializer,
    UserSerializer
)

# === API ROOT ===
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        "auth": {
            "login": reverse('api_login', request=request, format=format),
            "register_candidate": reverse('api_register_candidate', request=request, format=format),
            "register_staff": reverse('api_register_staff', request=request, format=format),
            "token_obtain_pair": reverse('token_obtain_pair', request=request, format=format),
            "token_refresh": reverse('token_refresh', request=request, format=format),
        },
        "candidates": {
            "list": reverse('api_candidate_list', request=request, format=format),
            "detail": "/api/candidates/<candidate_id>/",
            "assign_role": "/api/candidates/<candidate_id>/assign-role/",
            "scores": "/api/candidates/<candidate_id>/scores/",
            "me": reverse('api_candidate_me', request=request, format=format),
            "exam_history": "/api/candidates/<candidate_id>/exam-history/",
        },
        "staff": {
            "list": reverse('api_staff_list', request=request, format=format),
            "detail": "/api/staff/<staff_id>/",
            "me": reverse('api_staff_me', request=request, format=format),
        },
        "exams": {
            "list": reverse('api_exam_list', request=request, format=format),
            "detail": "/api/exams/<exam_id>/",
            "questions": "/api/exams/<exam_id>/questions/",
            "submit_score": "/api/exams/<exam_id>/submit-score/",
        },
        "questions": {
            "list": reverse('api_question_list', request=request, format=format),
            "detail": "/api/questions/<question_id>/",
        },
        "dashboard": {
            "candidate": reverse('api_candidate_dashboard', request=request, format=format),
            "staff": reverse('api_staff_dashboard', request=request, format=format),
        },
        "leaderboard": reverse('api_leaderboard', request=request, format=format)
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