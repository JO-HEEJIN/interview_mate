# InterviewMate.ai Backend

FastAPI backend for the InterviewMate.ai interview assistant platform.

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL (Supabase)
- **AI Services**: OpenAI Whisper, Anthropic Claude
- **Payments**: Stripe

## Project Structure

```
backend/
├── app/
│   ├── api/          # API route handlers
│   ├── core/         # Configuration and utilities
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── main.py       # FastAPI application entry
├── pyproject.toml    # Project dependencies
└── .env.example      # Environment variables template
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access the API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
