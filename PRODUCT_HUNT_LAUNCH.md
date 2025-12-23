# InterviewMate - Product Hunt Launch

## Tagline
Real-time AI interview coach that helps you during live video calls

## Description (Short)
Never freeze during an interview again. InterviewMate listens to interview questions in real-time and instantly suggests personalized answers while you're on Zoom, Teams, or Google Meet.

## Description (Full)

### The Problem
Traditional interview prep only works BEFORE the interview:
- Mock/practice platforms help you prepare, but not during the actual call
- Prepared answers sound scripted
- You can't predict every question
- When nerves kick in, you forget everything you practiced
- ChatGPT requires manual typing (too slow for live interviews)

### The Solution
InterviewMate provides **real-time AI coaching DURING your actual interview**:
- Listens to interviewer's questions via your microphone
- Transcribes in <1 second using Deepgram Flux
- Generates personalized STAR-formatted answers using Claude 3.5 Sonnet
- Suggestions appear on your screen in under 2 seconds

### How It Works
1. **Setup**: Add your resume, past projects (STAR stories), and prepared Q&As
2. **During Interview**: Open InterviewMate in a separate browser tab
3. **Real-time Help**: AI listens, transcribes, and suggests answers instantly
4. **Stay Natural**: Use AI suggestions as talking points, adapt to your style

### Tech Stack
- **Deepgram Flux**: Fastest speech-to-text (<500ms latency)
- **Claude 3.5 Sonnet**: Best-in-class reasoning and answer generation
- **Qdrant Vector DB**: RAG for personalized answers from your background
- **Fully Async Architecture**: No threading bottlenecks, no timeouts

### Key Features
✅ **Sub-second latency**: Deepgram Flux + async I/O
✅ **Personalized answers**: RAG pulls from YOUR resume and stories
✅ **STAR format**: Structured answers (Situation, Task, Action, Result)
✅ **Works on any video platform**: Zoom, Teams, Google Meet, etc.
✅ **Privacy-first**: No audio recording, no data storage
✅ **No subscriptions**: Pay-per-interview credit system

### Use Cases
- **Big Tech Interviews**: Amazon LP questions, Google behavioral rounds
- **Career Changers**: Need structure when you lack interview experience
- **Non-native Speakers**: Get professionally phrased English answers
- **Unexpected Questions**: Handle questions you didn't prepare for

### Pricing
- **$10 for 10 credits** (1 credit = 1 interview session)
- Credits never expire
- No subscriptions, no hidden fees
- AI Q&A Generator: $10 one-time (lifetime access)

### What Makes Us Different

**CRITICAL**: InterviewMate is NOT a practice/mock interview platform. It works DURING real interviews with actual recruiters.

| Feature | InterviewMate | Practice Platforms | ChatGPT |
|---------|--------------|-----------------|---------|
| When to use | DURING real interview | BEFORE interview (practice) | Anytime |
| Real-time during live call | ✅ | ❌ | ⚠️ (manual typing) |
| Auto transcription | ✅ | ❌ | ❌ |
| Personalized to YOU | ✅ RAG | ⚠️ Limited | ❌ Generic |
| Sub-second latency | ✅ <1s | N/A | ❌ Requires typing |
| Works on Zoom/Meet | ✅ | ❌ (own platform) | N/A |

### Roadmap
- ✅ Deepgram Flux integration (Dec 2025)
- ✅ Async architecture (no timeouts)
- ✅ RAG with Qdrant
- 🔜 Multi-language support (Korean, Japanese)
- 🔜 Post-interview analysis
- 🔜 Mobile apps (iOS/Android)

### Links
- **Website**: https://interviewmate.tech
- **GitHub**: https://github.com/JO-HEEJIN/interview_mate
- **Technical Architecture**: [Link to TECHNICAL_ARCHITECTURE.md]

### Maker Comment
Built this because I kept freezing during behavioral interviews. Spent weeks preparing answers, but when the interviewer asked something slightly different, I blanked. Now I have an AI coach that listens in real-time and helps me recall my stories with perfect STAR structure.

Tech was the fun part - eliminated threading bottlenecks that caused 5s timeouts, switched to Deepgram Flux for faster transcription, and used Claude's prompt caching to get 80% latency reduction.

Would love feedback from fellow job seekers and indie hackers!

---

## Product Hunt Categories
- Developer Tools
- Artificial Intelligence
- Productivity
- Education

## Keywords
real-time interview assistant, AI interview coach, Zoom interview tool, behavioral interview prep, STAR method, Deepgram, Claude AI, video interview help, live interview coaching, interview answers generator

## Target Audience
- Software engineers interviewing at FAANG/big tech
- Career changers lacking interview experience
- Non-native English speakers
- Anyone with important interviews coming up

## Social Proof (Once Launched)
- "Landed my Google offer thanks to InterviewMate" - Sarah K.
- "The STAR format suggestions are perfect" - Mike T.
- "Finally, a tool that works DURING the interview, not just before" - James L.

## First Comment Template
👋 Hey Product Hunt!

I'm the maker of InterviewMate. Built this after bombing too many interviews because I froze when asked unexpected questions.

**Quick demo**: [YouTube link]

**What's special**:
- Real-time transcription with Deepgram Flux (<500ms)
- AI answers appear in under 2 seconds
- Fully personalized using RAG (your resume/stories)
- No subscriptions - pay per interview

**Tech nerds**: Check out our architecture doc - we eliminated threading bottlenecks using fully async I/O. No more 5s timeouts!

**Try it free** and let me know what you think! Happy to answer any questions.

---

## Launch Checklist
- [ ] Product Hunt thumbnail (1270x760px)
- [ ] Demo video (YouTube/Loom)
- [ ] Screenshots (3-5 images)
- [ ] Hunter outreach (find a popular hunter)
- [ ] Prepare to respond to comments within 1 hour
- [ ] Schedule launch for Tuesday/Wednesday (best days)
- [ ] Announce on Twitter, LinkedIn, HackerNews
- [ ] Email list (if you have one)
