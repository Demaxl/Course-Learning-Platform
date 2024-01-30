import bleach
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import *

class CustomUserSerializer(UserSerializer):
    type = serializers.SerializerMethodField("check_user")

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("type",)

    def check_user(self, user: User):
        if user.is_student:
            return "Student"

        return "Instructor"
    

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
            raise serializers.ValidationError("Invalid account type. Choices are 'STUDENT' or 'INSTRUCTOR'")

        return type

    def create(self, validated_data):
        type = validated_data.pop("type")
        user = super().create(validated_data)
        
        if type == "INSTRUCTOR":
            user.is_student = False 
        
        user.save()
        return user

class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = ["id", "instructor", "title", "created_at", "description"]