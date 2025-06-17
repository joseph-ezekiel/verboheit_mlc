from rest_framework.response import Response

def handle_update_delete(request, obj, serializer_class):
    """Generic helper for PUT/PATCH/DELETE operations"""
    if request.method == 'DELETE':
        obj.delete()
        return Response(status=204)
    
    serializer = serializer_class(
        obj,
        data=request.data, 
        partial=(request.method == 'PATCH')
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

def validate_role(role, model_class):
    """Validate role against model choices"""
    if role not in dict(model_class.ROLE_CHOICES):
        return Response({'error': 'Invalid role'}, status=400)
    return None