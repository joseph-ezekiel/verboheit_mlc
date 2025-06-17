from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Staff
from ..permissions import StaffWithRole
from ..serializers import StaffDetailSerializer, StaffListSerializer
from ..utils.user import handle_update_delete
from ..utils.query_filters import filter_staffs
from ..utils.pagination_helpers import paginate_queryset

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_me_api(request):
    try:
        staff = request.user.staff
        serializer = StaffListSerializer(staff)
        return Response(serializer.data)
    except:
        return Response({"error": "Not a candidate"}, status=403)

@api_view(['GET'])
@permission_classes([IsAuthenticated, StaffWithRole(['moderator', 'admin', 'owner'])])
def staff_list_api(request):
    staff_queryset = Staff.objects.all()
    staff_queryset = filter_staffs(staff_queryset, request.query_params)
    return paginate_queryset(staff_queryset, request, StaffDetailSerializer)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, StaffWithRole(['owner'])])
def staff_detail_api(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)

    if request.method == 'GET':
        return Response(StaffDetailSerializer(staff).data)

    return handle_update_delete(request, staff, StaffDetailSerializer)
