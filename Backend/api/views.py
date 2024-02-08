from django.shortcuts import render
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import CourseSerializer, EnrollmentSerializer
from .permissions import IsInstructor

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.select_related("instructor")
    permission_classes = [IsInstructor]

    ordering_fields = ["created_at"]
    search_fields = ['title']

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    
