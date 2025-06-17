from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Question
from ..serializers import QuestionSerializer
from ..permissions import StaffWithRole
from ..utils.pagination_helpers import paginate_queryset
from ..utils.query_filters import filter_questions

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, StaffWithRole(['moderator', 'admin', 'owner'])])
def question_list_api(request):
    if request.method == 'GET':
        questions = Question.objects.all()
        questions = filter_questions(questions, request.query_params)
        return paginate_queryset(questions, request, QuestionSerializer)

    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, StaffWithRole(['moderator', 'admin', 'owner'])])
def question_detail_api(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'GET':
        return Response(QuestionSerializer(question).data)

    if request.method in ['PUT', 'PATCH']:
        serializer = QuestionSerializer(
            question, data=request.data, partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    question.delete()
    return Response({'message': 'Question deleted successfully'})