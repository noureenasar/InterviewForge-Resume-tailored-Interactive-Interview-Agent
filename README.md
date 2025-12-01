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

## How to run
1. Create virtual env:


InterviewForge — Resume-Tailored Interactive Interview Agent

Track: Concierge Agents
Built for: Google Agentic AI Intensive – Capstone Project

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
/InterviewForge
│
├── agents/
│   ├── orchestrator.py
│   ├── resume_analysis_agent.py
│   ├── interview_loop_agent.py
│   ├── evaluation_agent.py
│   └── followup_agent.py
│
├── tools/
│   ├── resume_parser.py
│   ├── answer_evaluator.py
│   ├── flashcard_generator.py
│   └── search_tool.py
│
├── memory/
│   └── session_service.py
│
├── logs/
│
├── main.py
│
└── README.md

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

▶ Demo Flow (Example)
1. User uploads resume

resume.pdf

2. System extracts key info
Skills: Python, SQL, Cloud, Flask
Strengths: Ownership, problem solving
Weaknesses: System design clarity

3. Interview Begins

Agent: “Tell me about a time you solved a difficult problem.”
User answers → stored → scored.

4. Technical Round

Q: “Design a scalable notification service.”
A: user response → scored → feedback.

5. Recommendations
Top improvement areas:
• Use metrics in behavioral answers
• Improve API scalability explanations
• Stronger deployment reasoning

6. Flashcards

What is eventual consistency?

Describe message queues.

7. Follow-up Email Generated
🛠 Tech Stack
AI Models

Gemini 2.0 Flash

Gemini 2.0 Pro (for evaluation + generation)

Google Agentic Framework

Agent orchestration

Tools API

A2A messaging

Memory & sessions

Long-running operations

Custom Tools

Resume Parser (regex + ML)

Answer Evaluator

Flashcard Generator

Search Tool

Built-in Tools

Google Search

Code Execution

⚙️ Setup Instructions

Clone the repo:

git clone https://github.com/<your-username>/InterviewForge.git
cd InterviewForge


Install dependencies:

pip install -r requirements.txt


Add your environment variables:

GEMINI_API_KEY=your_key


Run:

python main.py


⚠️ No API keys are included in this repository (as required).

💡 How It Works (Technical Summary)

Orchestrator initializes the session

Resume agent parses user resume

Loop agent conducts mock interview rounds

Evaluation agent scores each answer via a tool

Memory keeps track of all answers + weaknesses

Recommendation agent creates study plan + flashcards

Follow-up agent generates email

Agents communicate via structured schemas using A2A protocol, ensuring deterministic behavior.

📊 Observability

Logging of agent transitions

Evaluation scores stored in session history

Context compaction applied for long interviews

Debug traces available in logs/

🚀 Future Enhancements

If more time were available, next steps include:

1. Voice-based interview simulation

Real-time speech feedback (pace, clarity, tone).

2. System design whiteboard mode

Draw diagrams → AI evaluates.

3. Interview readiness dashboard

Trends, week-over-week improvement, weakness heatmap.

4. Deployment on Cloud Run

Public URL access + persistent storage.

5. Role-specific interview packs

PM, Cybersecurity, Data Engineering, Cloud Architect.

6. Adaptive difficulty

InterviewForge becomes harder as user improves.

📜 License

MIT License. Free to use, modify, and extend.

🙏 Acknowledgements

Thanks to the Google Agentic AI Intensive faculty, Gemini team, and open-source community.
