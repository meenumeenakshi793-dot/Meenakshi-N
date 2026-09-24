async function showResult(elementId, response) {
    const element = document.getElementById(elementId);

    if (!response.ok) {
        const errorText = await response.text();
        element.innerHTML = `<p class="error">Error: ${errorText}</p>`;
        return;
    }

    const data = await response.json();

    // Quiz response
    if (elementId === "quizResult" && data.quiz) {
        const quiz = data.quiz;

        element.innerHTML = `
            <div class="quiz-card">
                <h3>📝 Quiz</h3>
                <div class="quiz-question">
                    <strong>${quiz.question}</strong>
                </div>
            </div>
        `;

        return;
    }

    // Normal response
    let output = "";

    if (typeof data === "string") {
        output = data;
    } else if (Array.isArray(data)) {
        output = JSON.stringify(data, null, 2);
    } else {
        output = Object.entries(data)
            .map(([key, value]) => {
                if (Array.isArray(value) || typeof value === "object") {
                    return `<strong>${key}:</strong>
                            <pre>${JSON.stringify(value, null, 2)}</pre>`;
                }

                return `<strong>${key}:</strong> ${value}`;
            })
            .join("<br>");
    }

    element.innerHTML = `<div class="success">${output}</div>`;
}

/* =========================
   Q&A
========================= */

async function askQuestion() {
    const question = document.getElementById("question").value.trim();

    if (!question) {
        alert("Please enter a question.");
        return;
    }

    const result = document.getElementById("qaResult");
    result.innerHTML = "⏳ Getting answer...";

    try {
        const response = await fetch("/qa", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        await showResult("qaResult", response);

    } catch (error) {
        result.innerHTML = `<p class="error">Connection error: ${error.message}</p>`;
    }
}


/* =========================
   EXPLAIN
========================= */

async function explainTopic() {
    const topic = document.getElementById("explainTopic").value.trim();

    if (!topic) {
        alert("Please enter a topic.");
        return;
    }

    const result = document.getElementById("explainResult");
    result.innerHTML = "⏳ Generating explanation...";

    try {
        const response = await fetch("/explain", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                topic: topic
            })
        });

        await showResult("explainResult", response);

    } catch (error) {
        result.innerHTML = `<p class="error">Connection error: ${error.message}</p>`;
    }
}


/* =========================
   QUIZ
========================= */
async function generateQuiz() {
    const topic = document.getElementById("quizTopic").value.trim();

    if (!topic) {
        alert("Please enter a quiz topic.");
        return;
    }

    const result = document.getElementById("quizResult");

    result.innerHTML = "⏳ Generating quiz...";

    try {
        const response = await fetch("/quiz", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: topic
            })
        });

        const data = await response.json();

        if (!response.ok) {
            result.innerHTML = `
                <p class="error">
                    Error: ${data.detail || "Quiz generation failed."}
                </p>
            `;
            return;
        }

        // Backend returns: { quiz: {...} }
        const quiz = data.quiz || data;

        const questions = quiz.questions || [];

        if (!questions.length) {
            result.innerHTML = `
                <p class="error">
                    No questions were generated.
                </p>
            `;
            return;
        }

        let html = `
            <h2>${quiz.title || topic + " Quiz"}</h2>
            <div class="quiz-container">
        `;

        questions.forEach((q, index) => {
            html += `
                <div class="quiz-question">
                    <h3>${index + 1}. ${q.question}</h3>

                    <div class="quiz-options">
                        ${q.options.map((option, optionIndex) => `
                            <label>
                                <input
                                    type="radio"
                                    name="question-${index}"
                                    value="${optionIndex}"
                                >
                                ${option}
                            </label>
                        `).join("")}
                    </div>

                    <p
                        id="answer-${index}"
                        class="correct-answer"
                        style="display:none;"
                    >
                        Correct Answer: ${q.answer}
                    </p>
                </div>
            `;
        });

        html += `
            </div>

            <button
                type="button"
                onclick="showAnswers()"
                class="quiz-answer-button"
            >
                Show Answers
            </button>
        `;

        result.innerHTML = html;

        // Store quiz data for Show Answers button
        window.currentQuiz = quiz;

    } catch (error) {
        console.error("Quiz error:", error);

        result.innerHTML = `
            <p class="error">
                Error generating quiz: ${error.message}
            </p>
        `;
    }
}


function showAnswers() {
    if (!window.currentQuiz || !window.currentQuiz.questions) {
        return;
    }

    window.currentQuiz.questions.forEach((q, index) => {
        const answerElement = document.getElementById(`answer-${index}`);

        if (answerElement) {
            answerElement.style.display = "block";
        }
    });
}
/* =========================
   LEARNING RECOMMENDATIONS
========================= */

async function getRecommendations() {
    const topic = document
        .getElementById("recommendationTopic")
        .value
        .trim();

    if (!topic) {
        alert("Please enter a topic.");
        return;
    }

    const result = document.getElementById("recommendationResult");
    result.innerHTML = "⏳ Finding recommendations...";

    try {
        const response = await fetch(
            `/learn/recommendations?topic=${encodeURIComponent(topic)}`
        );

        await showResult("recommendationResult", response);

    } catch (error) {
        result.innerHTML = `<p class="error">Connection error: ${error.message}</p>`;
    }
}
async function summarizeText() {
    const text = document.getElementById("summaryText").value.trim();
    const result = document.getElementById("summaryResult");

    if (!text) {
        alert("Please enter text to summarize.");
        return;
    }

    result.innerHTML = "⏳ Summarizing...";

    try {
        const response = await fetch("/summarize", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text
            })
        });

        const data = await response.json();

        if (!response.ok) {
            result.innerHTML = `
                <p class="error">
                    Error: ${data.detail || "Summary generation failed."}
                </p>
            `;
            return;
        }

        const summary = data.summary || data;

        result.innerHTML = `
            <div class="success">
                <h3>Summary</h3>
                <p>${summary}</p>
            </div>
        `;

    } catch (error) {
        console.error("Summary error:", error);

        result.innerHTML = `
            <p class="error">
                Error generating summary: ${error.message}
            </p>
        `;
    }
}