import bleach

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import *


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

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ["order", "created_at", "course"]

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
