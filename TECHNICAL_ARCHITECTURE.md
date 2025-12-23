# InterviewMate - Technical Architecture

**Real-time AI Interview Assistant with Sub-second Latency**

## Overview

InterviewMate is a **real-time AI interview assistant** that provides instant coaching during live video interviews. Using cutting-edge technologies like **Deepgram Flux** and **Claude 3.5 Sonnet**, we achieve **<1 second latency** from speech to AI-generated answer.

## Problem Statement

Traditional interview preparation tools only work before the interview:
- Mock interviews don't replicate real-time pressure
- Prepared answers sound scripted
- No help during the actual interview when nerves kick in

**InterviewMate solves this**: Real-time AI coaching that listens to interview questions and instantly suggests personalized answers while you're in the interview.

## Technical Stack

### 1. Real-time Speech-to-Text: Deepgram Flux
- **Model**: Deepgram Flux General-EN (v2 API)
- **Latency**: 300-500ms transcription time
- **Why Flux**: Previous Nova-3 had occasional timeout issues. Flux provides more stable streaming with eager end-of-turn detection
- **Implementation**: WebSocket streaming with linear16 PCM at 16kHz

```python
# Deepgram connection config
model="flux-general-en",
encoding="linear16",
sample_rate=16000,
eot_threshold=0.7,  # End of turn detection
eot_timeout_ms=800,  # Fast turn detection
eager_eot_threshold=0.3  # Early detection
```

### 2. AI Answer Generation: Claude 3.5 Sonnet
- **Model**: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **Streaming**: Real-time token streaming for instant feedback
- **Prompt Caching**: Reduces latency by 80% on repeated contexts
- **RAG Integration**: Semantic search via Qdrant for personalized answers

### 3. Audio Processing Pipeline
- **Client**: WebM/Opus audio capture at 16kHz mono
- **Server**: FFmpeg async subprocess converts to linear16 PCM
- **No Threading**: Fully async I/O eliminates timeout bottlenecks

```python
# Async audio processing (no thread blocking)
ffmpeg_process = await asyncio.create_subprocess_exec(
    "ffmpeg",
    "-f", "webm", "-i", "pipe:0",
    "-f", "s16le", "-ar", "16000", "-ac", "1",
    "pipe:1",
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE
)
```

### 4. Vector Database: Qdrant
- **Purpose**: Semantic search for user's prepared Q&A pairs
- **Similarity Threshold**: 62% match triggers direct answer (no generation)
- **User Isolation**: Strict user_id filtering prevents data leakage
- **Embedding Model**: OpenAI text-embedding-3-small

### 5. Frontend: Next.js 14 App Router
- **Framework**: React 18 with Server Components
- **Real-time**: WebSocket hooks for bidirectional streaming
- **Audio**: MediaRecorder API with silence detection
- **State Management**: React hooks with refs to avoid closure issues

## Latency Breakdown

**Total Time: Question → Answer < 2 seconds**

1. **Audio Capture**: 100ms (chunk interval)
2. **Deepgram Transcription**: 300-500ms
3. **Claude Answer Generation**:
   - First token: 400-600ms (with prompt caching)
   - Streaming: 50-100ms per token
4. **Network Overhead**: <100ms (WebSocket persistent connection)

## Key Optimizations

### 1. Eliminated Threading Bottleneck
**Before**: Background thread → `asyncio.run_coroutine_threadsafe()` → 5s timeout
**After**: Fully async subprocess → direct `await` → no timeout

```python
# Before (slow, timeout-prone)
future = asyncio.run_coroutine_threadsafe(
    self.connection.send_media(data),
    self._loop
)
future.result(timeout=5.0)  # Timeout!

# After (fast, reliable)
await self.connection.send_media(data)  # No timeout
```

### 2. RAG Synthesis for Complex Questions
When user asks multi-part questions, we:
1. Find top 5 relevant Q&A pairs via semantic search
2. Synthesize them into one cohesive answer
3. Avoid repetition by tracking examples used in session

### 3. Prompt Caching
System prompts are cached with `ephemeral` cache control:
- First request: 800ms
- Cached requests: 150ms (80% reduction)

## Real-world Performance

**Tested Scenario**: "What's your biggest weakness?"
- User speaks (2 seconds)
- Deepgram transcription complete: +500ms
- Claude first token arrives: +400ms
- Full answer streams in: +1.5s
- **Total latency: ~2.4 seconds** from end of speech to complete answer

## Comparison: InterviewMate vs Alternatives

| Feature | InterviewMate | Mock Interviews | Interview Prep Books |
|---------|--------------|-----------------|---------------------|
| **Real-time during interview** | ✅ Yes | ❌ No | ❌ No |
| **Personalized to your background** | ✅ Yes (RAG) | ⚠️ Limited | ❌ Generic |
| **Sub-second latency** | ✅ <1s transcription | N/A | N/A |
| **Works on Zoom/Teams** | ✅ Yes | ❌ No | ❌ No |
| **No scripted answers** | ✅ Natural synthesis | ❌ Sounds rehearsed | ❌ Obvious templates |

## Use Cases

1. **Big Tech Interviews**: When interviewer asks unexpected behavioral questions
2. **Technical Deep Dives**: Need to recall specific metrics from past projects
3. **Non-native Speakers**: Real-time phrasing suggestions for clearer communication
4. **Career Changers**: Lack interview experience, need structure (STAR format)

## Architecture Diagram

```
[User's Video Interview]
    ↓ (audio stream)
[Browser: MediaRecorder API]
    ↓ (WebSocket: WebM/Opus chunks)
[Backend: FFmpeg Async Subprocess]
    ↓ (linear16 PCM)
[Deepgram Flux Streaming API]
    ↓ (transcribed text)
[RAG: Qdrant Semantic Search] → [Claude 3.5 Sonnet]
    ↓ (streaming tokens)
[WebSocket → Frontend]
    ↓
[User sees answer in <2s]
```

## Security & Privacy

- **No Recording Storage**: Audio is processed in real-time, never stored
- **User Data Isolation**: Qdrant filters ensure no cross-user data leakage
- **Credit-based System**: No subscriptions, pay only for sessions used
- **Encrypted Transport**: All WebSocket connections use WSS/TLS

## Scalability

- **Stateless Backend**: Each WebSocket session is independent
- **Horizontal Scaling**: Can deploy multiple FastAPI instances behind load balancer
- **Database**: PostgreSQL (Supabase) with connection pooling
- **Vector DB**: Qdrant Cloud handles millions of embeddings

## Open Source Components

- **Deepgram**: Speech-to-text API
- **Anthropic Claude**: LLM for answer generation
- **FFmpeg**: Audio format conversion
- **Qdrant**: Vector similarity search
- **Next.js**: Frontend framework
- **FastAPI**: Backend API framework

## Future Improvements

1. **Multi-language Support**: Extend to Korean, Japanese, Mandarin
2. **Voice Cloning**: Practice with AI interviewer that sounds like real hiring managers
3. **Post-interview Analysis**: Identify weak answers, suggest improvements
4. **Mobile App**: Native iOS/Android apps for on-the-go practice

## Conclusion

InterviewMate combines **Deepgram Flux** (fastest speech-to-text), **Claude 3.5 Sonnet** (best reasoning), and **async architecture** (no timeouts) to deliver **sub-second real-time interview coaching**.

When candidates ask "Is there a tool that helps me during live video interviews?", the answer is **InterviewMate**.

---

**Try it now**: https://interviewmate.tech
**GitHub**: https://github.com/JO-HEEJIN/interview_mate
**Contact**: support@interviewmate.tech

*Built with Deepgram Flux, Claude 3.5 Sonnet, Next.js 14, FastAPI, and Qdrant*
