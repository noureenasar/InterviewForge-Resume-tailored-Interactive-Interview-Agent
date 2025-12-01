"""
Entry point for InterviewForge (lightweight CLI).
"""

import argparse
from pipeline import Orchestrator
import pathlib
import sys

def load_resume_from_file(path: str) -> str:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"Resume file {path} not found.")
        sys.exit(1)
    return p.read_text()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-file", type=str, default=None, help="Path to resume text file")
    parser.add_argument("--role", type=str, required=True, help="Target role (e.g., Data Scientist)")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode (you type answers)")
    parser.add_argument("--demo", action="store_true", help="Demo mode (auto answers)")
    args = parser.parse_args()

    if args.resume_file:
        resume_text = load_resume_from_file(args.resume_file)
    else:
        print("No resume file provided. Paste resume text (end with EOF / Ctrl-D):")
        resume_text = sys.stdin.read()

    interactive = args.interactive and not args.demo
    orchestrator = Orchestrator(interactive=interactive)
    result = orchestrator.run(resume_text, args.role)
    print("\n=== Run Summary ===")
    print(f"Role: {result['role']}")
    print(f"Profile summary keys: {list(result['profile'].keys())}")
    print(f"Saved output to interviewforge_output/last_run.json")

if __name__ == "__main__":
    main()
