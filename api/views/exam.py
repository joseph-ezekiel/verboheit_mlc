from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Exam
from ..serializers import ExamListSerializer, ExamDetailSerializer
from ..permissions import StaffWithRole
from ..utils.pagination_helpers import paginate_queryset
from ..utils.query_filters import filter_exams

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, StaffWithRole(['moderator', 'admin', 'owner'])])
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