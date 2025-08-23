# backend/core/models.py

from django.db import models

class Class(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Student(models.Model):
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    name = models.CharField(max_length=150)
    
    def __str__(self):
        return self.name
    
class MarkingPrinciple(models.Model):
    name = models.CharField(max_length=200, unique=True)
    pdf_file = models.FileField(upload_to='marking_principles/')
    # This field will store the extracted text for quick AI access
    extracted_text = models.TextField(blank=True, null=True, editable=False)

    def __str__(self):
        return self.name

class Test(models.Model):
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)

    marking_principle = models.ForeignKey(
        MarkingPrinciple, 
        on_delete=models.SET_NULL, # If a principle is deleted, don't delete the test
        blank=True, 
        null=True
    )
    
    def __str__(self):
        return f"{self.name} ({self.class_group.name})"

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    q_number = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True, default="Question")
    max_mark = models.PositiveIntegerField(default=10)
    question_image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    model_answer = models.TextField(help_text="The standard correct answer text.")
    marking_scheme = models.TextField() 
    
    class Meta:
        ordering = ['q_number']
        unique_together = ('test', 'q_number')

    def __str__(self):
        return f"Q{self.q_number} for {self.test.name}"

class StudentAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    uploaded_image = models.ImageField(upload_to='student_answers/')
    ocr_text = models.TextField(blank=True, null=True, help_text="AI recognized text from handwriting.")
    mark_gained = models.FloatField(default=0)
    ai_evaluation_summary = models.TextField(blank=True, null=True, help_text="AI comparison summary.")
    ai_strength_points = models.TextField(blank=True, null=True)
    ai_improvement_points = models.TextField(blank=True, null=True)
    is_evaluated = models.BooleanField(default=False)

    class Meta:
        unique_together = ('question', 'student')

    def __str__(self):
        return f"{self.student.name}'s answer to Q{self.question.q_number}"