
"""
Tools & LLM wrapper for InterviewForge.

This file contains:
- llm_call(): uses Gemini (via google-genai) when GOOGLE_API_KEY is set,
  otherwise a deterministic stub for offline demo.
- helper tool wrappers used by agents.
"""

import os
import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger("interviewforge.tools")
logging.basicConfig(level=logging.INFO)

# Try importing google genai client if available
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False
    logger.info("google-genai not available — llm_call will use a stub.")

# -- LLM wrapper --------------------------------------------------------------
def llm_call(prompt: str, system: str = None, model: str = "gemini-2.0-flash", temperature: float = 0.2) -> str:
    """
    Unified LLM call wrapper.
    If GOOGLE_API_KEY is present and google-genai is installed, it calls Gemini.
    Otherwise returns a deterministic stubbed response useful for demos and tests.

    IMPORTANT: Do NOT put API keys into code. Use env vars or Kaggle secrets.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key and GENAI_AVAILABLE:
        client = genai.Client(api_key=api_key)
        system_msg = system or ""
        try:
            response = client.models.generate_content(
                model=model,
                contents=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                generation_config=types.GenerationConfig(temperature=temperature),
            )
            # response.text gives the textual content
            return response.text
        except Exception as e:
            logger.warning(f"LLM call failed: {e}. Falling back to stub.")
    # Fallback stub (deterministic, simple)
    lower = prompt.lower()
    if "extract" in lower and "resume" in lower:
        # Return a simple JSON string
        stub = {
            "name": "Jane Doe",
            "years_experience": 3,
            "skills": ["python", "sql", "flask"],
            "projects": ["project A - ETL", "project B - API"],
            "highlights": ["reduced latency by 30%"]
        }
        return json.dumps(stub)
    if "generate" in lower and "round" in lower:
        stub = {
            "Round 1": {"name": "Technical", "questions": [
                "Write a function to find two numbers that sum to target.",
                "Explain a time complexity trade-off you considered."
            ]},
            "Round 2": {"name": "Behavioral", "questions": [
                "Tell me about a time you led a project.",
                "Describe a time you handled conflict."
            ]},
            "Round 3": {"name": "System Design", "questions": [
                "Design a URL shortener service."
            ]}
        }
        return json.dumps(stub)
    if "critique" in lower or "feedback" in lower:
        return "Score: 6/10. Feedback: Good structure; add metrics and edge-case discussion."
    if "study plan" in lower:
        return "Week 1: arrays & hashing; Week 2: system design patterns; Week 3: behavioral STAR practice"
    if "flashcard" in lower:
        return json.dumps([
            {"q": "What is idempotency?", "a": "Operation can be applied multiple times without changing the result beyond the initial application."},
            {"q": "Time complexity of quicksort (avg)?", "a": "O(n log n)"}
        ])
    if "follow-up" in lower or "email" in lower:
        return "Hi [Interviewer],\nThanks for the mock interview. I appreciated the feedback. Best, Jane"
    # generic fallback
    return "LLM_STUB: (no full model available) " + prompt[:200]
