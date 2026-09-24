import os
import time
import random

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=API_KEY)

PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Automatic fallback models
MODELS = [
    PRIMARY_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
]

# Remove duplicate model names
MODELS = list(dict.fromkeys(MODELS))


def answer_question(question: str) -> str:

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    prompt = f"""
You are EduGenie, an AI learning assistant.

Answer the student's question clearly and accurately.

Question:
{question}

Instructions:
- Give a simple and understandable answer.
- Explain important concepts clearly.
- Use examples when useful.
- Keep the answer suitable for a college student.
- Do not mention that you are an AI unless necessary.
"""

    last_error = None

    for model in MODELS:

        for attempt in range(2):

            try:

                print(
                    f"Trying Q&A model: {model} "
                    f"(attempt {attempt + 1}/2)"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if not response.text:
                    raise RuntimeError("Gemini returned an empty response.")

                print(f"Q&A succeeded using: {model}")

                return response.text.strip()

            except Exception as exc:

                last_error = exc

                print(
                    f"Q&A failed with {model}: {exc}"
                )

                error_text = str(exc)

                # Retry only temporary server/model problems
                is_temporary = any(
                    code in error_text
                    for code in [
                        "503",
                        "UNAVAILABLE",
                        "500",
                        "502",
                        "504"
                    ]
                )

                if not is_temporary:
                    raise

                if attempt == 0:
                    time.sleep(
                        1 + random.uniform(0, 0.5)
                    )

        print(
            f"Switching to next Gemini model..."
        )

    raise RuntimeError(
        f"All Gemini models failed. Last error: {last_error}"
    )