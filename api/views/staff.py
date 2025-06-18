from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.settings import api_settings
from django.shortcuts import get_object_or_404

from ..models import Staff
from ..permissions import StaffWithRole
from ..serializers import StaffDetailSerializer, StaffListSerializer
from ..utils.user import handle_update_delete
from ..utils.query_filters import filter_staffs
from ..utils.pagination_helpers import paginate_queryset
from ..utils.user import handle_update_delete, validate_role
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_me_api(request):
    try:
        staff = request.user.staff
        serializer = StaffListSerializer(staff)
        return Response(serializer.data)
    except AttributeError:
        return Response({"error": "Not a staff member"}, status=status.HTTP_403_FORBIDDEN)

class StaffListView(ListAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['moderator', 'admin', 'owner'])]
    serializer_class = StaffDetailSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_queryset(self):
        return filter_staffs(
            Staff.objects.all(),
            self.request.query_params
        )
    
class StaffDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['owner'])]
    serializer_class = StaffDetailSerializer
    queryset = Staff.objects.all()
    lookup_url_kwarg = 'staff_id'
    
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer) -> None:
        logger.info(
            f"Updating staff {serializer.instance.id}",
            extra={'user': self.request.user.id}
        )
        serializer.save(updated_by=self.request.user.staff)

    def perform_destroy(self, instance) -> None:
        logger.info(
            f"Soft-deleting staff {instance.id}",
            extra={'user': self.request.user.id}
        )
        instance.is_active = False
        instance.save()
        
class AssignStaffRoleView(UpdateAPIView):
    permission_classes = [IsAuthenticated, StaffWithRole(['owner'])]
    serializer_class = StaffDetailSerializer
    queryset = Staff.objects.all()
    lookup_url_kwarg = 'staff_id'
    http_method_names = ['put']  # Restrict to PUT only

    def update(self, request, *args, **kwargs):
        staff = self.get_object()
        new_role = request.data.get('role')
        
        if error := validate_role(new_role, Staff):
            return error
            
        staff.role = new_role
        staff.save()
        return Response(self.get_serializer(staff).data)