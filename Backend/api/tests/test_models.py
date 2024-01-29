from django.test import TestCase
from django.core.exceptions import ValidationError
from api.models import *


class CourseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username="demaxl", password="Characters12345!")
        cls.instructor = User.objects.create_user(username="micheal", password="Characters12345!", is_student=False)
        cls.course = Course.objects.create(
            instructor=cls.instructor,
            title="Intro to backend",
            description="This is a backend course"
        )
        cls.lesson1 = Lesson.objects.create(
            course=cls.course,
            title="What is backend",
            lesson='{"type":"video","url":"asd"}'
        )

        cls.lesson2 = Lesson.objects.create(
            course=cls.course,
            title="What is frontend",
            lesson='{"type":"text","url":"asd"}'
        )

        cls.enrollment = cls.student.enroll(cls.course)

    