# backend/api/serializers.py

from rest_framework import serializers
from django.db import models
from core.models import Class, Student, Test, Question, StudentAnswer, MarkingPrinciple

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('class_group',)

class MarkingPrincipleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkingPrinciple
        fields = ['id', 'name']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'test', 'q_number', 'description', 'question_image', 'max_mark', 'model_answer', 'marking_scheme']
        read_only_fields = ('id','test',)

class TestSerializer(serializers.ModelSerializer):
    # This will calculate the total max mark for all questions in a test
    total_max_mark = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = ['id', 'name', 'class_group', 'date_created', 'marking_principle', 'total_max_mark']

    def get_total_max_mark(self, obj):
        # Sums the max_mark of all questions related to this test
        return obj.questions.aggregate(total=models.Sum('max_mark'))['total'] or 0

class StudentAnswerUploadSerializer(serializers.ModelSerializer):
    """Serializer just for handling the initial image upload."""
    class Meta:
        model = StudentAnswer
        fields = ('id', 'question', 'student', 'uploaded_image', 'is_evaluated')
        read_only_fields = ('is_evaluated',)

class StudentAnswerEvaluationSerializer(serializers.ModelSerializer):
    """Serializer for viewing the full, detailed evaluation results."""
    # We nest other serializers to show related object details
    question = QuestionSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = StudentAnswer
        fields = (
            'id', 'student', 'question', 'uploaded_image', 
            'ocr_text', 'mark_gained', 'ai_evaluation_summary', 
            'ai_strength_points', 'ai_improvement_points', 'is_evaluated'
        )

class StudentTestResultSerializer(serializers.ModelSerializer):
    """Serializer for the final report view."""
    total_mark_gained = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ('id', 'name', 'total_mark_gained')
    
    def get_total_mark_gained(self, obj):
        test_id = self.context.get('test_id')
        if not test_id:
            return 0
        
        total = StudentAnswer.objects.filter(
            student=obj,
            question__test_id=test_id
        ).aggregate(total=models.Sum('mark_gained'))['total']
        
        return total if total is not None else 0