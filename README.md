# InterviewMate

**AI interview preparation and realistic mock sessions**

[Website](https://interviewmate.tech) | [Guide](https://interviewmate.tech/guide) | [Engineering case study](https://interviewmate.tech/engineering) | [FAQ](https://interviewmate.tech/faq) | [Pricing](https://interviewmate.tech/pricing)

InterviewMate helps people prepare for interviews using their real background. You upload your resume and target-role context, generate personalized practice questions, and rehearse timed sessions. During a session your spoken questions are transcribed in real time, and the AI streams response suggestions grounded in your prepared context. You compare them with your own answers and refine how you explain real experience.

**Responsible use:** InterviewMate is for preparation, rehearsal, and settings where AI assistance is permitted. For formal interviews, assessments, exams, admissions or immigration processes, follow the organizer's rules and disclose AI assistance when required.

## Features

- **Personalized practice Q&A**: generated from your resume, organization info, and role details, then editable and exportable (Anki CSV)
- **Timed practice sessions**: real-time speech-to-text with Deepgram, from your microphone or audio shared from another tab (for example, a practice partner on a video call)
- **Response suggestions**: prepared answers are matched first; otherwise Claude streams a suggestion that references your context
- **Session history**: transcribed questions and suggestions are saved for review and export, and can be deleted
- **Custom instructions**: new profiles start from a short STAR reasoning prompt

## Architecture

```
Browser mic / shared audio ──WebSocket──▶ FastAPI ──FFmpeg──▶ Deepgram (streaming STT, end-of-turn)
                                             │
                                             ├─ question detection (heuristics + model verification when unsure)
                                             ├─ retrieval: Qdrant, filtered by user_id, up to 3 parallel sub-queries
                                             ├─ prepared-answer match (≥0.85 returns the user's own answer)
                                             └─ Claude streaming (prompt caching)
```

See the [engineering case study](https://interviewmate.tech/engineering) for configured latency bounds, reliability incidents, evaluation methodology, and known gaps. Prompt experiments with raw outputs are in [`car_wash/`](car_wash/).

## Project Structure

```
interview_mate/
├── frontend/         # Next.js web application
├── backend/          # FastAPI backend (WebSocket pipeline, retrieval, payments)
├── car_wash/         # Controlled prompt-architecture experiments
├── overlay/          # Experimental macOS wrapper app
└── docs/             # Early project documentation
```

## Tech Stack

- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, WebSockets, asyncio
- **Data & auth:** Supabase (PostgreSQL, Auth)
- **Speech:** Deepgram streaming STT
- **Retrieval:** Qdrant with OpenAI `text-embedding-3-small`
- **Generation:** Anthropic Claude (streaming, prompt caching)
- **Experimentation:** Statsig prompt variants with in-session thumbs up/down
- **Payments:** Lemon Squeezy

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (API docs at `/docs`)

## License

Private - All rights reserved
