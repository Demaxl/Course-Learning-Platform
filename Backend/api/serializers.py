import bleach, os
from django.utils.text import slugify
from django.core.files.storage import FileSystemStorage
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Course, Enrollment, Lesson, User, Progress, LessonValidator


class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = ["id", "instructor", "title", "created_at", "description"]



class EnrollmentSerializer(serializers.ModelSerializer):
    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    course = serializers.StringRelatedField()

    class Meta:
        model = Enrollment
        fields = ["id", "course", "is_complete", "completed_lessons", "total_lessons"]
    

    def get_total_lessons(self, enrollment: Enrollment):
        return enrollment.course.lessons.count()

    def get_completed_lessons(self, enrollment: Enrollment):
        return enrollment.getProgress()[0]

class CustomUserSerializer(UserSerializer):
    type = serializers.SerializerMethodField("check_user")
    courses = CourseSerializer(many=True)
    enrollments = EnrollmentSerializer(many=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("type", "courses", "enrollments")

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data['type'] == "Student":
            data.pop("courses")
        else:
            data.pop("enrollments")

        return data


    def check_user(self, user: User):
        if user.is_student:
            return "Student"

        return "Instructor"




class LessonSerializer(serializers.ModelSerializer):    
    video = serializers.FileField(write_only=True, use_url=True, required=False)
    lesson = serializers.JSONField(validators=[LessonValidator(serializer=True)])

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ["order", "created_at", "course"]

    def validate(self, attrs):
        if 'lesson' in attrs:
            if attrs['lesson']['type'] == "VIDEO" and "video" not in attrs:
                raise serializers.ValidationError({"video":"Video file not uploaded"})
        return super().validate(attrs)

    def handle_video_file(self, video_file, title):
        ext = os.path.splitext(video_file.name)[-1]
        file_name = "video_lessons/" + slugify(title) + ext

        fs = FileSystemStorage()
        name = fs.save(file_name, video_file)

        return fs.url(name)


    def create(self, validated_data):
        if validated_data['lesson']['type'] == "VIDEO":
            url = self.handle_video_file(validated_data.pop('video'), validated_data['title'])
            validated_data['lesson']['file_path'] = url

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        title = validated_data.get('title', instance.title)
        if validated_data.get("lesson", False) and validated_data['lesson']['type'] == "VIDEO":
            url = self.handle_video_file(validated_data['video'], title)
            validated_data['lesson']['file_path'] = url

        return super().update(instance, validated_data)

class CustomUserCreateSerializer(UserCreateSerializer):
    type = serializers.CharField(max_length=15, write_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ("type",)

    def validate(self, attrs):
        type = attrs.pop("type")
        attrs = super().validate(attrs)

        attrs["type"] = type
        return attrs

    def validate_type(self, type):
        type = bleach.clean(type)

        if type not in ["STUDENT", "INSTRUCTOR"]:
            raise serializers.ValidationError(
                "Invalid account type. Choices are 'STUDENT' or 'INSTRUCTOR'")

        return type

    def create(self, validated_data):
        type = validated_data.pop("type")
        user = super().create(validated_data)

        if type == "INSTRUCTOR":
            user.is_student = False

        user.save()
        return user
