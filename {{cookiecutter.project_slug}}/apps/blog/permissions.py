# apps/blog/permissions.py
from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the post.
        return obj.author == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit an object.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class CanModerateComments(permissions.BasePermission):
    """
    Permission to check if the user can moderate comments.
    Moderators are staff users or the author of the post.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # The author of the post that the comment belongs to can moderate
        return obj.post.author == request.user 