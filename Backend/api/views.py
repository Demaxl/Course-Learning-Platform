from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer
from .permissions import IsInstructorOrReadOnly, IsEnrolledOrInstructor, IsStudent


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.select_related("instructor").order_by("created_at")
    permission_classes = [IsInstructorOrReadOnly]

    ordering_fields = ["created_at"]
    search_fields = ['title']
    pagination_class = Pagination


    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    
    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()

        if request.user.isEnrolled(course):
            return Response({"error":"User already enrolled in course"}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = EnrollmentSerializer(request.user.enroll(course))
        return Response(enrollment.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def unenroll(self, request, *args, **kwargs):
        course = self.get_object()

        if not request.user.isEnrolled(course):
            return Response({"error":"User is not enrolled in course"}, status=status.HTTP_400_BAD_REQUEST)

        request.user.unEnroll(course)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsEnrolledOrInstructor]

    def dispatch(self, request, *args, **kwargs):
        course_pk = kwargs.get('course_pk')

        if course_pk and not course_pk.isdigit():
            kwargs.update({"course_pk": -1})    

        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        return Lesson.objects.filter(course=course)

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        serializer.save(course=course)


