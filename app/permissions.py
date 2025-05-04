from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'host'):
            return obj.host == request.user
        return False

class IsHost(permissions.BasePermission):
    """
    Custom permission to only allow hosts to create properties.
    """
    def has_permission(self, request, view):
        # Allow GET requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is a host for POST, PUT, DELETE
        return request.user.is_authenticated and request.user.is_host
