# backend/api/services.py

import os
import json
import google.generativeai as genai
from google.cloud import vision
from dotenv import load_dotenv
import PIL.Image

# Load environment variables from .env file
load_dotenv()

# --- CLIENT INITIALIZATION ---
client_vision = vision.ImageAnnotatorClient()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=GOOGLE_API_KEY)


# --- OCR FUNCTION ---
def perform_ocr(image_path):
    """Reads handwriting from an image using Google Vision API."""
    try:
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client_vision.document_text_detection(image=image)
        
        return response.full_text_annotation.text if response.full_text_annotation else ""
    except Exception as e:
        print(f"OCR Error: {e}")
        return f"OCR Failed: {str(e)}"

# --- AI EVALUATION FUNCTION ---
def evaluate_answer_with_ai(student_answer_text, model_answer, marking_scheme, max_mark, marking_principles=""):
    """
    Uses Google Gemini to evaluate a student's answer.
    """
    
    prompt = f"""
    You are an expert academic evaluator. Your task is to grade a student's answer based on a strict marking scheme and overall principles.

    --- CONTEXT ---
    Maximum Possible Mark: {max_mark}
    Overall Marking Principles for this test: "{marking_principles}"
    Model Answer (The ideal response for this question): "{model_answer}"
    Marking Scheme (Specific points for this question): "{marking_scheme}"

    --- STUDENT'S RESPONSE ---
    "{student_answer_text}"
    
    --- INSTRUCTIONS ---
    1.  First, consider the "Overall Marking Principles". If the principles are empty, ignore this step.
    2.  Then, carefully compare the "STUDENT'S RESPONSE" to the "Model Answer" and the "Marking Scheme".
    3.  Calculate the "Mark Gained". This MUST be a number between 0 and {max_mark}.
    4.  Write a brief "Summary" of the evaluation.
    5.  Identify specific "Strengths" where the student's answer correctly aligns with the marking scheme.
    6.  Identify specific "Improvement Points" where the student's answer is lacking or incorrect.
    
    --- OUTPUT FORMAT ---
    You MUST provide your response as a single, valid JSON object. Do not include any text before or after the JSON object.
    Example JSON format:
    {{
        "mark_gained": 8.5,
        "summary": "The student correctly identified the main causes but missed one key detail about the consequences.",
        "strengths": "Good explanation of Cause A and Cause B, aligning with the model answer.",
        "improvements": "The answer did not mention the long-term economic impact, which was worth 2 marks according to the scheme."
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        cleaned_json_string = response.text.strip().replace("```json", "").replace("```", "").strip()
        ai_output = json.loads(cleaned_json_string)
        
        try:
            mark = float(ai_output.get('mark_gained', 0))
        except (ValueError, TypeError):
            mark = 0
            
        return {
            'mark_gained': mark,
            'summary': ai_output.get('summary', 'Evaluation complete.'),
            'strengths': ai_output.get('strengths', 'Answer shows general understanding.'),
            'improvements': ai_output.get('improvements', 'Review the model answer for details.')
        }
    except Exception as e:
        print(f"AI Evaluation Error: {e}")
        return {
            'mark_gained': 0, 
            'summary': f"An error occurred during AI evaluation: {str(e)}",
            'strengths': "N/A",
            'improvements': "N/A"
        }
    
def generate_model_answer_with_ai(question_description, marking_scheme, image_path=None):
    """
    Uses Google Gemini to generate an ideal model answer based on a question,
    its marking scheme, and an optional image.
    """
    
    # Start building the content that we will send to the AI
    # This always includes the text part of the prompt.
    prompt_parts = [
        f"""
        You are an expert teacher and subject matter expert. Your task is to write an ideal, comprehensive model answer for a test question.

        --- QUESTION DETAILS ---
        Question: "{question_description}"
        Marking Scheme: "{marking_scheme}"

        --- INSTRUCTIONS ---
        1.  Carefully analyze the question text and the provided image (if any).
        2.  Write a perfect, detailed model answer that a top-scoring student would provide.
        3.  Ensure the answer directly addresses all parts of the question, including any labels or features in the diagram, and fulfills all criteria in the marking scheme.
        4.  Provide explanation why this is a model answer
        5.  Your response should ONLY be the text of the model answer. Do not include any extra text like "Here is the model answer:".

        --- MODEL ANSWER ---
        """
    ]

    # If an image path was provided, open the image and add it to our content list
    if image_path:
        try:
            img = PIL.Image.open(image_path)
            prompt_parts.append(img)
        except Exception as e:
            print(f"Error opening image for AI Vision: {e}")
            # If the image fails to load, we can proceed with just the text
            # Or we could return an error. For now, let's proceed.
            pass

    try:
        # We use a multimodal model that can handle both text and images
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # We pass the list of content parts (text and optionally an image)
        response = model.generate_content(prompt_parts)
        return response.text.strip()
    except Exception as e:
        print(f"AI Model Answer Generation Error: {e}")
        return f"Error generating model answer: {str(e)}"