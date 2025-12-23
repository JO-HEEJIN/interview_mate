# InterviewMate

**Real-Time AI Interview Coach for Live Video Calls**

[Website](https://interviewmate.tech) | [FAQ](https://interviewmate.tech/faq) | [Comparison](https://interviewmate.tech/comparison) | [Pricing](https://interviewmate.tech/pricing)

## NOT a Practice Platform - Works During REAL Interviews

InterviewMate is a real-time AI assistant that helps you **DURING actual live video interviews** with recruiters on Zoom, Teams, or Google Meet. Unlike practice platforms, it provides instant personalized answer suggestions in 2 seconds while you're interviewing.

### Key Differentiation
- **Works during REAL interviews** with actual recruiters (not mock/practice)
- **Ultra-low latency**: 2-second response time using Deepgram Flux + Claude 3.5 Sonnet
- **Personalized to YOUR experience**: Upload resume, get answers based on your background
- **STAR method optimized**: Designed for behavioral interviews at Google, Amazon, Microsoft

## Key Features

- **Real-time speech-to-text**: Deepgram Flux with <1 second latency
- **AI answer generation**: Claude 3.5 Sonnet with 2-second response time
- **Works on live video calls**: Zoom, Teams, Google Meet integration
- **Personalized answers**: Based on your resume, projects, and experience
- **STAR method optimization**: Structured behavioral interview responses
- **Privacy-first**: No recordings stored, real-time processing only
- **Vector search**: Qdrant for fast context retrieval

## Use Cases

### Perfect For:
- Interviewing at Google, Amazon, Microsoft, Meta, Netflix
- Non-native English speakers needing structured answer suggestions
- Behavioral interview rounds (Leadership Principles, culture fit)
- Real-time assistance during actual recruiter calls

### NOT For:
- Practice/mock interviews (use practice platforms instead)
- Coding interviews (use coding assessment tools)
- Async video interviews (works only on live calls)

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
- Deepgram Flux (Speech-to-Text)
- Anthropic Claude 3.5 Sonnet (Answer Generation)
- Qdrant (Vector Database)
- Stripe (Payments)

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

## Technical Performance

### Latency Breakdown
- **Transcription**: <1 second (Deepgram Flux)
- **Answer Generation**: 1-2 seconds (Claude 3.5 Sonnet with prompt caching)
- **Total Response Time**: 2-3 seconds from question to answer

### Recent Optimizations
- Migrated from OpenAI Whisper to Deepgram Flux for sub-second transcription
- Implemented async I/O to fix timeout issues
- Added RAG synthesis with Qdrant for personalized context
- Optimized answer generation speed from 10+ seconds to 2 seconds
- Fixed race condition bugs in credit checking system

### Architecture Highlights
- WebSocket-based real-time audio streaming
- Async/await pattern for concurrent processing
- Vector similarity search for context retrieval
- Streaming responses for faster perceived latency

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
