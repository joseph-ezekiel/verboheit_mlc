"""
API views to set, list, and retrieve exam details.
"""

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
)

from ..models import Exam, CandidateScore, Candidate
from ..serializers import ExamListSerializer, ExamDetailSerializer, QuestionSerializer
from ..permissions import StaffWithRole
from ..utils.query_filters import filter_exams


class ExamListView(ListCreateAPIView):
    """
    API view to list all exams or create a new exam.

    - GET: Returns a list of all exams.
    - POST: Creates a new exam with detailed input data.
    """

    permission_classes = [IsAuthenticated, StaffWithRole(["admin", "owner"])]
    serializer_class = ExamListSerializer
    filterset_class = filter_exams

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the HTTP method.
        - Uses `ExamDetailSerializer` for POST requests.
        - Uses `ExamListSerializer` for GET requests.
        """
        return (
            ExamDetailSerializer
            if self.request.method == "POST"
            else ExamListSerializer
        )

    def get_queryset(self):
        """Returns a queryset of all Exam objects."""
        return Exam.objects.all()


class ExamDetailView(RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single exam instance.

    - GET: Retrieve exam details.
    - PUT/PATCH: Update exam information.
    - DELETE: Remove the exam.
    """

    permission_classes = [IsAuthenticated, StaffWithRole(["admin", "owner"])]
    serializer_class = ExamDetailSerializer
    queryset = Exam.objects.all()
    lookup_url_kwarg = "exam_id"

    def perform_destroy(self, instance):
        """
        Deletes the exam instance and returns a success message.
        """
        instance.delete()
        return Response({"message": "Exam deleted successfully."})


class ExamQuestionsView(ListAPIView):
    """
    API view to list all questions belonging to a specific exam.

    Requires exam_id in the URL path.
    """

    permission_classes = [IsAuthenticated, StaffWithRole(["admin", "owner"])]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        """
        Returns the queryset of questions related to a given exam.
        """
        exam = get_object_or_404(Exam, pk=self.kwargs["exam_id"])
        return exam.questions.all()


class ExamHistoryView(ListAPIView):
    """
    API view to retrieve the exam history and scores of a specific candidate.

    Requires candidate_id in the URL path.
    """

    permission_classes = [IsAuthenticated, StaffWithRole(["admin", "owner"])]

    def get(self, request, *args, **kwargs):
        """
        Returns a list of exams taken by the candidate and their respective scores.
        """
        candidate = get_object_or_404(Candidate, pk=self.kwargs["candidate_id"])
        scores = CandidateScore.objects.filter(candidate=candidate).select_related(
            "exam"
        )

        data = [
            {
                "exam": s.exam.title,
                "score": float(s.score),
            }
            for s in scores
        ]

        return Response(data)
