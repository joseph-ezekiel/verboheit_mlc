"""
API views for managing exam questions, including listing, creation,
retrieval, updating, and deletion.
"""

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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, StaffWithRole(["moderator", "admin", "owner"])])
def question_list_api(request):
    """
    List all questions or create a new question.

    - GET: Returns a paginated and filtered list of questions.
    - POST: Creates a new question from provided data.

    Permissions:
        - Only accessible to staff with role: moderator, admin, or owner.
    """
    if request.method == "GET":
        questions = Question.objects.all().order_by("-date_created")
        questions = filter_questions(questions, request.query_params)
        return paginate_queryset(questions, request, QuestionSerializer)

    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, StaffWithRole(["moderator", "admin", "owner"])])
def question_detail_api(request, question_id):
    """
    Retrieve, update, or delete a specific question.

    - GET: Returns details of a specific question.
    - PUT/PATCH: Updates the question data.
    - DELETE: Deletes the question.

    Args:
        question_id (int): The ID of the question to operate on.

    Permissions:
        - Only accessible to staff with role: moderator, admin, or owner.
    """
    question = get_object_or_404(Question, id=question_id)

    if request.method == "GET":
        return Response(QuestionSerializer(question).data)

    if request.method in ["PUT", "PATCH"]:
        serializer = QuestionSerializer(
            question, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    question.delete()
    return Response({"message": "Question deleted successfully"})
