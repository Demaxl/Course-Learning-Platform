from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

@admin.register(User)
class NewUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ["is_student"]}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ["is_student"]}),)

    list_display = UserAdmin.list_display + ("is_student",)


admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Progress)
admin.site.register(Enrollment)
