from rest_framework import permissions

## Admin permissions ##
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'ADMIN'
        )

## Blood bank permissions ##
class IsBloodBank(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'BLOOD_BANK'
        )
    
## Staff permissions ##
class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'STAFF'
        )

## Donor permissions ##
class IsDonor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'DONOR'
        )

## Conssumer permissions ##
class IsConsumer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'CONSUMER'
        )



class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a blood bank or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.user_type == 'ADMIN':
            return True
            
        # Blood bank can only access their own profile
        return obj.email == request.user.email