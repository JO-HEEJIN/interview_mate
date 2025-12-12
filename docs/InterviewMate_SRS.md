# Software Requirements Specification (SRS)
## InterviewMate.ai - Real-time AI Interview Assistant

**Document Version:** 1.0  
**Date:** December 10, 2024  
**Project:** InterviewMate.ai  
**Author:** Heejin Jo  
**Status:** Approved

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document provides a complete description of the functional and non-functional requirements for InterviewMate.ai, a real-time AI-powered interview assistant platform. This document is intended for:
- Development team
- Stakeholders
- Quality assurance team
- Future maintainers

### 1.2 Document Conventions
- **Must/Shall:** Mandatory requirement
- **Should:** Recommended requirement
- **May:** Optional requirement
- **FR:** Functional Requirement
- **NFR:** Non-Functional Requirement
- **Priority Levels:** High (Critical), Medium (Important), Low (Nice to have)

### 1.3 Intended Audience
- Full-stack developer (Heejin Jo)
- Beta testers
- Future team members
- Potential investors or partners

### 1.4 Product Scope
InterviewMate.ai is a web-based platform that provides real-time AI assistance during interview practice sessions. The platform helps job seekers prepare for technical and behavioral interviews by:
- Recording and transcribing spoken responses in real-time
- Analyzing interview questions
- Generating personalized, contextual answer suggestions
- Tracking progress and providing analytics

The MVP focuses on mock interview practice, not live interview assistance.

### 1.5 References
- Software Development Plan (SDP) v1.0
- UML Diagrams v1.0
- Business Requirements Document (BRD) v1.0
- OpenAI Whisper API Documentation
- Anthropic Claude API Documentation
- Next.js 14 Documentation
- FastAPI Documentation

---

## 2. Overall Description

### 2.1 Product Perspective
InterviewMate.ai is a standalone web application consisting of:
- Frontend: Next.js 14 single-page application
- Backend: FastAPI REST and WebSocket API
- Database: PostgreSQL (via Supabase)
- AI Services: OpenAI Whisper, Anthropic Claude
- File Storage: Supabase Storage
- Payment Processing: Stripe

The system integrates with third-party services but operates independently.

### 2.2 Product Features (High-Level)
1. User authentication and profile management
2. Resume upload and parsing
3. STAR story and talking points database
4. Real-time audio capture and transcription
5. AI-powered answer generation
6. Mock interview sessions
7. Session history and analytics
8. Subscription management
9. Multi-tier pricing (Free, Pro, Premium)

### 2.3 User Classes and Characteristics

**Primary User - Job Seeker:**
- Age: 22-45
- Technical proficiency: Medium to High
- Goal: Prepare for upcoming interviews
- Frequency: 3-5 sessions per week during job search
- Needs: Confidence, structured practice, personalized feedback

**Secondary User - Career Changer:**
- Age: 30-50
- Technical proficiency: Medium
- Goal: Transition to new industry/role
- Frequency: Daily practice for 2-4 weeks
- Needs: Industry-specific guidance, structured frameworks

**Admin User:**
- Internal team member
- Technical proficiency: High
- Goal: Monitor system health, manage users
- Frequency: Daily checks
- Needs: Dashboard, analytics, user management tools

### 2.4 Operating Environment
**Client Side:**
- Modern web browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Operating systems: Windows 10+, macOS 11+, iOS 14+, Android 10+
- Internet connection: Minimum 5 Mbps for real-time features
- Microphone: Required for audio input

**Server Side:**
- Frontend hosting: Vercel (Node.js environment)
- Backend hosting: Railway or AWS EC2 (Linux)
- Database: Supabase (PostgreSQL 14+)
- External APIs: OpenAI, Anthropic, Stripe

### 2.5 Design and Implementation Constraints
- Must use HTTPS for all communications
- Must comply with GDPR, CCPA for data privacy
- API rate limits: Whisper (50 requests/min), Claude (40 requests/min)
- Budget constraint: <$500/month for MVP phase
- Development timeline: 6 weeks to MVP
- Single developer (initially)
- Must work on mobile browsers (responsive design)

### 2.6 Assumptions and Dependencies

**Assumptions:**
- Users have access to a working microphone
- Users understand basic interview concepts (STAR framework)
- Primary language is English (MVP)
- Users are comfortable with AI-generated content
- Most sessions will be 30-60 minutes long

**Dependencies:**
- OpenAI Whisper API availability and reliability
- Anthropic Claude API availability and reliability
- Stripe payment processing
- Supabase infrastructure
- Vercel hosting platform
- Web browser support for Web Audio API

---

## 3. Functional Requirements

### 3.1 User Authentication (Priority: High)

**FR-1.1: User Registration**
- The system shall allow users to register with email and password
- The system shall support OAuth registration (Google, GitHub)
- The system shall validate email format
- The system shall require password minimum length of 8 characters
- The system shall send verification email upon registration
- The system shall prevent duplicate email registrations

**FR-1.2: User Login**
- The system shall authenticate users with email and password
- The system shall support OAuth login (Google, GitHub)
- The system shall implement session management with JWT tokens
- The system shall provide "Remember Me" functionality
- The system shall lock account after 5 failed login attempts
- The system shall provide password reset functionality

**FR-1.3: User Logout**
- The system shall allow users to logout
- The system shall invalidate JWT tokens upon logout
- The system shall clear local storage/session data

**FR-1.4: Password Management**
- The system shall allow users to reset forgotten passwords
- The system shall send password reset link via email
- The system shall allow users to change passwords when logged in
- The system shall hash all passwords using bcrypt

---

### 3.2 Profile Management (Priority: High)

**FR-2.1: Resume Upload**
- The system shall accept PDF and DOCX file formats
- The system shall limit file size to 5MB
- The system shall extract text from uploaded resumes
- The system shall store original files securely
- The system shall allow users to re-upload/update resumes
- The system shall provide preview of extracted text

**FR-2.2: STAR Stories Management**
- The system shall allow users to create STAR stories
- The system shall provide fields for: Title, Situation, Task, Action, Result
- The system shall allow tagging stories by skill/category
- The system shall allow editing and deleting stories
- The system shall store unlimited stories per user
- The system shall provide search and filter functionality

**FR-2.3: Talking Points**
- The system shall allow users to add key talking points
- The system shall organize talking points by category
- The system shall support markdown formatting
- The system shall allow editing and deleting talking points

**FR-2.4: Profile Editing**
- The system shall allow users to update personal information
- The system shall allow users to add skills/technologies
- The system shall allow users to specify target companies/roles
- The system shall auto-save changes

---

### 3.3 Audio Capture and Transcription (Priority: High)

**FR-3.1: Audio Input**
- The system shall request microphone permissions
- The system shall detect available audio input devices
- The system shall allow users to select input device
- The system shall display real-time audio level indicator
- The system shall handle microphone disconnection gracefully

**FR-3.2: Audio Streaming**
- The system shall stream audio via WebSocket connection
- The system shall buffer audio in 1-second chunks
- The system shall implement automatic reconnection
- The system shall display connection status
- The system shall compress audio before transmission

**FR-3.3: Real-time Transcription**
- The system shall transcribe audio using Whisper API
- The system shall display transcription with <2 second latency
- The system shall handle multiple languages (English priority)
- The system shall provide confidence scores for transcriptions
- The system shall allow manual correction of transcriptions

**FR-3.4: Question Detection**
- The system shall detect complete questions from transcription
- The system shall identify question boundaries (pause, intonation)
- The system shall categorize questions (behavioral, technical, situational)
- The system shall extract key entities from questions

---

### 3.4 AI Answer Generation (Priority: High)

**FR-4.1: Context Building**
- The system shall load user profile (resume, STAR stories)
- The system shall include relevant talking points
- The system shall consider question category and difficulty
- The system shall maintain conversation history

**FR-4.2: Answer Generation**
- The system shall generate answers using Claude API
- The system shall structure answers using STAR framework (when applicable)
- The system shall limit answer length to 90-120 seconds when spoken
- The system shall provide natural, conversational tone
- The system shall avoid robotic or repetitive phrasing

**FR-4.3: Answer Delivery**
- The system shall display generated answers within 3 seconds
- The system shall highlight key points in answers
- The system shall allow users to regenerate answers
- The system shall provide multiple answer variations (Pro tier)
- The system shall allow users to save favorite answers

**FR-4.4: Fallback Handling**
- The system shall retry failed API calls (max 3 attempts)
- The system shall use GPT-4 as fallback if Claude fails
- The system shall notify users of generation failures
- The system shall provide cached answers for common questions

---

### 3.5 Practice Sessions (Priority: High)

**FR-5.1: Session Initialization**
- The system shall allow users to start new practice sessions
- The system shall allow selection of session type (General, Behavioral, Technical)
- The system shall allow selection of difficulty level
- The system shall provide estimated session duration
- The system shall create unique session ID

**FR-5.2: Question Database**
- The system shall provide 100+ curated interview questions
- The system shall organize questions by category and difficulty
- The system shall allow random question selection
- The system shall track which questions user has practiced
- The system shall allow users to add custom questions (Pro tier)

**FR-5.3: Session Flow**
- The system shall display question one at a time
- The system shall allow users to skip questions
- The system shall provide timer for each question
- The system shall allow pause/resume functionality
- The system shall show progress indicator

**FR-5.4: Session Management**
- The system shall auto-save session progress every 30 seconds
- The system shall allow manual session end
- The system shall handle unexpected disconnections
- The system shall provide session recovery on reconnection

**FR-5.5: Session Summary**
- The system shall generate session summary at end
- The system shall display: duration, questions asked, answers generated
- The system shall provide downloadable transcript
- The system shall highlight areas for improvement
- The system shall suggest next steps

---

### 3.6 Session History and Analytics (Priority: Medium)

**FR-6.1: Session History**
- The system shall display list of past sessions
- The system shall show session metadata (date, duration, type)
- The system shall allow filtering by date range and session type
- The system shall allow sorting by various criteria
- The system shall provide search functionality

**FR-6.2: Session Details**
- The system shall allow users to view full session transcripts
- The system shall display all questions and answers
- The system shall show timestamps for each interaction
- The system shall allow export to PDF or text file

**FR-6.3: Analytics Dashboard**
- The system shall display total practice time
- The system shall show number of sessions completed
- The system shall track most practiced question categories
- The system shall display improvement trends over time
- The system shall show average session length

**FR-6.4: Progress Tracking**
- The system shall track questions practiced
- The system shall identify frequently missed question types
- The system shall suggest focus areas
- The system shall display streak statistics (Pro tier)

---

### 3.7 Subscription Management (Priority: Medium)

**FR-7.1: Plan Selection**
- The system shall display available subscription tiers (Free, Pro, Premium)
- The system shall clearly show features for each tier
- The system shall allow users to upgrade/downgrade plans
- The system shall provide annual billing option (20% discount)

**FR-7.2: Payment Processing**
- The system shall integrate with Stripe for payments
- The system shall support credit/debit cards
- The system shall store payment methods securely (via Stripe)
- The system shall provide payment receipts via email
- The system shall handle failed payments gracefully

**FR-7.3: Subscription Lifecycle**
- The system shall automatically renew subscriptions
- The system shall send renewal reminders 7 days before
- The system shall allow subscription cancellation
- The system shall provide grace period after failed payment (3 days)
- The system shall downgrade to Free tier after cancellation

**FR-7.4: Usage Limits**
- The system shall enforce session limits for Free tier (5/month)
- The system shall display remaining sessions
- The system shall prompt upgrade when limit reached
- The system shall reset limits on billing cycle

---

### 3.8 Admin Panel (Priority: Low)

**FR-8.1: User Management**
- The system shall allow admins to view all users
- The system shall allow searching users by email/name
- The system shall allow viewing user details
- The system shall allow disabling/enabling user accounts
- The system shall display user subscription status

**FR-8.2: System Monitoring**
- The system shall display system health metrics
- The system shall show API usage statistics
- The system shall display error logs
- The system shall show active sessions count
- The system shall alert on critical errors

**FR-8.3: Content Management**
- The system shall allow admins to add/edit question database
- The system shall allow managing question categories
- The system shall allow setting question difficulty levels

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements (Priority: High)

**NFR-1.1: Response Time**
- System shall load initial page within 2 seconds
- System shall display transcription with <2 second latency
- System shall generate answers within 3 seconds (95th percentile)
- System shall support 100 concurrent users without degradation

**NFR-1.2: Throughput**
- System shall handle 1,000 sessions per day
- System shall process 10,000 audio chunks per hour
- System shall support 500 API calls per minute (aggregate)

**NFR-1.3: Resource Usage**
- Frontend bundle size shall be <1MB (gzipped)
- Backend memory usage shall be <512MB per instance
- Database queries shall execute within 100ms (average)

---

### 4.2 Reliability Requirements (Priority: High)

**NFR-2.1: Availability**
- System shall maintain 99.5% uptime (excluding planned maintenance)
- System shall have <1 hour downtime per month
- Planned maintenance shall be scheduled during low-usage hours

**NFR-2.2: Fault Tolerance**
- System shall handle API failures gracefully with retries
- System shall implement circuit breakers for external services
- System shall auto-recover from transient failures
- System shall maintain session state during temporary disconnections

**NFR-2.3: Data Integrity**
- System shall ensure no data loss during normal operations
- System shall implement database transaction rollbacks on errors
- System shall validate all user inputs
- System shall maintain referential integrity in database

**NFR-2.4: Backup and Recovery**
- System shall perform daily database backups
- System shall retain backups for 30 days
- System shall support point-in-time recovery
- Recovery Time Objective (RTO): <4 hours
- Recovery Point Objective (RPO): <24 hours

---

### 4.3 Security Requirements (Priority: High)

**NFR-3.1: Authentication and Authorization**
- System shall implement JWT-based authentication
- System shall use OAuth 2.0 for third-party login
- System shall enforce role-based access control (RBAC)
- System shall expire sessions after 7 days of inactivity
- System shall require re-authentication for sensitive operations

**NFR-3.2: Data Protection**
- System shall encrypt all data in transit using TLS 1.3
- System shall encrypt sensitive data at rest (passwords, payment info)
- System shall hash passwords using bcrypt (cost factor 12)
- System shall not log sensitive information (passwords, tokens)
- System shall implement secure API key management

**NFR-3.3: Privacy**
- System shall comply with GDPR and CCPA regulations
- System shall allow users to export their data
- System shall allow users to delete their accounts and data
- System shall provide clear privacy policy
- System shall obtain consent for data processing

**NFR-3.4: Input Validation**
- System shall sanitize all user inputs
- System shall prevent SQL injection attacks
- System shall prevent XSS attacks
- System shall implement rate limiting (100 requests/minute per user)
- System shall validate file uploads (type, size, content)

**NFR-3.5: API Security**
- System shall use HTTPS for all API calls
- System shall implement API key rotation
- System shall use environment variables for secrets
- System shall not expose internal error details to clients
- System shall implement CORS policies

---

### 4.4 Usability Requirements (Priority: High)

**NFR-4.1: User Interface**
- System shall follow consistent design language
- System shall be responsive (mobile, tablet, desktop)
- System shall support dark mode
- System shall provide clear navigation
- System shall use accessible color contrast ratios (WCAG 2.1 AA)

**NFR-4.2: Accessibility**
- System shall support keyboard navigation
- System shall provide ARIA labels for screen readers
- System shall support browser text scaling
- System shall provide alt text for images
- System shall meet WCAG 2.1 Level AA standards

**NFR-4.3: User Feedback**
- System shall display loading indicators for async operations
- System shall provide clear error messages
- System shall show success confirmations
- System shall display helpful tooltips
- System shall provide inline validation feedback

**NFR-4.4: Help and Documentation**
- System shall provide in-app help tooltips
- System shall include FAQ section
- System shall offer interactive onboarding for new users
- System shall provide video tutorials (Phase 2)

---

### 4.5 Compatibility Requirements (Priority: Medium)

**NFR-5.1: Browser Compatibility**
- System shall work on Chrome 90+
- System shall work on Firefox 88+
- System shall work on Safari 14+
- System shall work on Edge 90+
- System shall gracefully degrade on older browsers

**NFR-5.2: Device Compatibility**
- System shall work on desktop (1920x1080 and above)
- System shall work on tablets (768x1024 and above)
- System shall work on mobile phones (375x667 and above)
- System shall adapt layout based on screen size

**NFR-5.3: API Compatibility**
- System shall handle Whisper API version updates
- System shall handle Claude API version updates
- System shall maintain backward compatibility for internal APIs (v1, v2)

---

### 4.6 Maintainability Requirements (Priority: Medium)

**NFR-6.1: Code Quality**
- System shall maintain 80%+ test coverage
- System shall follow TypeScript strict mode
- System shall use ESLint and Prettier for code formatting
- System shall document all public APIs
- System shall use semantic versioning

**NFR-6.2: Modularity**
- System shall separate concerns (frontend/backend, services/controllers)
- System shall use dependency injection
- System shall implement service interfaces
- System shall minimize coupling between modules

**NFR-6.3: Logging and Monitoring**
- System shall log all errors with stack traces
- System shall log API calls with timestamps and response times
- System shall implement structured logging (JSON format)
- System shall integrate with monitoring tools (Sentry, PostHog)

**NFR-6.4: Documentation**
- System shall maintain up-to-date README
- System shall document all API endpoints (OpenAPI/Swagger)
- System shall document database schema
- System shall maintain deployment documentation
- System shall document environment variables

---

### 4.7 Scalability Requirements (Priority: Medium)

**NFR-7.1: Horizontal Scaling**
- Backend shall support multiple instances behind load balancer
- Database shall support read replicas for scaling reads
- System shall use stateless architecture for easy scaling

**NFR-7.2: Vertical Scaling**
- System shall efficiently use resources up to 4 CPU cores
- System shall efficiently use resources up to 8GB RAM
- Database shall support scaling to 100GB+ storage

**NFR-7.3: Performance at Scale**
- System shall maintain response times with 10,000 registered users
- System shall support 500 concurrent sessions
- System shall handle 100,000 audio chunks per day

---

### 4.8 Localization Requirements (Priority: Low)

**NFR-8.1: Internationalization**
- System shall support multiple languages (Phase 2)
- System shall externalize all UI strings
- System shall support RTL languages (Phase 2)
- System shall handle different date/time formats

**NFR-8.2: Language Support**
- MVP: English only
- Phase 2: Korean, Spanish, Mandarin
- Phase 3: Additional European languages

---

## 5. External Interface Requirements

### 5.1 User Interfaces

**UI-1: Login Page**
- Email and password input fields
- OAuth buttons (Google, GitHub)
- "Forgot Password" link
- "Create Account" link

**UI-2: Dashboard**
- Welcome message with user name
- Quick action buttons (Start Practice, View History)
- Recent sessions list
- Practice statistics widget
- Subscription status

**UI-3: Practice Session Page**
- Real-time transcription display
- Question display area
- Answer suggestion card
- Timer
- Session controls (pause, end)
- Audio level indicator

**UI-4: Profile Management Page**
- Resume upload section
- STAR stories list and editor
- Talking points editor
- Personal information form

**UI-5: Session History Page**
- List of past sessions with filters
- Session details modal
- Export options

**UI-6: Subscription Page**
- Pricing tiers comparison
- Payment form
- Billing history
- Cancel subscription option

### 5.2 Hardware Interfaces

**HW-1: Microphone**
- System shall access user's microphone via Web Audio API
- System shall support USB and built-in microphones
- System shall handle microphone selection

### 5.3 Software Interfaces

**SW-1: OpenAI Whisper API**
- Endpoint: https://api.openai.com/v1/audio/transcriptions
- Method: POST (multipart/form-data)
- Authentication: API Key in headers
- Input: Audio file (webm, mp3, wav)
- Output: JSON with transcription text

**SW-2: Anthropic Claude API**
- Endpoint: https://api.anthropic.com/v1/messages
- Method: POST
- Authentication: API Key in headers
- Input: JSON with messages array
- Output: JSON with generated text

**SW-3: Stripe API**
- Subscriptions API for recurring payments
- Checkout API for payment processing
- Webhooks for payment events

**SW-4: Supabase API**
- PostgreSQL database via REST API
- Authentication via supabase-js SDK
- Storage via supabase-js SDK

### 5.4 Communication Interfaces

**COM-1: HTTPS**
- All client-server communication via HTTPS (TLS 1.3)

**COM-2: WebSocket**
- Real-time audio streaming via WSS (WebSocket Secure)
- Protocol: Socket.io

**COM-3: REST API**
- RESTful endpoints for CRUD operations
- JSON request/response format
- Authentication via JWT in headers

---

## 6. System Features by Priority

### 6.1 Critical (Must Have for MVP)
1. User authentication (register, login, logout)
2. Audio capture and transcription
3. AI answer generation
4. Basic practice session flow
5. Profile management (resume upload, STAR stories)

### 6.2 Important (Should Have for MVP)
1. Session history
2. Question database
3. Subscription tiers (Free, Pro)
4. Payment integration
5. Basic analytics

### 6.3 Nice to Have (Can Defer to Phase 2)
1. Advanced analytics and insights
2. Video practice
3. Company-specific prep
4. Mobile app
5. Collaborative features
6. Admin panel enhancements

---

## 7. Other Requirements

### 7.1 Legal Requirements
- Provide terms of service
- Provide privacy policy
- Obtain user consent for data processing
- Comply with GDPR (EU users)
- Comply with CCPA (California users)
- Display refund policy

### 7.2 Ethical Requirements
- Clearly label as "practice tool," not for live interviews
- Provide disclaimer about AI-generated content
- Encourage honest preparation, not cheating
- Protect user privacy and confidentiality
- Avoid discriminatory bias in AI responses

### 7.3 Business Rules
- Free tier: 5 practice sessions per month
- Pro tier: Unlimited sessions at $19/month
- Premium tier: All features at $49/month
- Session timeout: 2 hours maximum
- File upload limit: 5MB per file
- Maximum audio recording: 2 hours per session

---

## 8. Appendices

### 8.1 Glossary
- **STAR Framework:** Situation, Task, Action, Result - a structured method for answering behavioral interview questions
- **Transcription:** Converting spoken words to written text
- **WebSocket:** Protocol for real-time bidirectional communication
- **JWT:** JSON Web Token for authentication
- **TLS:** Transport Layer Security for encrypted communication
- **Latency:** Time delay between input and output
- **API:** Application Programming Interface

### 8.2 Acronyms
- SRS: Software Requirements Specification
- MVP: Minimum Viable Product
- API: Application Programming Interface
- UI: User Interface
- GDPR: General Data Protection Regulation
- CCPA: California Consumer Privacy Act
- JWT: JSON Web Token
- RBAC: Role-Based Access Control
- WCAG: Web Content Accessibility Guidelines
- RTO: Recovery Time Objective
- RPO: Recovery Point Objective

### 8.3 Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 10, 2024 | Heejin Jo | Initial SRS created |

---

## 9. Approval

**Project Lead:** Heejin Jo  
**Date:** December 10, 2024  
**Status:** Approved for Development

**Next Steps:**
1. Review and finalize BRD
2. Create test cases based on requirements
3. Begin Phase 1 development
4. Conduct requirements walkthrough with stakeholders (if applicable)
