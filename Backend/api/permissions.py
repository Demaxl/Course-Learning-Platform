from rest_framework import permissions


class IsInstructor(permissions.IsAuthenticated):
    message = "Only instructors are allowed"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not super().has_permission(request, view):
            return False
        
        return not request.user.is_student

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        self.message = "Only the instructor of this course can edit it"
        return request.user == obj.instructor
    
