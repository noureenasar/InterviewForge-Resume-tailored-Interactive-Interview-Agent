# interviewforge.py
"""
InterviewForge - Resume-tailored Interactive Interview Agent (scaffold)

Usage:
  # interactive (type answers)
  python interviewforge.py --resume ./sample_resume.txt --role "Data Scientist" --interactive

  # quick demo (non-interactive)
  python interviewforge.py --resume ./sample_resume.txt --role "Data Scientist" --demo

NOTE: Replace llm_call() with your LLM provider (Gemini/OpenAI). Do NOT place API keys in repo.
"""

import asyncio
import json
import logging
import os
import pathlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# -------------------------
# Config & logging
# -------------------------
OUTPUT_DIR = pathlib.Path("interviewforge_output")
MEMORY_FILE = OUTPUT_DIR / "memory_bank.json"
OUTPUT_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("InterviewForge")

# -------------------------
# Memory & Session
# -------------------------
class MemoryBank:
    """Persistent lightweight memory bank (JSON). Stores past interview runs."""
    def __init__(self, path=MEMORY_FILE):
        self.path = pathlib.Path(path)
        if self.path.exists():
            self._data = json.loads(self.path.read_text())
        else:
            self._data = {"runs": []}

    def save_run(self, run_summary: Dict[str, Any]):
        self._data["runs"].append(run_summary)
        self.path.write_text(json.dumps(self._data, indent=2))

    def list_runs(self):
        return self._data["runs"]

class InMemorySession:
    """Short-lived session state for the active interview run."""
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.questions = []
        self.answers = []
        self.current_q_index = 0
        self.checkpoints = []  # simple list of state snapshots

    def checkpoint(self):
        snap = {
            "time": time.time(),
            "q_index": self.current_q_index,
            "questions": self.questions.copy(),
            "answers": self.answers.copy()
        }
        self.checkpoints.append(snap)
        return snap

# -------------------------
# A2A messaging
# -------------------------
@dataclass
class A2AMessage:
    sender: str
    msg_type: str
    payload: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

# -------------------------
# Tools (custom)
# -------------------------
class FileTool:
    @staticmethod
    def write_text(path: pathlib.Path, text: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        logger.info(f"[FileTool] Wrote {path}")

    @staticmethod
    def read_text(path: pathlib.Path) -> str:
        return path.read_text()

class TimerTool:
    @staticmethod
    def now_ms():
        return int(time.time() * 1000)

class GitTool:
    @staticmethod
    def note_run(path: pathlib.Path, msg: str):
        # placeholder for later GitHub integration
        logger.info(f"[GitTool] (simulate) note: {msg} -> {path}")

# -------------------------
# LLM call placeholder
# -------------------------
def llm_call(prompt: str, role: str = "assistant") -> str:
    """
    Replace with real LLM API. Keep API keys in environment variables.
    For the scaffold, this returns deterministic simple outputs to demo flow.
    """
    logger.debug(f"[LLM] Prompt truncated: {prompt[:240]}")
    # Provide useful simple stubs:
    if "parse resume" in prompt.lower():
        return "ParsedResume: name=Jane Doe; years_experience=3; skills=[python, ml, sql]; highlights=[project A]"
    if "generate rounds" in prompt.lower():
        # produce JSON-like plan
        return json.dumps([
            {"round": "behavioral", "focus": "culture-fit, teamwork", "questions": [
                "Tell me about a time you disagreed with a teammate.",
                "Describe a high-pressure situation and how you handled it."
            ]},
            {"round": "technical-coding", "focus": "algorithms, python", "questions": [
                "Given an array, find two numbers that add to target.",
                "Implement LRU cache."
            ]},
            {"round": "system-design", "focus": "design principles", "questions": [
                "Design a URL shortening service."
            ]}
        ], indent=2)
    if "critique answer" in prompt.lower():
        return "Score: 6/10. Feedback: Good structure, but missing complexity discussion and performance tradeoffs. Suggest: mention edge cases and complexity."
    if "study plan" in prompt.lower():
        return "- Week 1: algorithms practice (arrays, hashing)\n- Week 2: system design basics\n- Week 3: behavioral STAR practice\n"
    if "flashcards" in prompt.lower():
        return json.dumps([
            {"q": "What is time complexity of quicksort average?", "a": "O(n log n)"},
            {"q": "Define LRU cache", "a": "Cache eviction policy that removes least recently used item"}
        ], indent=2)
    if "draft follow-up email" in prompt.lower():
        return "Hi [Interviewer],\nThanks for the time. I enjoyed discussing the role and projects. Attached is my portfolio. Best, Jane"
    # fallback
    return "LLM: placeholder"

# -------------------------
# Agents
# -------------------------
class OrchestratorAgent:
    """Coordinates the whole pipeline, checkpoints progress, and saves run summary."""
    def __init__(self, memory: MemoryBank):
        self.memory = memory
        self.run_id = str(uuid.uuid4())
        self.session = InMemorySession(self.run_id)
        self.metrics = {"questions_asked": 0, "critiques": 0}
        logger.info(f"[Orchestrator] starting run {self.run_id}")

    async def run(self, resume_path: Optional[pathlib.Path], resume_mode: bool, resume_index: int,
                  resume_answers: Optional[List[str]], resume_checkpoints: Optional[List[Dict[str,Any]]],
                  resume_force: bool,
                  resume_demo_brief: Dict[str,str],
                  interactive: bool = True):
        start_time = time.time()
        # 0. If resume data present, restore
        if resume_mode and resume_path:
            logger.info("[Orchestrator] Resuming from checkpoint")
            self._restore_checkpoint(resume_path, resume_index, resume_answers, resume_checkpoints)

        # 1. Parse resume
        parser = ResumeParserAgent()
        parsed = await parser.parse_resume(resume_demo_brief["resume_text"], resume_demo_brief["role"])

        # 2. Generate rounds (parallel sub-agents)
        round_gen = RoundGeneratorAgent()
        rounds = await round_gen.generate_rounds(parsed)

        # 3. Produce rubrics (simple heuristic)
        rubrics = self._generate_rubrics(rounds)

        # 4. Conduct interview (interactive loop or demo automated)
        interview_agent = InterviewAgent(session=self.session, interactive=interactive)
        interview_results = await interview_agent.conduct(rounds, rubrics)

        # 5. Critique answers
        critique_agent = CritiqueAgent()
        critiques = []
        for qa in interview_results["qa_pairs"]:
            critique = critique_agent.critique(qa["question"], qa["answer"], parsed)
            critiques.append({"question": qa["question"], "answer": qa["answer"], "critique": critique})
            self.metrics["critiques"] += 1

        # 6. Produce study plan & flashcards
        study_agent = StudyPlanAgent()
        study_plan = study_agent.create_plan(critiques, parsed)
        flash_agent = FlashcardAgent()
        flashcards = flash_agent.generate_flashcards(critiques, parsed)

        # 7. Draft follow-up email
        email_agent = EmailAgent()
        followup_email = email_agent.draft_email(parsed, resume_demo_brief["role"])

        # 8. Save outputs
        project_dir = OUTPUT_DIR / f"interview_{int(time.time())}"
        FileTool.write_text(project_dir / "interview_results.json", json.dumps(interview_results, indent=2))
        FileTool.write_text(project_dir / "critiques.json", json.dumps(critiques, indent=2))
        FileTool.write_text(project_dir / "study_plan.md", study_plan)
        FileTool.write_text(project_dir / "flashcards.json", flashcards)
        FileTool.write_text(project_dir / "followup_email.txt", followup_email)

        # 9. Save run to memory
        run_summary = {
            "run_id": self.run_id,
            "role": resume_demo_brief["role"],
            "timestamp": time.time(),
            "metrics": self.metrics,
            "summary": {
                "num_questions": len(interview_results["qa_pairs"])
            },
            "project_dir": str(project_dir)
        }
        self.memory.save_run(run_summary)
        duration = time.time() - start_time
        logger.info(f"[Orchestrator] finished run {self.run_id} in {duration:.2f}s")
        return {
            "run_summary": run_summary,
            "interview_results": interview_results,
            "critiques": critiques,
            "study_plan": study_plan,
            "flashcards": json.loads(flashcards),
            "followup_email": followup_email
        }

    def _restore_checkpoint(self, resume_path, resume_index, resume_answers, resume_checkpoints):
        # For the scaffold: if resume answers provided, restore into session
        if resume_answers:
            self.session.answers = resume_answers
            self.session.current_q_index = resume_index
        if resume_checkpoints:
            self.session.checkpoints = resume_checkpoints
        logger.info("[Orchestrator] restored session state")

    def _generate_rubrics(self, rounds):
        # Simple rubrics example: each question scored on structure, depth, examples (0-10)
        rubrics = {}
        for rnd in rounds:
            for q in rnd["questions"]:
                rubrics[q] = {"structure": 3, "depth": 3, "examples": 4}
        return rubrics

class ResumeParserAgent:
    async def parse_resume(self, resume_text: str, role: str) -> Dict[str, Any]:
        logger.info("[ResumeParser] parsing resume")
        prompt = f"Parse resume and extract skills, experiences, projects for role {role}. Tag: parse resume\n\n{resume_text}"
        resp = llm_call(prompt)
        # In real usage, parse structured response. Here we return demonstration dict.
        return {"raw_parse": resp, "name": "Jane Doe", "skills": ["python", "ml", "sql"], "years_experience": 3}

class RoundGeneratorAgent:
    async def generate_rounds(self, parsed_resume: Dict[str, Any]) -> List[Dict[str,Any]]:
        logger.info("[RoundGenerator] generating interview rounds (parallel)")
        # Simulate parallel producers for different round types
        async def gen_round(kind):
            await asyncio.sleep(0.2)
            prompt = f"Generate {kind} round questions for resume: {parsed_resume}"
            return llm_call(f"generate rounds for kind={kind}\n{prompt}")

        # We'll "parallelize" different high-level batches: behavioral, technical, system
        tasks = [gen_round("behavioral"), gen_round("technical"), gen_round("system-design")]
        outs = await asyncio.gather(*tasks)
        # Out contains JSON strings or serialized lists — for scaffold we call llm once to get full list
        all_rounds = json.loads(llm_call("generate rounds\nTag: generate rounds"))
        logger.info("[RoundGenerator] rounds produced")
        return all_rounds

class InterviewAgent:
    """Conducts the interview — either interactive (user types answers) or demo mode (auto answers)."""
    def __init__(self, session: InMemorySession, interactive: bool = True):
        self.session = session
        self.interactive = interactive

    async def conduct(self, rounds: List[Dict[str,Any]], rubrics: Dict[str,Any]) -> Dict[str,Any]:
        qa_pairs = []
        logger.info("[InterviewAgent] starting interview")
        # Flatten questions preserving round context
        for rnd in rounds:
            for q in rnd["questions"]:
                q_obj = {"round": rnd["round"], "focus": rnd.get("focus", ""), "question": q}
                # Ask question
                logger.info(f"[InterviewAgent] Q: {q}")
                start_ms = TimerTool.now_ms()
                if self.interactive:
                    answer = input(f"Q ({rnd['round']}): {q}\nYour answer: ")
                else:
                    # auto-demo answer: short canned response
                    answer = f"Demo answer to: {q}"
                    await asyncio.sleep(0.2)
                elapsed = TimerTool.now_ms() - start_ms
                # Save into session and checkpoint
                self.session.questions.append(q_obj)
                self.session.answers.append(answer)
                self.session.current_q_index += 1
                cp = self.session.checkpoint()
                logger.info(f"[InterviewAgent] saved checkpoint at q_index {self.session.current_q_index}")
                qa_pairs.append({"question": q, "answer": answer, "round": rnd["round"], "time_ms": elapsed})
        logger.info("[InterviewAgent] interview complete")
        return {"qa_pairs": qa_pairs, "session_checkpoints": self.session.checkpoints}

class CritiqueAgent:
    """Uses LLM to critique answers and produce rubric scores."""
    def critique(self, question: str, answer: str, parsed_resume: Dict[str,Any]) -> Dict[str,Any]:
        prompt = f"Critique answer. Question: {question}\nAnswer: {answer}\nResume: {parsed_resume}\n(Tag: critique answer)"
        resp = llm_call(prompt)
        # For scaffold, parse the stub text
        return {"raw": resp, "score": 6, "feedback": resp}

class StudyPlanAgent:
    def create_plan(self, critiques: List[Dict[str,Any]], parsed_resume: Dict[str,Any]) -> str:
        logger.info("[StudyPlanAgent] creating study plan")
        prompt = f"Create weekly study plan based on critiques: {critiques}"
        plan = llm_call("study plan\n" + prompt)
        return plan

class FlashcardAgent:
    def generate_flashcards(self, critiques: List[Dict[str,Any]], parsed_resume: Dict[str,Any]) -> str:
        logger.info("[FlashcardAgent] generating flashcards")
        prompt = f"Generate flashcards from critiques: {critiques}"
        cards = llm_call("flashcards\n" + prompt)
        return cards

class EmailAgent:
    def draft_email(self, parsed_resume: Dict[str,Any], role: str) -> str:
        logger.info("[EmailAgent] drafting follow-up email")
        prompt = f"Draft follow-up email for role {role} for candidate {parsed_resume.get('name')}"
        return llm_call("draft follow-up email\n" + prompt)

# -------------------------
# CLI & Runner
# -------------------------
import argparse

def load_resume(path: pathlib.Path) -> str:
    if not path.exists():
        return "Name: Jane Doe\nExperience: 3 years\nSkills: python, ml, sql\nProjects: project A"
    return path.read_text()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", type=str, required=False, default="sample_resume.txt", help="Path to resume text file")
    parser.add_argument("--role", type=str, required=True, help="Target role (e.g., Data Scientist)")
    parser.add_argument("--interactive", action="store_true", help="Run interactive Q&A (type answers)")
    parser.add_argument("--demo", action="store_true", help="Run demo (auto answers)")
    parser.add_argument("--resume_mode", action="store_true", help="Simulate resume from checkpoint")
    args = parser.parse_args()

    mem = MemoryBank()
    run_resume_path = pathlib.Path(args.resume)
    resume_text = load_resume(run_resume_path)
    run_info = {"resume_text": resume_text, "role": args.role}

    orch = OrchestratorAgent(mem)
    # For quick demo, non-interactive
    interactive = args.interactive
    demo_mode = args.demo
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        orch.run(
            resume_path=None,
            resume_mode=False,
            resume_index=0,
            resume_answers=None,
            resume_checkpoints=None,
            resume_force=False,
            resume_demo_brief=run_info,
            interactive=interactive if not demo_mode else False
        )
    )
    print("Run finished. Summary:")
    print(json.dumps(result["run_summary"], indent=2))
    print(f"Outputs written to: {result['run_summary']['project_dir']}")

if __name__ == "__main__":
    main()
