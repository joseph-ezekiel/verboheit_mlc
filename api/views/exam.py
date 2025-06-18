from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView

from ..models import Exam, Question, CandidateScore, Candidate
from ..serializers import ExamListSerializer, ExamDetailSerializer, QuestionSerializer
from ..permissions import StaffWithRole
from ..utils.pagination_helpers import paginate_queryset
from ..utils.query_filters import filter_exams

# === Exam Details ===
class ExamListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['admin', 'owner'])]
    serializer_class = ExamListSerializer
    filterset_class = filter_exams  # Assuming filter_exams is a FilterSet
    
    def get_serializer_class(self):
        return ExamDetailSerializer if self.request.method == 'POST' else ExamListSerializer
    
    def get_queryset(self):
        return Exam.objects.all()

class ExamDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['admin', 'owner'])]
    serializer_class = ExamDetailSerializer
    queryset = Exam.objects.all()
    lookup_url_kwarg = 'exam_id'
    
    def perform_destroy(self, instance):
        instance.delete()
        return Response({'message': 'Exam deleted successfully.'})

# === Exam Questions ===
class ExamQuestionsView(ListAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['admin', 'owner'])]
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return exam.questions.all()

# === Exam History ===
class ExamHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['admin', 'owner'])]
    
    def get(self, request, *args, **kwargs):
        candidate = get_object_or_404(Candidate, pk=self.kwargs['candidate_id'])
        scores = CandidateScore.objects.filter(
            candidate=candidate
        ).select_related('exam')
        
        data = [{
            "exam": s.exam.title,
            "score": float(s.score),
        } for s in scores]
        
        return Response(data)
