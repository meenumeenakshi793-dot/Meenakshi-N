import os
import json
import time
import random

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=API_KEY)


def generate_quiz(topic: str):

    topic = topic.strip()

    if not topic:
        raise ValueError("Quiz topic cannot be empty.")

    prompt = f"""
Create a quiz about {topic}.

Generate exactly 5 multiple-choice questions.

Return ONLY valid JSON.
Do not use markdown.
Do not use ```json.
Do not add any text outside the JSON.

Use exactly this structure:

{{
    "title": "{topic} Quiz",
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "Option A"
        }}
    ]
}}

Rules:
- Exactly 5 questions.
- Exactly 4 options per question.
- Only one correct answer per question.
- The answer must exactly match one of the options.
- Questions must be educational and factually correct.
"""

    models_to_try = [
        MODEL,
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash"
    ]

    # Remove duplicate model names
    models_to_try = list(dict.fromkeys(models_to_try))

    last_error = None

    for model_name in models_to_try:

        for attempt in range(4):

            try:
                print(
                    f"Trying Gemini model: {model_name} "
                    f"(attempt {attempt + 1}/4)"
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                text = response.text.strip()

                if text.startswith("```"):
                    text = text.replace("```json", "")
                    text = text.replace("```", "")
                    text = text.strip()

                quiz = json.loads(text)

                return quiz

            except Exception as exc:

                last_error = exc
                error_text = str(exc)

                print(f"Gemini error: {error_text}")

                # Retry only temporary 503 errors
                if "503" in error_text or "UNAVAILABLE" in error_text:

                    if attempt < 3:
                        wait_time = (2 ** attempt) + random.uniform(0, 0.5)

                        print(
                            f"Gemini temporarily unavailable. "
                            f"Retrying in {wait_time:.1f} seconds..."
                        )

                        time.sleep(wait_time)
                        continue

                    # Try next model
                    print(
                        f"Model {model_name} failed after 4 attempts. "
                        f"Trying next model..."
                    )
                    break

                # Other errors should not be silently retried
                raise

    raise RuntimeError(
        f"Gemini quiz generation failed: {last_error}"
    )