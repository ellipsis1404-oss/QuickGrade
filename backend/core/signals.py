# backend/core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from PyPDF2 import PdfReader
from .models import MarkingPrinciple

@receiver(post_save, sender=MarkingPrinciple)
def extract_text_from_pdf(sender, instance, created, **kwargs):
    # This function runs every time a MarkingPrinciple is saved.
    # We check if the extracted_text is empty or if the file has been re-uploaded.
    
    if instance.pdf_file and not instance.extracted_text:
        text = ""
        try:
            # Open the PDF file from storage
            with instance.pdf_file.open('rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            # Update the instance without triggering the signal again to avoid a loop
            MarkingPrinciple.objects.filter(pk=instance.pk).update(extracted_text=text)
            print(f"Successfully extracted text from {instance.name}")

        except Exception as e:
            print(f"Error extracting text from PDF for {instance.name}: {e}")
            MarkingPrinciple.objects.filter(pk=instance.pk).update(extracted_text=f"Error: {e}")