# Database Migrations

This directory contains SQL migration files for the InterviewMate.ai database.

## Structure

```
database/
├── migrations/      # Schema migrations (numbered)
│   └── 001_initial_schema.sql
└── seeds/           # Seed data
    └── 001_questions.sql
```

## Usage with Supabase

### Option 1: Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste the migration SQL files in order
4. Run each migration

### Option 2: Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

## Migration Files

| File | Description |
|------|-------------|
| `001_initial_schema.sql` | Core tables, indexes, RLS policies, and triggers |

## Seed Files

| File | Description |
|------|-------------|
| `001_questions.sql` | Interview questions (45 questions across 3 categories) |

## Tables Overview

- `profiles` - User profiles (extends Supabase auth)
- `resumes` - User uploaded resumes
- `star_stories` - STAR format stories
- `talking_points` - Key talking points
- `questions` - Interview question bank
- `sessions` - Practice session records
- `session_answers` - Question/answer pairs per session
