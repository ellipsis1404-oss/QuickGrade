# backend/core/admin.py

from django.contrib import admin
from .models import Class, Student, Test, Question, StudentAnswer, MarkingPrinciple

admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(StudentAnswer)
admin.site.register(MarkingPrinciple)