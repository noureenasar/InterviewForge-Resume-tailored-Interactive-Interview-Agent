"""
Pipeline / Orchestrator for InterviewForge.
Handles the end-to-end flow and saves results via MemoryBank.
"""

from agents import (
    ResumeAgent,
    RoundGeneratorAgent,
    InterviewAgent,
    CritiqueAgent,
    StudyPlanAgent,
    EmailAgent,
)
from memory import MemoryBank
import pathlib
import json
import logging

logger = logging.getLogger("interviewforge.pipeline")
logging.basicConfig(level=logging.INFO)

OUT_DIR = pathlib.Path("interviewforge_output")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_text(x, default=""):
    """
    Ensures we never propagate None into downstream steps.
    """
    if x is None:
        return default
    if isinstance(x, str):
        return x
    return str(x)


class Orchestrator:
    def __init__(self, interactive: bool = True):
        self.resume_agent = ResumeAgent()
        self.round_gen = RoundGeneratorAgent()
        self.interview_agent = InterviewAgent(interactive=interactive)
        self.critique_agent = CritiqueAgent()
        self.study_agent = StudyPlanAgent()
        self.email_agent = EmailAgent()
        self.memory = MemoryBank()

    def run(self, resume_text: str, role: str) -> dict:
        # -------------------------
        # 1. Parse Resume
        # -------------------------
        logger.info("Parsing resume...")
        profile_raw = self.resume_agent.parse(resume_text)
        profile = {}

        try:
            if isinstance(profile_raw, str):
                profile = json.loads(profile_raw)
            else:
                profile = profile_raw
        except Exception:
            logger.warning("ResumeAgent returned non-JSON output. Wrapping fallback.")
            profile = {"raw_output": safe_text(profile_raw)}

        # Ensure required fields exist
        profile.setdefault("name", "Candidate")

        # -------------------------
        # 2. Generate rounds
        # -------------------------
        logger.info("Generating rounds...")
        rounds_raw = self.round_gen.generate(profile, role)

        try:
            if isinstance(rounds_raw, str):
                rounds = json.loads(rounds_raw)
            else:
                rounds = rounds_raw
        except Exception:
            logger.warning("RoundGenerator returned non-JSON; using fallback structure.")
            rounds = {"Round 1": {"name": "General", "questions": []}}

        # -------------------------
        # 3. Conduct Interview
        # -------------------------
        transcript = []

        for r_key, r_info in rounds.items():
            round_name = r_info.get("name", r_key)
            questions = r_info.get("questions", [])

            logger.info(f"Running round {round_name} with {len(questions)} questions...")

            qa_pairs = self.interview_agent.run_round(round_name, questions)

            for qa in qa_pairs:
                # Ensure question/answer exist
                qa["question"] = safe_text(qa.get("question", ""))
                qa["answer"] = safe_text(qa.get("answer", ""))

            transcript.extend(qa_pairs)

        # -------------------------
        # 4. Critique Answers
        # -------------------------
        critiques = []
        for qa in transcript:
            critique_raw = self.critique_agent.critique(
                qa["question"], qa["answer"], profile
            )

            critique_text = safe_text(critique_raw, default="No critique generated.")

            critiques.append({
                "question": qa["question"],
                "answer": qa["answer"],
                "critique": critique_text,
            })

        # -------------------------
        # 5. Study Plan + Flashcards
        # -------------------------
        study_raw = self.study_agent.create_plan_and_flashcards(critiques)

        if isinstance(study_raw, str):
            try:
                study_obj = json.loads(study_raw)
            except Exception:
                study_obj = {"raw_output": study_raw}
        else:
            study_obj = study_raw

        # -------------------------
        # 6. Draft Follow-up Email
        # -------------------------
        name = profile.get("name", "Candidate")

        summary = (
            "Summary of critiques:\n"
            + "\n".join([safe_text(c["critique"]) for c in critiques])
        )

        email_text = self.email_agent.draft(name, role, summary)
        email_text = safe_text(email_text)

        # -------------------------
        # 7. Save & Return Final Output
        # -------------------------
        run_summary = {
            "profile": profile,
            "role": role,
            "rounds": rounds,
            "transcript": transcript,
            "critiques": critiques,
            "study": study_obj,
            "follow_up_email": email_text,
        }

        self.memory.save_run(run_summary)

        OUT_DIR.joinpath("last_run.json").write_text(
            json.dumps(run_summary, indent=2)
        )

        logger.info(f"Run completed. Outputs written to {OUT_DIR.resolve()}")

        return run_summary
