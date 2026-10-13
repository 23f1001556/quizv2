import google.generativeai as genai
import os
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini using the server-side key.
DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=DEFAULT_API_KEY)

def get_model():
    if not DEFAULT_API_KEY:
        raise ValueError("Gemini API key is not configured on the server.")

    genai.configure(api_key=DEFAULT_API_KEY)
    return genai.GenerativeModel("gemini-flash-latest")

GUARDRAIL_PROMPT = """
You are a strict and helpful study assistant for a student platform called Quizzy.
Your ONLY purpose is to help with studies, quizzes, and educational content.
If the user asks anything unrelated to studies (e.g., entertainment, politics, personal advice), you MUST refuse to answer and politely redirect them to study topics.
Do not generate any harmful, inappropriate, or non-educational content.
"""

def _call_gemini(prompt):
    full_prompt = f"{GUARDRAIL_PROMPT}\n\n{prompt}"
    try:
        model = get_model()
        response = model.generate_content(full_prompt)
        return response.text
    except ValueError as ve:
        # Pass through expected errors (like missing API key)
        raise ve
    except Exception as e:
        raise Exception(f"AI Service Error: {str(e)}")

def analyze_quiz_performance(user_name, performance_data):
    """
    Analyzes user performance based on multiple quiz results.
    performance_data: List of dicts { 'quiz_title': str, 'score': str, 'weak_concepts': list }
    """
    prompt = f"""
    Analyze the quiz performance for student: {user_name}.
    
    Performance Data:
    {performance_data}

    1. Identify the TOP 3 overall weak concepts across these quizzes.
    2. Provide a 1-sentence motivation.
    3. For EACH of the 3 weak concepts, suggest a specific, actionable study focus.
    
    Return strict JSON format ONLY:
    {{
      "summary": "...",
      "weak_areas": [
        {{ "concept": "...", "advice": "..." }},
        {{ "concept": "...", "advice": "..." }}
      ]
    }}
    """
    return _call_gemini(prompt)

def generate_study_material(topic, weakness_context):
    """
    Generates a COMPREHENSIVE study guide.
    """
    prompt = f"""
    Generate a concise and structured study guide for the topic: "{topic}".
    Context/Weakness: {weakness_context}
    
    Format as Markdown. Keep it brief and to the point.
    
    REQUIREMENTS:
    1. **Key Concepts**: Use bullet points to explain core concepts briefly.
    2. **Visuals**: Use one simple ASCII diagram if necessary.
    3. **Comparison**: Small table comparing key items.
    4. **Quick Tips**: 2-3 common pitfalls.
    5. **Example**: One short example.
    
    Total length should be optimized for quick reading. Avoid long paragraphs.
    """
    return _call_gemini(prompt)

def generate_questions(topic, count=5, question_type="single", difficulty="Medium"):
    """
    Generates unique questions on a topic.
    """
    prompt = f"""
    Generate {count} unique {question_type}-choice questions on the topic: "{topic}".
    Complexity Level: {difficulty}
    
    The questions should be conceptual and appropriate for the {difficulty} level.
    
    Return strict JSON format ONLY:
    {{
      "questions": [
        {{
          "question": "...",
          "options": {{
              "A": "...",
              "B": "...",
              "C": "...",
              "D": "..."
          }},
          "answer": "A",
          "explanation": "..."
        }}
      ]
    }}
    """
    return _call_gemini(prompt)

def process_media(file_path, action, query=None, difficulty="Medium", count=5):
    """
    Processes PDF or Image and performs an action.
    """
    try:
        is_pdf = file_path.lower().endswith(".pdf")
        
        if is_pdf:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            if len(text) > 30000:
                text = text[:30000] + "...(truncated)"
            
            content_part = f"Document Content:\n{text}"
        else:
            # Handle Image
            import PIL.Image
            img = PIL.Image.open(file_path)
            content_part = img

        if action == "explain":
            prompt = f"""
            Based on the provided content (PDF/Image), explain the key concepts simply.
            Target Difficulty: {difficulty}
            Specific Question: {query if query else 'None'}
            """
        elif action == "generate_quiz":
            prompt = f"""
            Based on the provided content (PDF/Image), generate {count} multiple-choice questions.
            Difficulty Level: {difficulty}
            
            Return strict JSON format ONLY:
            {{
              "questions": [
                {{
                  "question": "...",
                  "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
                  "answer": "A",
                  "explanation": "..."
                }}
              ]
            }}
            """
        else:
            return "Invalid action."

        # Multimodal generation
        model = get_model()
        response = model.generate_content([GUARDRAIL_PROMPT, prompt, content_part] if not is_pdf else [GUARDRAIL_PROMPT, prompt + "\n" + content_part])
        return response.text

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Media Processing Error: {str(e)}")
