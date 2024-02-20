# urls.py
from rest_framework_nested import routers
from django.urls import path, include

from . import views

coursesRouter = routers.DefaultRouter(trailing_slash=False)
coursesRouter.register("courses", views.CourseViewSet, basename="courses")

lessonsRouter = routers.NestedDefaultRouter(coursesRouter, "courses", lookup="course")
lessonsRouter.register("lessons", views.LessonViewSet, basename="course-lessons")


urlpatterns = [
    path("", include(coursesRouter.urls)),
    path("", include(lessonsRouter.urls))
]
