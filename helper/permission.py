from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user != request.user:
            return False
        return obj.user == request.user
