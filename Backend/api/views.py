from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import *
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer
from .permissions import IsInstructor, IsEnrolledOrInstructor


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.select_related("instructor").order_by("created_at")
    permission_classes = [IsInstructor]

    ordering_fields = ["created_at"]
    search_fields = ['title']
    pagination_class = Pagination


    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


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
    
    # def partial_update(self, request, *args, **kwargs):
    #     # video = request.data.get('video')
    #     # print(video.temporary_file_path())
    #     # print(video.name)
    #     # with open('test.mp4', 'wb') as destination:
    #     #     for chunk in video.chunks():
    #     #         destination.write(chunk)
    #     # print(request.files)
    #     return super().partial_update(request, *args, **kwargs)

    
