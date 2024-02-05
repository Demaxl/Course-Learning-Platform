# urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path 

from . import views

router = DefaultRouter(trailing_slash=False)
router.register("courses", views.CourseViewSet, basename="courses")
urlpatterns = router.urls
