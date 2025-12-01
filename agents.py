"""
Agent implementations (lightweight) used in InterviewForge.

Agents:
- ResumeAgent
- RoundGeneratorAgent
- InterviewAgent
- CritiqueAgent
- StudyPlanAgent
- EmailAgent
"""

from typing import Dict, List, Any
from tools import llm_call
import json
import logging

logger = logging.getLogger("interviewforge.agents")
logging.basicConfig(level=logging.INFO)


# -------------------------
# Resume Agent
# -------------------------
class ResumeAgent:
    def parse(self, resume_text: str) -> Dict[str, Any]:
        prompt = f"Extract structured fields from this resume text (JSON):\n\n{resume_text}"
        resp = llm_call(prompt, system="Extract resume fields to JSON")

        if resp is None:
            logger.error("llm_call returned None in ResumeAgent.parse")
            return {"raw": None, "text_preview": resume_text[:300]}

        try:
            parsed = json.loads(resp)
            return parsed
        except Exception:
            return {"raw": resp, "text_preview": resume_text[:300]}


# -------------------------
# Round Generator Agent
# -------------------------
class RoundGeneratorAgent:
    def generate(self, parsed_resume: Dict[str, Any], role: str) -> Dict[str, Any]:
        prompt = f"Generate interview rounds for role '{role}' given this resume: {parsed_resume}. Return JSON with rounds and questions."
        resp = llm_call(prompt, system="Generate interview rounds")

        if resp is None:
            logger.error("llm_call returned None in RoundGeneratorAgent.generate, using fallback.")
            return {"Round 1": {"name": "Technical", "questions": ["Describe project X."]}}

        try:
            return json.loads(resp)
        except Exception:
            return {"Round 1": {"name": "Technical", "questions": ["Describe project X."]}}


# -------------------------
# Interview Agent
# -------------------------
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


# -------------------------
# Critique Agent
# -------------------------
class CritiqueAgent:
    def critique(self, question: str, answer: str, resume_profile: Dict[str, Any]) -> Dict[str, Any]:

        prompt = (
            f"Critique this answer to the question. Provide a numeric score (1-10) and short actionable feedback.\n"
            f"Question: {question}\nAnswer: {answer}\nResumeProfile: {resume_profile}"
        )
        resp = llm_call(prompt, system="Critique answer and give score+feedback")

        if resp is None:
            logger.error("llm_call returned None in CritiqueAgent. Returning fallback critique.")
            return {"raw": None, "score": None, "feedback": "No critique generated."}

        out = {"raw": resp}

        low = resp.lower() if isinstance(resp, str) else ""

        if "score" in low:
            try:
                digits = "".join(ch for ch in resp if ch.isdigit())
                if digits:
                    out["score"] = int(digits[:2])
                else:
                    out["score"] = None
            except Exception:
                out["score"] = None
        else:
            out["score"] = None

        return out


# -------------------------
# Study Plan Agent
# -------------------------
class StudyPlanAgent:
    def create_plan_and_flashcards(self, critiques: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = f"Given these critiques: {critiques}, produce a 7-day prioritized study plan and 10 flashcards (JSON)."
        resp = llm_call(prompt, system="Create study plan and flashcards")

        if resp is None:
            logger.error("llm_call returned None in StudyPlanAgent, using fallback.")
            return {
                "study_plan": "Practice key weaknesses identified in critiques.",
                "flashcards": []
            }

        try:
            return json.loads(resp)
        except Exception:
            return {
                "study_plan": "Week 1: practice arrays; Week 2: system design",
                "flashcards": [
                    {"q": "What is idempotency?", "a": "An operation that can be applied multiple times without changing the result."}
                ]
            }


# -------------------------
# Email Agent
# -------------------------
class EmailAgent:
    def draft(self, name: str, role: str, summary: str) -> str:
        prompt = f"Draft a professional follow-up email for {name} after a mock interview for {role}. Include summary: {summary}"
        resp = llm_call(prompt, system="Draft follow-up email")

        if resp is None:
            logger.error("llm_call returned None in EmailAgent, using fallback email text.")
            return f"Hello,\n\nThank you for the interview for the {role} position.\n\nRegards,\n{name}"

        return resp
