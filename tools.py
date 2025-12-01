"""
tools.py
Utility functions including llm_call.
Provides a safe stub if no real LLM backend is available.
"""

import logging
import json

logger = logging.getLogger("interviewforge.tools")
logging.basicConfig(level=logging.INFO)

# ------------------------------------------------------------------
# Main LLM CALL FUNCTION
# ------------------------------------------------------------------
def llm_call(prompt: str, system: str = None) -> str:
    """
    Safe LLM wrapper.
    If no real model is integrated, returns a stub deterministic output.
    NEVER returns None.
    """

    logger.info(f"[llm_call] SYSTEM={system}, PROMPT_LEN={len(prompt)}")

    # ---------------------------------------------------------------
    # TODO: If using a real LLM (OpenAI, Gemini, etc), add integration here.
    # ---------------------------------------------------------------

    # Fallback stub response (to prevent crashes)
    # You can improve the stubs later.
    if "Extract resume" in (system or ""):
        return json.dumps({
            "name": "Sample User",
            "skills": ["Python", "Data Analysis"],
            "experience": ["Intern at XYZ", "Project: Data Pipeline"]
        })

    if "Generate interview rounds" in (system or ""):
        return json.dumps({
            "Round 1": {
                "name": "Technical",
                "questions": [
                    "Explain a project you worked on.",
                    "What is your experience with Python?"
                ]
            },
            "Round 2": {
                "name": "Behavioral",
                "questions": [
                    "Tell me about a challenge you overcame."
                ]
            }
        })

    if "Critique answer" in (system or ""):
        return "Score: 7. Feedback: More detail needed."

    if "Create study plan" in (system or ""):
        return json.dumps({
            "study_plan": ["Day 1: Review basics", "Day 2: Practice coding"],
            "flashcards": [
                {"q": "What is OOP?", "a": "Object Oriented Programming"},
                {"q": "Define REST.", "a": "Representational State Transfer"}
            ]
        })

    if "Draft follow-up email" in (system or ""):
        return (
            f"Hello,\n\nThank you for the opportunity. Here is the summary:\n"
            f"{prompt}\n\nRegards,\nCandidate"
        )

    # DEFAULT STUB
    return "Default LLM Stub Response"
