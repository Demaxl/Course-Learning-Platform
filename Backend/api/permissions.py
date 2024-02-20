from rest_framework import permissions
from .models import Course, Lesson
from django.shortcuts import get_object_or_404

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
    

class IsEnrolledOrInstructor(permissions.IsAuthenticated):
    message = "Only enrolled students or the instructor of this course can view its lessons"
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        course = get_object_or_404(Course, pk=view.kwargs['course_pk'])

        if request.method not in permissions.SAFE_METHODS:
            self.message = "Only the instructor of this course can create and edit its lessons"
            return request.user == course.instructor

        return request.user.isEnrolled(course) or request.user == course.instructor     
        
       

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            self.message = "Only the instructor of this course can edit its lessons"
            return request.user == obj.course.instructor
        
        return (request.user == obj.course.instructor) or (request.user.isEnrolled(obj.course))
