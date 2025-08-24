# backend/api/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ClassViewSet, 
    StudentViewSet,
    MarkingPrincipleViewSet, 
    TestViewSet, 
    QuestionViewSet, 
    StudentAnswerViewSet,
    generate_model_answer_view
)

# The router handles all the standard URLs (list, create, retrieve, update, delete)
router = DefaultRouter()
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'tests', TestViewSet, basename='test')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'marking-principles', MarkingPrincipleViewSet, basename='markingprinciple')
router.register(r'answers', StudentAnswerViewSet, basename='studentanswer')

# We start with the router's default URLs
urlpatterns = router.urls

# --- THIS IS THE CRITICAL FIX ---
# We manually add the URLs for our custom actions.
# This bypasses the router's magic and explicitly tells Django what to do.
urlpatterns += [
    path('generate-model-answer/', generate_model_answer_view, name='generate-model-answer'),
    
    # This line creates the URL: /api/answers/<id>/run-ocr/
    # It maps a POST request to the 'run_ocr' method inside StudentAnswerViewSet.
    path(
        'answers/<int:pk>/run-ocr/', 
        StudentAnswerViewSet.as_view({'post': 'run_ocr'}), 
        name='studentanswer-run-ocr'
    ),
    
    # This line creates the URL: /api/answers/<id>/run-marking/
    # It maps a POST request to the 'run_marking' method inside StudentAnswerViewSet.
    path(
        'answers/<int:pk>/run-marking/', 
        StudentAnswerViewSet.as_view({'post': 'run_marking'}), 
        name='studentanswer-run-marking'
    ),
    
    path(
        'answers/find/',
        StudentAnswerViewSet.as_view({'get': 'find'}),
        name='studentanswer-find'
    ),
]