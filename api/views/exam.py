from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Exam, Question, CandidateScore, Candidate
from ..serializers import ExamListSerializer, ExamDetailSerializer, QuestionSerializer
from ..permissions import StaffWithRole
from ..utils.pagination_helpers import paginate_queryset
from ..utils.query_filters import filter_exams

# === Exam Details ===
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
def exam_list_api(request):
    if request.method == 'GET':
        exams = Exam.objects.all()
        exams = filter_exams(exams, request.query_params)
        return paginate_queryset(exams, request, ExamListSerializer)

    serializer = ExamDetailSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
def exam_detail_api(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'GET':
        return Response(ExamDetailSerializer(exam).data)

    if request.method in ['PUT', 'PATCH']:
        serializer = ExamDetailSerializer(
            exam, data=request.data, partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    exam.delete()
    return Response({'message': 'Exam deleted successfully.'})

# === Exam Questions ===
@api_view(['GET'])
@permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
def exam_questions_api(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = Question.objects.filter(exam=exam)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)

# === Exam History ===
@api_view(['GET'])
@permission_classes([IsAuthenticated, StaffWithRole(['admin', 'owner'])])
def exam_history_api(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    scores = CandidateScore.objects.filter(candidate=candidate).select_related('exam')
    data = [
        {
            "exam": s.exam.title,
            "score": float(s.score),
        } for s in scores
    ]
    return Response(data)
