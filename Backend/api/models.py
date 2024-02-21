from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.db.models import UniqueConstraint
from django.utils.deconstruct import deconstructible

@deconstructible
class LessonValidator(object):
    def __init__(self, serializer=False):
        self.serializer = serializer

    def __call__(self, lesson):
        if lesson is None:
            raise ValidationError([{
                        "lesson": _("Lesson can not be null")
                    }])
        if not isinstance(lesson, dict):
            raise ValidationError([{
                        "lesson": _("Invalid JSON")
                }])
        
        if "type" not in lesson:
            raise ValidationError([{
                "lesson": _("Lesson must specify type")
            }])

        
        match lesson['type']:
            case "READING":
                if "content" not in lesson:
                    raise ValidationError([{
                        "lesson": _("Reading lesson should have a 'content' field")
                    }])
            case 'VIDEO':
                if not self.serializer and 'file_path' not in lesson:
                    raise ValidationError([{
                        'lesson': _("Video lessons must have a 'file_path' field")
                    }])
            
            case _:
                raise ValidationError([{
                    "lesson": _("Lesson can only be of type 'READING' or 'VIDEO'")
                }])

    



class User(AbstractUser):
    is_student = models.BooleanField(default=True)
    
    def enroll(self, course: 'Course'):
        return Enrollment.objects.create(
            student=self,
            course=course)

    def isEnrolled(self, course):
        return course.students.contains(self)
    
    def unEnroll(self, course: 'Course'):
        course.students.remove(self)


        
class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=1000)

    students = models.ManyToManyField(
        User, 
        through="Enrollment",
        through_fields=("course", "student"),
        related_name="enrolled_courses")

    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def clean(self) -> None:
        if self.instructor.is_student:
            raise ValidationError(
                {
                    "instructor":_("Only Instructors can create courses")
                }
            )
        

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)

    class Meta:
        constraints = [UniqueConstraint(fields=["student", "course"], name="unique_enrollments")]

    def __str__(self) -> str:
        return f"{self.student} enrolled in {self.course}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.student.is_student:
            raise ValidationError(_("Only students can enroll in courses"))
    
    def getProgress(self):
        lessons_len = self.course.lessons.count()
        completed = self.student.progress.filter(course=self.course).count()
        

        return (completed, lessons_len)



class Lesson(models.Model):
    order = models.SmallAutoField(editable=False, primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    lesson = models.JSONField(null=False, validators=[LessonValidator()])
    
    class Meta:
        get_latest_by = "pk"
        constraints = [
            UniqueConstraint(fields=["course", "title"], name="unique_lesson_title")
        ]

    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
 
    def complete(self, student: User):
        Progress.objects.create(student=student, course=self.course, lesson=self)
    

class Progress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["student", "course", "lesson"], name="unique_progress")
            ]
    
    def __str__(self):
        return f"{self.student} has completed {self.lesson}"
    
    def getEnrollment(self) -> Enrollment:
        return self.student.enrollments.get(course=self.course)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.course.students.contains(self.student):
            raise ValidationError(_("Student is not enrolled in this course"))