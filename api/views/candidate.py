from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.settings import api_settings
from django.db.models import Prefetch

from ..models import Candidate, CandidateScore
from ..permissions import StaffWithRole
from ..serializers import CandidateDetailSerializer, CandidateListSerializer
from ..utils.user import validate_role
from ..utils.query_filters import filter_candidates
from ..utils.helpers import get_candidate_with_scores
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def candidate_me_api(request):
    try:
        candidate = request.user.candidate
        serializer = CandidateListSerializer(candidate)
        return Response(serializer.data)
    except AttributeError:
        return Response({"error": "Not a candidate"}, status=status.HTTP_403_FORBIDDEN)

class CandidateListView(ListAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['moderator', 'admin', 'owner'])]
    serializer_class = CandidateListSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_queryset(self):
        return filter_candidates(
            Candidate.objects.all(),
            self.request.query_params
            )

class CandidateDetailView(RetrieveUpdateDestroyAPIView):
    """
    Handles retrieval, updates, and deletion of candidate profiles.
    - Only owners or admins can view and modify
    """
    permission_classes = [IsAuthenticated, StaffWithRole(['owner', 'admin'])]
    serializer_class = CandidateDetailSerializer
    queryset = Candidate.objects.all()
    lookup_url_kwarg = 'candidate_id'
    
    def get_queryset(self):
        return Candidate.objects.with_scores().prefetch_related(
            Prefetch('scores', queryset=CandidateScore.objects.select_related('exam', 'submitted_by'))
        )
    
    def retrieve(self, request, *args, **kwargs):
        candidate = self.get_object()
        return Response(get_candidate_with_scores(candidate))

class AssignCandidateRoleView(UpdateAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['owner', 'admin'])]
    serializer_class = CandidateDetailSerializer
    queryset = Candidate.objects.all()
    lookup_url_kwarg = 'candidate_id'
    http_method_names = ['put']

    def update(self, request, *args, **kwargs):
        candidate = self.get_object()
        new_role = request.data.get('role')
        
        if error := validate_role(new_role, Candidate):
            return error
            
        candidate.role = new_role
        candidate.save()
        return Response(self.get_serializer(candidate).data)