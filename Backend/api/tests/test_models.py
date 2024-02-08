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
            lesson={"type":"VIDEO","file_path":"path"}
        )

        cls.lesson2 = Lesson.objects.create(
            course=cls.course,
            title="What is frontend",
            lesson={"type":"READING","content":"hello"}
        )

        cls.enrollment = cls.student.enroll(cls.course)

    def testCourseComplete(self):
        """ Test to mark a course as complete if all its lessons are complete """
        self.lesson1.complete(self.student)
        self.lesson2.complete(self.student)

        enrollment = self.student.enrollments.get(course=self.course)
        
        self.assertEqual(enrollment.is_complete, True)

        Progress.objects.get(lesson=self.lesson2).delete()

        enrollment = self.student.enrollments.get(course=self.course)
        
        self.assertEqual(enrollment.is_complete, False)
    
    def testCreateCourse(self):
        # Test student create
        with self.assertRaises(ValidationError):
            Course.objects.create(
                instructor=self.student,
                title="Test",
                description="A TEST"
            )

        # Test instructor create
        Course.objects.create(
                instructor=self.instructor,
                title="Test",
                description="A TEST"
        )
    
    def testLesson(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                course=self.course,
                title="What is frontend",
                lesson={"type":"asd","content":"hello"}
            )
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                course=self.course,
                title="What is frontend",
                lesson=''
            )
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                course=self.course,
                title="What is frontend",
                lesson=None
            )
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                course=self.course,
                title="What is frontend",
                lesson={}
            )
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                course=self.course,
                title="What is frontend",
                lesson="asd"
            )
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                course=self.course,
                title="What is frontend",
                lesson={
                    "type": "READING"
                }
            )
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                course=self.course,
                title="What is frontend",
                lesson={
                    "type": "VIDEO"
                }
            )
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                course=self.course,
                title="What is frontend",
                lesson='{"type": "VIDEO", "file_path":"sad"}'
            )
            
        Lesson.objects.create(
            course=self.course,
                title="What is frontend2",
                lesson={
                    "type": "READING",
                    "content": "A test reading"
                }
            )
        Lesson.objects.create(
            course=self.course,
            title="What is backend2",
            lesson={
                    "type": "VIDEO",
                    "file_path": "asasd"
            }
        )
        
