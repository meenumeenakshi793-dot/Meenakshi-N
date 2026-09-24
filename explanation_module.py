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

MODELS = [
    PRIMARY_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
]

MODELS = list(dict.fromkeys(MODELS))


def explain_topic(topic: str) -> str:

    topic = topic.strip()

    if not topic:
        raise ValueError("Topic cannot be empty.")

    prompt = f"""
You are EduGenie, an AI learning assistant.

Explain the following topic clearly for a college student:

Topic:
{topic}

Instructions:
- Start with a simple definition.
- Explain the concept clearly.
- Use simple language.
- Include important points.
- Give a real-world example when useful.
- Use headings and bullet points where appropriate.
- Make the explanation educational and easy to understand.
"""

    last_error = None

    for model in MODELS:

        for attempt in range(2):

            try:

                print(
                    f"Trying Explanation model: {model} "
                    f"(attempt {attempt + 1}/2)"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                print(
                    f"Explanation succeeded using: {model}"
                )

                return response.text.strip()

            except Exception as exc:

                last_error = exc

                print(
                    f"Explanation failed with {model}: {exc}"
                )

                error_text = str(exc)

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

        print("Switching to next Gemini model...")

    raise RuntimeError(
        f"All Gemini models failed. Last error: {last_error}"
    )