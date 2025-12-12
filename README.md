# InterviewMate.ai

Real-time AI-powered interview assistant that helps job seekers prepare for technical and behavioral interviews.

## Overview

InterviewMate.ai provides personalized answer suggestions using speech recognition and AI generation, helping users practice and improve their interview skills.

## Key Features

- Real-time speech-to-text transcription using OpenAI Whisper
- Intelligent question detection with validation
- AI-powered answer generation using Anthropic Claude
- Silence detection for automatic audio processing
- STAR stories integration for personalized responses
- Optimized transcription pipeline with reduced latency
- Pre-filtering for efficient question detection

## Project Structure

```
interview_mate/
├── frontend/         # Next.js 14 web application
├── backend/          # FastAPI Python backend
├── docs/             # Project documentation
└── tasks/            # Development task tracking
```

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- NextAuth.js

### Backend
- FastAPI (Python)
- PostgreSQL (Supabase)
- OpenAI Whisper API
- Anthropic Claude API
- Stripe

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm or yarn

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm run dev
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

## Development

- Frontend runs on: http://localhost:3000
- Backend runs on: http://localhost:8000
- API docs: http://localhost:8000/docs

## Recent Optimizations

### Transcription Performance
- Reduced latency from 1.5-2 seconds to 0.8-1.5 seconds
- Silence detection with 800ms threshold for instant processing
- Interview-specific Whisper prompts for better accuracy
- Optimized buffer management to prevent duplicate processing

### Question Detection
- Pre-filter keyword matching reduces Claude API calls by 30-50%
- Question completeness validation (minimum 5 words)
- Fuzzy matching to prevent duplicate answer generation
- Real-time processing state indicators

### API Optimization
- Lower Whisper temperature (0.1) for consistent output
- Smart pre-filtering before Claude API calls
- Reduced processing thresholds for faster response

## Documentation

See the `/docs` directory for detailed documentation:
- Business Requirements (BRD)
- Software Requirements (SRS)
- System Design (SDP)
- User Flow diagrams
- UML diagrams
- Test Cases

See `/tasks/todo.md` for:
- Development progress
- Implementation details
- Optimization review

## License

Private - All rights reserved
