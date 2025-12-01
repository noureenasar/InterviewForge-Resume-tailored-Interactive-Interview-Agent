# InterviewForge — Resume-tailored Interactive Interview Agent

## What it does
InterviewForge ingests a candidate resume and target role, generates tailored interview rounds & rubrics, runs a simulated interview (interactive or demo), critiques answers, and outputs a prioritized study plan, flashcards, and a follow-up email.

## Architecture
- Orchestrator: coordinates pipeline and persists runs
- ResumeParserAgent: extracts skills & highlights from resume
- RoundGeneratorAgent: parallel generation of behavioral/technical/system-design rounds
- InterviewAgent: conducts Q&A with checkpoint/resume support
- CritiqueAgent: scores & feedback (LLM-assisted)
- StudyPlanAgent & FlashcardAgent: generate study artifacts
- EmailAgent: creates follow-up email


📌 Overview

InterviewForge is a multi-agent, resume-aware mock interview assistant that delivers personalized, adaptive, and repeatable interview practice.

It ingests a candidate’s resume and target job role, runs dynamic multi-round mock interviews, evaluates answers using rubric-based scoring, generates personalized study plans and flashcards, and even drafts a follow-up email summarizing the candidate’s progress.

This project demonstrates:
✔ Multi-agent systems (sequential + loop agents)
✔ Custom tools (resume parser, evaluator, flashcard generator)
✔ Built-in tools (Search, Code Execution)
✔ Long-running agents (pause/resume interview)
✔ Memory and Sessions (InMemorySessionService)
✔ Logging, tracing, context compaction
✔ A2A communication
✔ Gemini-powered intelligence

🚩 Problem Statement

Interview preparation is traditionally generic, inconsistent, not personalized, lacking actionable feedback and spread across many disconnected tools.

Candidates need role-specific and resume-specific interview practice, not random questions.

InterviewForge solves this by enabling:
a. Resume-aware question generation
b. Structured multi-round interviews
c. Real-time scoring + feedback
d. Adaptive learning recommendations
e. Study plan + flashcard generation


🤖 Why Agents?

Interview preparation is a sequential, multi-step, stateful process. Agents are the perfect solution because:

1. Each interview stage requires specialization
    a. Resume parsing
    b. Mock interview rounds
    c. Answer evaluation
    d. Study plan creation

2. Interviews require a loop
Ask → Answer → Evaluate → Continue. Loop agents model interview behavior naturally.

3. Memory is essential
The agent must recall previous answers, weaknesses, job role target, progress trend

4. Tooling improves precision
Custom tools handle structured parsing, scoring, flashcards, and external searches.

5. A2A Protocol
Ensures deterministic and modular inter-agent communication.


🧱 Architecture

InterviewForge uses four primary agents orchestrated by the main controller.

                         ┌─────────────────────────┐
                         │   User Uploads Resume   │
                         └──────────┬──────────────┘
                                    │
                             Orchestrator Agent
                                    │
          ┌─────────────────────────┼───────────────────────────┐
          │                         │                           │
┌────────────────┐     ┌───────────────────────┐     ┌─────────────────────┐
│ Resume Analysis│     │ Interview Simulator   │     │ Evaluation &        │
│ Agent          │     │ (Loop Agent)          │     │ Recommendation Agent│
└────────────────┘     └───────────────────────┘     └─────────────────────┘
          │                         │                          │
          │                         │                          │
          └──────────────┬──────────┴───────────────┬──────────┘
                         ▼                          ▼
            ┌────────────────────┐        ┌────────────────────────┐
            │ Flashcard Generator│        │ Follow-up Email Agent  │
            └────────────────────┘        └────────────────────────┘


Key Components:

1. Sequential agents → Resume → Interview → Evaluation
2. Loop agent → Repeats question cycles
3. Memory → Stores answers, scores, resume insights
4. Custom tools → Parsing, scoring, generation
5. Observability → Logging, tracing

📂 Repository Structure
interviewforge/
│── agents.py
│── tools.py
│── memory.py
│── pipeline.py
│── main.py
│── README.md
│── requirements.txt


✨ Features
1. Resume Ingestion & Analysis

    Extracts skills, experience, weaknesses
    Creates a structured profile object
    Maps resume → job role expectations

2. Multi-Round Mock Interview

    Behavioral round
    Technical/role-specific round
    Scenario/problem-solving round
    Loop agent manages Q&A cycles

3. Real-Time Evaluation

    Rubric scoring on:
      Clarity
      Structure
      Technical Depth
      Examples
      Role Alignment

4. Personalized Study Plan

    Skill gaps
    Daily tasks
    Learning roadmap

5. Auto-Generated Flashcards

    Dynamic Q&A dataset
    Exportable JSON

6. Follow-Up Email

    Summarizes:
      Performance
      Next steps
      Areas to focus

7. Pause & Resume

Long-running session state retained.

