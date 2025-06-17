from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from ..models import Candidate, CandidateScore
from ..permissions import StaffWithRole
from ..serializers import CandidateDetailSerializer, CandidateListSerializer
from ..utils.user import handle_update_delete, validate_role
from ..utils.query_filters import filter_candidates
from ..utils.pagination_helpers import paginate_queryset

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def candidate_me_api(request):
    try:
        candidate = request.user.candidate
        serializer = CandidateListSerializer(candidate)
        return Response(serializer.data)
    except:
        return Response({"error": "Not a candidate"}, status=403)


@api_view(['GET'])
@permission_classes([IsAuthenticated, StaffWithRole(['moderator', 'admin', 'owner'])])
def candidate_list_api(request):
    candidates = Candidate.objects.all()
    candidates = filter_candidates(candidates, request.query_params)
    return paginate_queryset(candidates, request, CandidateListSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
def candidate_detail_api(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # Restrict non-admin users from modifying other users
    if request.method in ['PUT', 'PATCH', 'DELETE']:
        if request.user != candidate.user and not hasattr(request.user, 'staff'):
            return Response({'error': 'Permission denied.'}, status=403)

    if request.method == 'GET':
        # Get candidate's exam scores
        scores = CandidateScore.objects.filter(candidate=candidate).select_related('exam')
        score_data = [
            {
                'exam_id': score.exam.id,
                'exam_title': score.exam.title,
                'score': float(score.score),
                'date_taken': getattr(score, 'date_taken', None),
            }
            for score in scores
        ]

        total_score = sum([float(s['score']) for s in score_data])
        average_score = total_score / len(score_data) if score_data else 0.0

        candidate_data = CandidateDetailSerializer(candidate).data
        candidate_data.update({
            'scores': score_data,
            'total_score': total_score,
            'average_score': average_score,
        })

        return Response(candidate_data)

    return handle_update_delete(request, candidate, CandidateDetailSerializer)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, StaffWithRole(['owner', 'admin'])])
def assign_candidate_role_api(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    new_role = request.data.get('role')

    error_response = validate_role(new_role, Candidate)
    if error_response:
        return error_response

    candidate.role = new_role
    candidate.save()
    return Response(CandidateDetailSerializer(candidate).data)