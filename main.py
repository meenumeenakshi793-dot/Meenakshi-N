from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from explanation_module import explain_topic
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations


app = FastAPI(
    title="EduGenie - Google Gemini Powered Learning Assistant",
    version="1.0.0",
    description=(
        "AI-powered educational assistant based on the EduGenie "
        "project documentation."
    ),
)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------

class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=30000
    )


class TopicRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=10000
    )


# ---------------------------------------------------------
# Home Page
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    index_file = BASE_DIR / "templates" / "index.html"
    return HTMLResponse(
        content=index_file.read_text(encoding="utf-8")
    )


# ---------------------------------------------------------
# Q&A
# ---------------------------------------------------------

@app.get("/qa")
async def qa_get(question: str = ""):

    question = question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please provide a question."
        )

    try:
        answer = answer_question(question)

        return {
            "answer": answer
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Q&A service error: {exc}"
        ) from exc


@app.post("/qa")
async def qa_post(payload: QuestionRequest):

    try:
        answer = answer_question(
            payload.question.strip()
        )

        return {
            "answer": answer
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Q&A service error: {exc}"
        ) from exc


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

@app.post("/explain")
async def explain(payload: TopicRequest):

    try:
        topic = payload.topic.strip()

        explanation = explain_topic(topic)

        return {
            "topic": topic,
            "explanation": explanation
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Explanation service error: {exc}"
        ) from exc


# ---------------------------------------------------------
# Quiz
# ---------------------------------------------------------

@app.post("/quiz")
async def quiz(payload: TextRequest):

    try:
        text = payload.text.strip()

        quiz = generate_quiz(text)

        return {
            "quiz": quiz
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Quiz service error: {exc}"
        ) from exc


# ---------------------------------------------------------
# Summarization
# ---------------------------------------------------------

@app.post("/summarize")
async def summarize(payload: TextRequest):

    try:
        text = payload.text.strip()

        summary = summarize_text(text)

        return {
            "summary": summary
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Summary service error: {exc}"
        ) from exc


# ---------------------------------------------------------
# Learning Recommendations
# ---------------------------------------------------------

@app.get("/learn/recommendations")
async def learning_recommendations(
    topic: str = ""
):

    topic = topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Please provide a topic."
        )

    try:

        recommendation = get_learning_recommendations(
            topic
        )

        return {
            "topic": topic,
            "recommendation": recommendation
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Learning-path service error: {exc}"
        ) from exc


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "EduGenie"
    }
@app.get("/")
async def home():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        html = file.read()

    return HTMLResponse(content=html)