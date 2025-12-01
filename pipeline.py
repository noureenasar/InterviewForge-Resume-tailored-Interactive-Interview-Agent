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
from memory import MemoryBank, InMemorySession
import pathlib
import json
import logging

logger = logging.getLogger("interviewforge.pipeline")
logging.basicConfig(level=logging.INFO)

OUT_DIR = pathlib.Path("interviewforge_output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

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
#1.Parse resume
        logger.info("Parsing resume...")
        profile = self.resume_agent.parse(resume_text)

#2.Generate rounds
        logger.info("Generating rounds...")
        rounds = self.round_gen.generate(profile, role)

#3.Run interview rounds
        transcript = []
        for r_key, r_info in rounds.items():
            round_name = r_info.get("name", r_key)
            questions = r_info.get("questions", [])
            logger.info(f"Running round {round_name} with {len(questions)} qns.")
            qa_pairs = self.interview_agent.run_round(round_name, questions)
            transcript.extend(qa_pairs)

#4.Critique answers
        critiques = []
        for qa in transcript:
            c = self.critique_agent.critique(qa["question"], qa["answer"], profile)
            critiques.append({"question": qa["question"], "answer": qa["answer"], "critique": c})

#5.Study plan & flashcards
        study_obj = self.study_agent.create_plan_and_flashcards(critiques)

#6.Follow-up email
        name = profile.get("name", "Candidate")
        summary = "Summary: " + str([c.get("critique", {}).get("score") for c in critiques])
        email_text = self.email_agent.draft(name, role, summary)

#7.Save run
        run_summary = {
            "profile": profile,
            "role": role,
            "rounds": rounds,
            "transcript": transcript,
            "critiques": critiques,
            "study": study_obj,
            "follow_up_email": email_text
        }
        self.memory.save_run(run_summary)
        # Write output files too
        OUT_DIR.joinpath("last_run.json").write_text(json.dumps(run_summary, indent=2))
        logger.info(f"Run completed. Outputs written to {OUT_DIR.resolve()}")
        return run_summary
