"""
Generic utilities for update/delete operations and role validation.
Used to reduce duplication across view logic.
"""

from rest_framework.response import Response


def handle_update_delete(request, obj, serializer_class):
    """
    Generic helper for handling update and delete operations (PUT, PATCH, DELETE)
    on a model instance using a DRF serializer.

    Args:
        request (HttpRequest): The incoming request object.
        obj (Model): The model instance to update or delete.
        serializer_class (Serializer): The DRF serializer class to validate and save data.

    Returns:
        Response: DRF Response containing serialized data, error messages, or status code.
    """
    if request.method == "DELETE":
        obj.delete()
        return Response(status=204)

    serializer = serializer_class(
        obj, data=request.data, partial=(request.method == "PATCH")
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


def validate_role(role, model_class):
    """
    Validate a given role against the allowed ROLE_CHOICES for a model.

    Args:
        role (str): The role string to validate.
        model_class (Model): The model class containing ROLE_CHOICES.

    Returns:
        None if valid, or Response with error message if invalid.
    """
    if role not in dict(model_class.ROLE_CHOICES):
        return Response({"error": "Invalid role"}, status=400)
    return None
