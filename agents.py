
"""
Agent implementations (lightweight) used in InterviewForge.

Agents:
- ResumeAgent: parse resume text into structured profile
- RoundGeneratorAgent: create question rounds
- InterviewAgent: interactive/dummy loop asking questions
- CritiqueAgent: evaluate individual answers
- StudyPlanAgent: create study plan and flashcards
- EmailAgent: draft follow-up email
"""

from typing import Dict, List, Any
from tools import llm_call
import json
import logging

logger = logging.getLogger("interviewforge.agents")
logging.basicConfig(level=logging.INFO)

# -----------------------
# Resume Agent
# -----------------------
class ResumeAgent:
    def parse(self, resume_text: str) -> Dict[str, Any]:
        prompt = f"Extract structured fields from this resume text (JSON):\n\n{resume_text}"
        resp = llm_call(prompt, system="Extract resume fields to JSON")
        try:
            parsed = json.loads(resp)
            return parsed
        except Exception:
            # fallback: return raw string
            return {"raw": resp, "text_preview": resume_text[:300]}

# -----------------------
# Round Generator Agent
# -----------------------
class RoundGeneratorAgent:
    def generate(self, parsed_resume: Dict[str, Any], role: str) -> Dict[str, Any]:
        prompt = f"Generate interview rounds for role '{role}' given this resume: {parsed_resume}. Return JSON with rounds and questions."
        resp = llm_call(prompt, system="Generate interview rounds")
        try:
            return json.loads(resp)
        except Exception:
            # fallback attempt if stub returned as string
            return {"Round 1": {"name": "Technical", "questions": ["Describe project X."]}}

# -----------------------
# Interview Agent (Loop)
# -----------------------
class InterviewAgent:
    def __init__(self, interactive: bool = True):
        self.interactive = interactive

    def run_round(self, round_name: str, questions: List[str]) -> List[Dict[str, str]]:
        qa_pairs = []
        for q in questions:
            print(f"\nQuestion ({round_name}): {q}")
            if self.interactive:
                ans = input("Your answer: ")
            else:
                ans = f"Demo answer for: {q}"
            qa_pairs.append({"question": q, "answer": ans})
        return qa_pairs

# -----------------------
# Critique / Evaluation Agent
# -----------------------
class CritiqueAgent:
    def critique(self, question: str, answer: str, resume_profile: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Critique this answer to the question. Provide a numeric score (1-10) and short actionable feedback.\nQuestion: {question}\nAnswer: {answer}\nResumeProfile: {resume_profile}"
        resp = llm_call(prompt, system="Critique answer and give score+feedback")
        # try parse simple "Score: X. Feedback: ...", otherwise return raw.
        out = {"raw": resp}
        low = resp.lower()
        if "score" in low:
            # crude extraction
            try:
                s = int(''.join(ch for ch in resp if ch.isdigit())[:2])
                out["score"] = s
            except Exception:
                out["score"] = None
        return out

# -----------------------
# StudyPlan Agent
# -----------------------
class StudyPlanAgent:
    def create_plan_and_flashcards(self, critiques: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = f"Given these critiques: {critiques}, produce a 7-day prioritized study plan and 10 flashcards (JSON)."
        resp = llm_call(prompt, system="Create study plan and flashcards")
        try:
            return json.loads(resp)
        except Exception:
            # fallback: small structured object
            return {
                "study_plan": "Week 1: practice arrays; Week 2: system design",
                "flashcards": [
                    {"q": "What is idempotency?", "a": "Idempotent op..."},
                    {"q": "Average case quicksort?", "a": "O(n log n)"}
                ]
            }

# -----------------------
# Email Agent
# -----------------------
class EmailAgent:
    def draft(self, name: str, role: str, summary: str) -> str:
        prompt = f"Draft a professional follow-up email for {name} after a mock interview for {role}. Include summary: {summary}"
        return llm_call(prompt, system="Draft follow-up email")
