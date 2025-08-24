# backend/api/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage

from core.models import Class, Student, Test, Question, StudentAnswer, MarkingPrinciple
from .serializers import (
    ClassSerializer, StudentSerializer, MarkingPrincipleSerializer, TestSerializer, QuestionSerializer, 
    StudentAnswerUploadSerializer, StudentAnswerEvaluationSerializer,
    StudentTestResultSerializer
)
# We only need one line to import from services
from .services import perform_ocr, evaluate_answer_with_ai, generate_model_answer_with_ai


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        class_obj = self.get_object()
        students = class_obj.students.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tests(self, request, pk=None):
        class_obj = self.get_object()
        tests = class_obj.tests.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class MarkingPrincipleViewSet(viewsets.ModelViewSet):
    queryset = MarkingPrinciple.objects.all()
    serializer_class = MarkingPrincipleSerializer

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        test = self.get_object()
        students = test.class_group.students.all()
        serializer = StudentTestResultSerializer(students, many=True, context={'test_id': test.id})
        return Response(serializer.data)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        test_id = self.request.query_params.get('test')
        if test_id:
            queryset = queryset.filter(test_id=test_id)
        return queryset
    def perform_create(self, serializer):
        """
        Overrides the default create behavior to inject the test_id from the data payload.
        This is the most robust way to ensure the relationship is set.
        """
        # Get the test_id from the incoming request data
        test_id = self.request.data.get('test')
        
        # Check if test_id was provided
        if not test_id:
            # This is a more informative way to handle the error if it ever happens again
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'test': 'This field is required.'})

        # Fetch the actual Test object from the database
        test_instance = get_object_or_404(Test, pk=test_id)
        
        # Save the serializer, passing the test_instance in directly
        serializer.save(test=test_instance)

class StudentAnswerViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswer.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudentAnswerUploadSerializer
        return StudentAnswerEvaluationSerializer

    @action(detail=False, methods=['get'])
    def find(self, request):
        """
        Custom action to find a single StudentAnswer by student and question IDs.
        e.g., /api/answers/find/?student=1&question=2
        """
        student_id = request.query_params.get('student')
        question_id = request.query_params.get('question')
        
        if not student_id or not question_id:
            return Response(
                {"error": "Both student and question parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Use get_object_or_404 to find the object or return a 404 if not found
        answer = get_object_or_404(
            StudentAnswer, 
            student_id=student_id, 
            question_id=question_id
        )
        
        # Use the detailed serializer for the response
        serializer = StudentAnswerEvaluationSerializer(answer, context={'request': request})
        return Response(serializer.data)

    # --- THIS FUNCTION IS NOW INDENTED CORRECTLY ---
    @action(detail=True, methods=['post'])
    def run_ocr(self, request, pk=None):
        answer = self.get_object()
        if not answer.uploaded_image:
            return Response({"detail": "No image found for this answer."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            image_path = answer.uploaded_image.path
            ocr_output = perform_ocr(image_path)
            answer.ocr_text = ocr_output
            answer.save(update_fields=['ocr_text'])
            
            serializer = self.get_serializer(answer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"OCR failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- THIS FUNCTION IS ALSO INDENTED CORRECTLY ---
    @action(detail=True, methods=['post'])
    def run_marking(self, request, pk=None):
        answer = self.get_object()
        
        corrected_text = request.data.get('corrected_text', answer.ocr_text)
        
        try:
            question = answer.question
            test = question.test
            if test.marking_principle:
                # If it is, then safely get its extracted text.
                principles_text = test.marking_principle.extracted_text or ""

            evaluation_result = evaluate_answer_with_ai(
                student_answer_text=corrected_text,
                model_answer=question.model_answer,
                marking_scheme=question.marking_scheme,
                max_mark=question.max_mark,
                marking_principles=principles_text
            )
            
            answer.ocr_text = corrected_text
            answer.mark_gained = evaluation_result['mark_gained']
            answer.ai_evaluation_summary = evaluation_result['summary']
            answer.ai_strength_points = evaluation_result['strengths']
            answer.ai_improvement_points = evaluation_result['improvements']
            answer.is_evaluated = True
            answer.save()
            
            serializer = StudentAnswerEvaluationSerializer(answer, context={'request': request})
        
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"!!! AI Marking CRASHED with error: {e}")
            return Response({"detail": f"AI Marking failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ... (the standalone generate_model_answer_view function stays here, un-indented) ...

# --- STANDALONE VIEW FUNCTION ---
# Note that this is NOT indented. It is outside of any class.
@api_view(['POST'])
def generate_model_answer_view(request):
    """
    An endpoint that receives a question description, marking scheme, and an optional image,
    and returns an AI-generated model answer.
    """
    description = request.data.get('description', '')
    marking_scheme = request.data.get('marking_scheme', '')
    question_image = request.FILES.get('question_image', None)
    
    image_path = None

    if not description or not marking_scheme:
        return Response(
            {"error": "Description and marking scheme are required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # If an image was uploaded, save it temporarily so we can get a path to it
    if question_image:
        try:
            # Save the file to the default storage (your 'media' folder)
            file_name = default_storage.save(question_image.name, question_image)
            # Get the full system path to the saved file
            image_path = default_storage.path(file_name)
        except Exception as e:
            return Response(
                {"error": f"Failed to handle image upload: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Call our upgraded service function, now with the optional image_path
    model_answer = generate_model_answer_with_ai(description, marking_scheme, image_path)

    # IMPORTANT: Clean up the temporary file after we're done with it
    if image_path:
        default_storage.delete(file_name)
    
    return Response({"model_answer": model_answer})