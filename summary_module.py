import os
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


def summarize_text(text: str) -> str:
    text = text.strip()

    if not text:
        raise ValueError("Text cannot be empty.")

    prompt = f"""
Summarize the following text clearly and concisely.

Text:
{text}

Requirements:
- Keep the important information.
- Remove unnecessary repetition.
- Use simple student-friendly English.
- Write a short paragraph.
- Do not add information that is not in the original text.
"""

    models_to_try = [
        MODEL,
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash"
    ]

    models_to_try = list(dict.fromkeys(models_to_try))

    last_error = None

    for model_name in models_to_try:

        for attempt in range(4):

            try:
                print(
                    f"Trying Summary model: {model_name} "
                    f"(attempt {attempt + 1}/4)"
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                return response.text.strip()

            except Exception as exc:

                last_error = exc
                error_text = str(exc)

                print(f"Summary Gemini error: {error_text}")

                if (
                       "503" in error_text
                        or "UNAVAILABLE" in error_text
                        or "10053" in error_text
                        or "10054" in error_text
                        or "Connection" in error_text
                        or "connection" in error_text
                    ):
                    if attempt < 3:
                        wait_time = (2 ** attempt) + random.uniform(0, 0.5)

                        print(
                            f"Retrying in {wait_time:.1f} seconds..."
                        )

                        time.sleep(wait_time)
                        continue

                    print(
                        f"{model_name} failed. Trying next model..."
                    )
                    break

                raise

    raise RuntimeError(
        f"Gemini summary generation failed: {last_error}"
    )