# User Process Flow Documentation
## InterviewMate.ai - Real-time AI Interview Assistant

**Document Version:** 1.0  
**Date:** December 10, 2024  
**Project:** InterviewMate.ai  
**Author:** Heejin Jo  
**Status:** Approved

---

## 1. Introduction

### 1.1 Purpose
This document describes the complete user journey through InterviewMate.ai, from first visit to becoming a power user. It provides detailed flows for all major use cases and user interactions.

### 1.2 Intended Audience
- Development team (for implementation)
- UX/UI designers (for wireframes)
- Product managers (for feature planning)
- Beta testers (for understanding the product)
- Marketing team (for messaging)

### 1.3 Document Structure
Each flow includes:
- Flow diagram
- Step-by-step description
- User actions and system responses
- Decision points and alternate paths
- Success criteria
- Pain points and solutions

---

## 2. User Personas

### 2.1 Primary Persona: Alex (Junior Engineer)
**Background:**
- Age: 25
- Just completed coding bootcamp
- Looking for first tech job
- Interview experience: Limited
- Technical skills: Intermediate
- Confidence: Low

**Goals:**
- Practice common interview questions
- Build confidence speaking about experience
- Get immediate feedback on answers
- Prepare for behavioral and technical questions

**Pain Points:**
- Gets nervous during interviews
- Struggles to articulate experiences
- Can't afford expensive coaching
- Needs flexible practice schedule

### 2.2 Secondary Persona: Sarah (Career Changer)
**Background:**
- Age: 35
- 10 years in marketing
- Transitioning to product management
- Interview experience: Moderate (in different field)
- Technical skills: Basic
- Confidence: Medium

**Goals:**
- Frame marketing experience for PM roles
- Practice storytelling with STAR method
- Get help crafting answers
- Understand PM interview expectations

**Pain Points:**
- Difficulty connecting past experience to new role
- Impostor syndrome
- Limited network in tech
- Time constraints (full-time job + job search)

---

## 3. High-Level User Journey

```
Discovery → Sign Up → Onboarding → Profile Setup → Practice → Review → Upgrade (optional) → Continued Use
```

### 3.1 Discovery Phase
**Touchpoints:**
- Google search: "AI interview coach"
- Social media: LinkedIn, Twitter posts
- Product Hunt launch
- Word of mouth / referral
- Career blog articles

**User Mindset:**
- Anxious about upcoming interviews
- Looking for affordable help
- Skeptical but curious about AI

**Key Message:**
"Practice interviews with an AI coach that knows your background - for $0.63/day"

---

## 4. Detailed User Flows

### 4.1 Flow 1: New User Registration and Onboarding

#### Step-by-Step Flow:

**Step 1: Landing Page (First Impression)**
- **User arrives at:** https://interviewmate.ai
- **User sees:**
  - Hero headline: "Ace Your Next Interview with AI"
  - Subheadline: "Practice with a personal AI coach that knows your story"
  - CTA button: "Start Practicing Free"
  - Social proof: "Join 10,000+ job seekers"
  - Demo video (30 seconds)
  - Feature highlights
  - Pricing preview
- **User thinks:** "Is this legit? Will this actually help me?"
- **User action:** Clicks "Start Practicing Free"

**Step 2: Registration**
- **System shows:** Registration modal
  - Options: Email, Google OAuth, GitHub OAuth
  - Input fields: Email, Password
  - "Already have an account?" link
  - Privacy policy and terms checkboxes
- **User chooses:** Email registration or OAuth
- **Path A (Email):**
  - User enters: alex@example.com, password
  - User clicks "Sign Up"
  - System validates email format
  - System checks for existing account
  - System creates account
  - System sends verification email
  - System shows: "Check your email to verify"
  - User clicks verification link in email
  - User redirected to dashboard
- **Path B (OAuth):**
  - User clicks "Continue with Google"
  - OAuth popup opens
  - User authenticates with Google
  - OAuth callback received
  - System creates/updates account
  - User redirected to dashboard
- **Success Criteria:** Account created, user logged in

**Step 3: Welcome Screen**
- **System shows:**
  - "Welcome to InterviewMate, Alex!"
  - Quick intro: "Let's get you interview-ready in 3 easy steps"
  - Progress indicator: 1 of 3
- **User sees:** Clear path forward, feels guided
- **User action:** Clicks "Next" or "Skip" (optional)

**Step 4: Onboarding - Resume Upload**
- **System shows:**
  - "Step 1: Upload Your Resume"
  - Explanation: "We'll use this to personalize your answers"
  - Upload area: Drag & drop or click
  - Supported formats: PDF, DOCX
  - "Skip for now" option
- **User action (Path A - Upload):**
  - User drags resume.pdf to upload area
  - System shows upload progress
  - System extracts text from PDF
  - System shows preview: "Here's what we extracted..."
  - System asks: "Does this look right?"
  - User confirms or corrects
  - System saves resume data
- **User action (Path B - Skip):**
  - User clicks "Skip for now"
  - System notes: Can add resume later
  - Continues to next step
- **Success Criteria:** Resume uploaded and parsed OR user consciously skipped

**Step 5: Onboarding - Add First STAR Story**
- **System shows:**
  - "Step 2: Add Your First Success Story"
  - Explanation: "Tell us about a project or achievement you're proud of"
  - STAR framework guidance:
    - Situation: "What was the context?"
    - Task: "What needed to be done?"
    - Action: "What did you do?"
    - Result: "What was the outcome?"
  - Example story (pre-filled, optional)
  - "Skip for now" option
- **User action (Path A - Add Story):**
  - User sees pre-filled example
  - User clicks "Edit" or "Start Fresh"
  - User fills in:
    - Title: "Led Team Hackathon Project"
    - Situation: "My bootcamp team was struggling with direction..."
    - Task: "I needed to get us aligned and deliver a working app..."
    - Action: "I organized daily standups, divided work by skills..."
    - Result: "We won 1st place and I learned leadership..."
  - User clicks "Save"
  - System saves story
  - System shows: "Great! We'll use this in your answers."
- **User action (Path B - Skip):**
  - User clicks "Skip for now"
  - System notes: Can add stories later
  - Continues to next step
- **Success Criteria:** First STAR story added OR user consciously skipped

**Step 6: Onboarding - Complete**
- **System shows:**
  - "You're All Set!"
  - Summary of what user added
  - "Ready for your first practice session?"
  - CTA: "Start Practicing"
  - Secondary CTA: "Explore Dashboard"
- **User feels:** Accomplished, ready to start
- **User action:** Clicks "Start Practicing"
- **Success Criteria:** User reaches dashboard, onboarding complete

---

### 4.2 Flow 2: Starting a Practice Session

#### Step-by-Step Flow:

**Step 1: Dashboard (Starting Point)**
- **User is at:** Dashboard
- **User sees:**
  - Welcome message: "Hi Alex, ready to practice?"
  - Quick actions:
    - "Start Practice" (primary CTA)
    - "View History"
    - "Edit Profile"
  - Statistics widget:
    - Total practice time: 2 hours
    - Sessions completed: 5
    - Most practiced: Behavioral
  - Recent sessions list (if any)
  - Motivational tip: "Practice makes permanent!"
- **User thinks:** "Let's do a practice session"
- **User action:** Clicks "Start Practice"

**Step 2: Session Configuration**
- **System shows:** Session setup modal
  - "Let's customize your practice"
  - Dropdown: Session Type
    - Behavioral
    - Technical
    - Situational
    - Mixed (default)
  - Dropdown: Difficulty
    - Easy
    - Medium (default)
    - Hard
  - Slider: Number of questions (3-10, default 5)
  - Estimated time: "~30 minutes"
  - CTA: "Begin Practice"
- **User action:**
  - User selects: "Behavioral"
  - User selects: "Medium"
  - User leaves questions at 5
  - User clicks "Begin Practice"
- **System:**
  - Creates session record in database
  - Generates unique session ID
  - Selects 5 random behavioral questions (medium difficulty)
  - Initializes WebSocket connection
- **Success Criteria:** Session initialized, user ready to practice

**Step 3: Microphone Permission**
- **System shows:** Browser permission prompt
  - "InterviewMate.ai wants to use your microphone"
  - Explanation: "We need this to transcribe your answers"
  - Allow / Block buttons
- **User action (Path A - Allow):**
  - User clicks "Allow"
  - System gets microphone access
  - System shows: "Microphone ready ✓"
  - System shows audio level indicator (green bars)
  - Continues to practice
- **User action (Path B - Block):**
  - User clicks "Block"
  - System shows error: "We need microphone access to transcribe your answers"
  - System offers: "You can still type your answers"
  - System shows: "Or grant permission in browser settings"
- **Success Criteria:** Microphone access granted OR fallback to text input

**Step 4: First Question Displayed**
- **System shows:**
  - Question card:
    - Question number: "Question 1 of 5"
    - Category badge: "Behavioral"
    - Question text: "Tell me about a time you worked on a challenging team project."
    - Timer: "00:00" (starts when user begins speaking)
    - Suggested time: "Aim for 60-90 seconds"
  - Controls:
    - "Start Speaking" button (primary)
    - "Skip Question" (secondary)
    - "Pause Session" (icon)
    - "End Session" (icon)
  - Audio level indicator (waiting)
  - Transcription area (empty, ready)
- **User sees:** Clear question, feels prepared
- **User thinks:** "Okay, I can answer this... let me think..."
- **User action:** Clicks "Start Speaking" (or just starts talking)

**Step 5: User Speaks (Real-time Transcription)**
- **User speaks:**
  "Um, so at my bootcamp, I worked on a team project where we had to build a web app in two weeks. It was challenging because..."
- **System behavior (simultaneous):**
  - Audio captured via microphone
  - Audio buffered in 1-second chunks
  - Audio sent via WebSocket to backend
  - Backend forwards to Whisper API
  - Whisper returns transcription
  - System displays transcription in real-time:
    - "Um, so at my bootcamp,"
    - "I worked on a team project"
    - "where we had to build a web app in two weeks."
    - "It was challenging because..."
  - Timer updates: "00:03", "00:05", "00:08"...
  - Audio level indicator shows green bars (user is speaking)
- **User sees:**
  - Their words appearing on screen
  - Timer counting up
  - Visual feedback that system is listening
- **User feels:** Confident, system is working

**Step 6: User Stops Speaking (Question Detection)**
- **User action:** Stops speaking, pauses for 3 seconds
- **System detects:**
  - Silence for 3+ seconds
  - Question likely complete
  - Final transcription: "Um, so at my bootcamp, I worked on a team project where we had to build a web app in two weeks. It was challenging because not everyone had the same skill level, so I organized daily standups and divided work by strengths. We delivered on time and I learned a lot about leadership."
- **System behavior:**
  - Analyzes transcription
  - Identifies it as a complete answer (not just thinking pause)
  - Shows: "Analyzing your answer..."
  - Stops recording
  - Prepares to generate AI suggestion

**Step 7: AI Answer Generation**
- **System behavior (backend):**
  - Extracts question: "Tell me about a time you worked on a challenging team project."
  - Loads user context:
    - Resume: "Completed coding bootcamp..."
    - STAR story: "Led Team Hackathon Project"
    - Talking points: "Team player, leadership skills"
  - Sends to Claude API:
    - Question: [question text]
    - User context: [resume + STAR stories + talking points]
    - Instruction: "Generate a structured, conversational answer using STAR framework. Keep it 60-90 seconds when spoken. Use specific details from user's experience."
  - Claude generates answer (takes 2-3 seconds)
  - System receives answer
- **User sees (during generation):**
  - Loading indicator: "AI is preparing a suggested answer..."
  - Spinner animation
- **User waits:** 2-3 seconds

**Step 8: AI Answer Displayed**
- **System shows:**
  - Answer card (slides in with animation)
    - Title: "Suggested Answer"
    - AI-generated answer:
      "During my bootcamp, our team faced a challenging situation building a web app in just two weeks. The task was complicated by varying skill levels on the team. I took the initiative to organize daily standups and strategically divided work based on each person's strengths - assigning frontend to those comfortable with React, and backend to those who preferred Node.js. The result was impressive: we not only delivered on time, but won first place in the final presentation. This experience taught me that effective leadership isn't about knowing everything yourself, it's about recognizing and leveraging each team member's unique skills."
    - Action buttons:
      - "Use This Answer" (copy icon)
      - "Regenerate" (refresh icon)
      - "Edit" (pencil icon)
  - User's original answer still visible above
  - Comparison toggle: "Show Differences"
- **User sees:**
  - Well-structured answer
  - Their experience, but articulated better
  - Specific details from their STAR story
  - Professional, confident tone
- **User thinks:** "Wow, this is much better than what I said!"
- **User action (options):**
  - **Option A:** Clicks "Use This Answer" to save/copy
  - **Option B:** Clicks "Regenerate" for different version
  - **Option C:** Clicks "Edit" to modify answer
  - **Option D:** Clicks "Next Question" to continue

**Step 9: Continue to Next Question**
- **User action:** Clicks "Next Question"
- **System behavior:**
  - Saves question, user answer, and AI suggestion to database
  - Loads next question: "Question 2 of 5"
  - Displays new question: "Describe a time you failed at something. What did you learn?"
  - Resets transcription area
  - Resets timer
  - Ready for next answer
- **User:** Repeats steps 5-8 for remaining questions

**Step 10: Session Complete**
- **After 5 questions:**
  - System shows: "Great job! You've completed your session."
  - Session summary card:
    - Duration: 28 minutes
    - Questions answered: 5/5
    - AI suggestions used: 5
    - Average answer length: 75 seconds
  - Action buttons:
    - "View Transcript" (primary)
    - "Start Another Session"
    - "Back to Dashboard"
- **User feels:** Accomplished, prepared, confident
- **User action:** Clicks "View Transcript"

---

### 4.3 Flow 3: Reviewing Session History

#### Step-by-Step Flow:

**Step 1: Navigate to History**
- **User is at:** Dashboard
- **User action:** Clicks "View History"
- **System shows:**
  - Page title: "Your Practice History"
  - Filter options:
    - Date range picker
    - Session type dropdown (All, Behavioral, Technical, etc.)
    - Sort: Newest first (default)
  - Session list:
    - Each session card shows:
      - Date and time
      - Session type badge
      - Duration
      - Questions count
      - Thumbnail of first question
      - "View Details" button
  - Pagination (if many sessions)
- **User sees:** All their past sessions, organized

**Step 2: Select a Session**
- **User action:** Clicks on a recent session card
- **System shows:** Session detail page
  - Session header:
    - Date, time, duration
    - Session type
    - Questions count
  - Transcript section:
    - Question-by-question breakdown
    - Each Q&A includes:
      - Question text
      - User's spoken answer (transcription)
      - AI suggested answer
      - Toggle: "Show side-by-side comparison"
      - Timestamps
  - Export button: "Download PDF"
  - Back button: "Back to History"
- **User:** Reviews their answers, compares with AI suggestions

**Step 3: Export Transcript**
- **User action:** Clicks "Download PDF"
- **System:**
  - Generates PDF with formatted transcript
  - Includes session metadata
  - Triggers download
- **User:** Saves PDF for offline review or printing

---

### 4.4 Flow 4: Upgrading to Pro

#### Step-by-Step Flow:

**Step 1: Hit Free Tier Limit**
- **User:** Free tier user who has completed 5 sessions this month
- **User action:** Tries to start 6th session
- **System:**
  - Blocks session start
  - Shows modal:
    - "You've reached your monthly limit"
    - "Free tier: 5 sessions per month"
    - "Upgrade to Pro for unlimited practice"
    - Comparison table:
      - Free: 5 sessions, basic features
      - Pro: Unlimited, advanced features
    - CTA: "Upgrade to Pro - $19/month"
    - Secondary CTA: "Maybe Later"
- **User sees:** Value of Pro, feels limited
- **User thinks:** "$19 is worth it if I get the job"
- **User action:** Clicks "Upgrade to Pro"

**Step 2: Pricing Page**
- **System shows:**
  - Page title: "Choose Your Plan"
  - Three tiers side-by-side:
    - Free: $0 (current tier highlighted)
    - Pro: $19/month (recommended badge)
    - Premium: $49/month
  - Feature comparison matrix
  - Billing toggle: Monthly / Annual (save 20%)
  - CTA per tier: "Current Plan" / "Upgrade Now" / "Upgrade Now"
  - FAQ section below
  - Testimonials
- **User reviews:** Features, pricing, annual savings
- **User action:** Clicks "Upgrade Now" under Pro tier

**Step 3: Checkout (Stripe)**
- **System:**
  - Creates Stripe checkout session
  - Redirects to Stripe hosted checkout page
- **User sees:**
  - Stripe checkout page:
    - Product: InterviewMate Pro
    - Price: $19/month (or $182/year if annual)
    - Payment form:
      - Email (pre-filled)
      - Card number
      - Expiry, CVC
      - Billing address
    - "Subscribe" button
- **User action:**
  - Enters card: 4242 4242 4242 4242 (test card)
  - Clicks "Subscribe"
- **Stripe:**
  - Validates card
  - Processes payment
  - Creates subscription
  - Sends webhook to InterviewMate backend

**Step 4: Subscription Activated**
- **Backend receives webhook:**
  - Webhook type: "customer.subscription.created"
  - Verifies webhook signature
  - Extracts customer ID, subscription ID
  - Updates user record in database:
    - subscription_tier: "pro"
    - subscription_id: [stripe_sub_id]
    - subscription_status: "active"
    - subscription_end_date: [30 days from now]
  - Sends confirmation email
- **User:**
  - Redirected back to InterviewMate
  - Sees success message: "Welcome to Pro!"
  - Dashboard updated: "Pro" badge visible
  - Session limit removed
- **Success Criteria:** Subscription active, user has full Pro access

---

### 4.5 Flow 5: Editing Profile

#### Step-by-Step Flow:

**Step 1: Access Profile**
- **User:** Logged in, on dashboard
- **User action:** Clicks "Edit Profile" or profile icon
- **System shows:** Profile page
  - Tabs:
    - Personal Info
    - Resume
    - STAR Stories
    - Talking Points
  - Current tab: Personal Info
  - Fields:
    - Name
    - Email (read-only)
    - Target role (optional)
    - Skills (tags)
    - Years of experience
  - Save button

**Step 2: Update Personal Info**
- **User action:**
  - Updates "Target role": "Software Engineer"
  - Adds skills: "Python", "React", "Node.js"
  - Clicks "Save"
- **System:**
  - Validates inputs
  - Updates database
  - Shows success message: "Profile updated"

**Step 3: Add STAR Stories**
- **User action:** Clicks "STAR Stories" tab
- **System shows:**
  - List of existing stories
  - "Add New Story" button
  - Search and filter options
- **User action:** Clicks "Add New Story"
- **System shows:** STAR story form (as in onboarding)
- **User:** Fills out second story about technical challenge
- **User action:** Clicks "Save"
- **System:** Saves story, shows in list

**Step 4: Update Resume**
- **User action:** Clicks "Resume" tab
- **System shows:**
  - Current resume (if any)
  - Extracted text preview
  - "Upload New Resume" button
- **User action:** Uploads updated resume
- **System:**
  - Replaces old resume
  - Re-extracts text
  - Shows preview
  - Asks for confirmation

---

### 4.6 Flow 6: Cancelling Subscription

#### Step-by-Step Flow:

**Step 1: Access Subscription Settings**
- **User:** Pro subscriber, wants to cancel
- **User action:**
  - Navigates to Account/Settings
  - Clicks "Manage Subscription"
- **System shows:**
  - Current plan: Pro ($19/month)
  - Next billing date: Jan 15, 2025
  - Payment method: Visa ending in 4242
  - Buttons:
    - "Update Payment Method"
    - "Cancel Subscription" (destructive style)

**Step 2: Initiate Cancellation**
- **User action:** Clicks "Cancel Subscription"
- **System shows:** Cancellation modal
  - "Are you sure you want to cancel?"
  - "You'll lose access to:"
    - Unlimited practice sessions
    - Advanced features
    - Priority support
  - "Your access continues until: Jan 15, 2025"
  - Feedback form: "Why are you cancelling?" (optional)
    - Too expensive
    - Not using enough
    - Found alternative
    - Other
  - Buttons:
    - "Keep Subscription" (primary)
    - "Cancel Subscription" (secondary)

**Step 3: Confirm Cancellation**
- **User action:**
  - Selects reason: "Not using enough"
  - Clicks "Cancel Subscription"
- **System:**
  - Calls Stripe API to cancel subscription
  - Updates database:
    - subscription_status: "cancelled"
    - subscription_end_date: [current billing period end]
  - Sends confirmation email
  - Shows success message:
    - "Subscription cancelled"
    - "You have access until Jan 15, 2025"
    - "We're sorry to see you go"
- **User:** Continues using Pro until end of billing period

---

## 5. User Success Metrics

### 5.1 Activation Metrics
- **Account created:** User completes registration
- **Profile completed:** User uploads resume OR adds 1 STAR story
- **First session:** User completes at least 1 practice session
- **Aha moment:** User sees first AI-generated answer

**Target:** 60% of signups reach "First session"

### 5.2 Engagement Metrics
- **Weekly active users:** User completes 1+ session per week
- **Session completion rate:** User completes full session (not just starts)
- **Average session length:** 30+ minutes
- **Sessions per user per week:** 3+

**Target:** 60% weekly active users

### 5.3 Conversion Metrics
- **Free to Pro conversion:** User upgrades within 30 days
- **Time to conversion:** Days from signup to upgrade
- **Conversion trigger:** What caused user to upgrade (limit hit, feature locked, etc.)

**Target:** 5% conversion rate

### 5.4 Retention Metrics
- **Day 1 retention:** User returns day after signup
- **Day 7 retention:** User returns 7 days after signup
- **Day 30 retention:** User returns 30 days after signup
- **Churn rate:** Monthly subscription cancellations

**Target:** 60% Day 7 retention, <5% monthly churn

---

## 6. Pain Points and Solutions

### 6.1 Pain Point: User Nervous About First Session
**Problem:** New users don't know what to expect
**Solution:**
- Clear onboarding explains process
- Demo video shows real example
- First question is easy warm-up
- Friendly, encouraging UI copy

### 6.2 Pain Point: User Unsure About AI Quality
**Problem:** Users skeptical of AI-generated answers
**Solution:**
- Show side-by-side comparison (user vs AI)
- Allow regeneration for different versions
- Explain AI is a "suggestion" not a "script"
- Include testimonials from successful users

### 6.3 Pain Point: Microphone Permission Confusion
**Problem:** Users don't understand why microphone is needed
**Solution:**
- Clear explanation before requesting permission
- Show example of transcription in action
- Offer text input fallback
- Help article on troubleshooting microphone

### 6.4 Pain Point: User Overwhelmed by Too Many Features
**Problem:** New users see too much at once
**Solution:**
- Progressive disclosure: Show features gradually
- Onboarding focuses on core value (practice)
- Advanced features hidden until user is ready
- Tooltips and help hints throughout

### 6.5 Pain Point: User Doesn't See Value Before Limit
**Problem:** Free users hit 5-session limit before experiencing full value
**Solution:**
- Make first 5 sessions extremely valuable
- Show clear progress and improvement
- Highlight Pro features during free sessions
- Strategic upgrade prompts (not annoying)

---

## 7. Edge Cases and Alternate Flows

### 7.1 Network Disconnection During Session
**Scenario:** User's internet drops mid-session
**Flow:**
- System detects disconnection
- Auto-saves all data up to disconnection point
- Shows reconnection indicator
- When reconnected:
  - Offer to "Resume Session" or "End Session"
  - Restore state from last save
  - Continue seamlessly

### 7.2 User Speaks in Non-English Language
**Scenario:** User speaks in Korean during English session
**Flow:**
- Whisper transcribes Korean text
- System detects language mismatch
- Shows warning: "We detected Korean. This session is set to English. Would you like to switch?"
- User can:
  - Switch to Korean mode (Phase 2)
  - Continue in English
  - End session

### 7.3 User Doesn't Speak at All
**Scenario:** User is silent for 5 minutes
**Flow:**
- After 2 minutes: Show gentle prompt "Need help getting started?"
- After 5 minutes: Show warning "Session will timeout in 1 minute"
- After 6 minutes: Offer to end session or continue
- User can respond to continue

### 7.4 Multiple Browser Tabs Open
**Scenario:** User opens two sessions in different tabs
**Flow:**
- System detects multiple active sessions
- Shows warning in second tab: "You have an active session in another tab"
- Options:
  - "Close this session"
  - "End other session and continue here"
  - "View all active sessions"

### 7.5 Payment Failure on Renewal
**Scenario:** User's card declines on monthly renewal
**Flow:**
- Stripe webhook: "invoice.payment_failed"
- System emails user: "Payment failed, please update card"
- User has 3-day grace period
- During grace: Show banner "Payment failed, update card to continue"
- After 3 days: Downgrade to Free tier
- All Pro features locked
- Data preserved (not deleted)

---

## 8. Accessibility Considerations

### 8.1 Keyboard Navigation
- All interactive elements accessible via Tab key
- Clear focus indicators
- Logical tab order
- Keyboard shortcuts for common actions:
  - Space: Start/stop recording
  - N: Next question
  - E: End session

### 8.2 Screen Reader Support
- ARIA labels on all interactive elements
- Semantic HTML (headings, lists, buttons)
- Alt text on images
- Status announcements for dynamic content

### 8.3 Visual Accessibility
- High contrast mode available
- Minimum color contrast ratio: 4.5:1 (WCAG AA)
- Text scalable up to 200%
- No information conveyed by color alone

### 8.4 Audio Accessibility
- Option to type instead of speak
- Transcription visible in real-time
- Captions on demo videos

---

## 9. Mobile Experience

### 9.1 Responsive Design
- Layout adapts to screen size
- Touch-friendly buttons (44x44px minimum)
- No horizontal scrolling
- Optimized font sizes

### 9.2 Mobile-Specific Features
- Tap to start recording (instead of click)
- Swipe gestures (e.g., swipe to skip question)
- Reduced animations for performance
- Offline mode (Phase 2)

### 9.3 Mobile Constraints
- Audio capture works via browser (no app needed)
- WebSocket connection maintained
- Battery usage optimized

---

## 10. Notifications and Communication

### 10.1 In-App Notifications
- Session reminders (if user hasn't practiced in 3 days)
- New question bank updates
- Feature announcements
- Subscription renewal reminders

### 10.2 Email Communications
- Welcome email (onboarding)
- Verification email (signup)
- Weekly practice summary
- Payment receipts
- Subscription changes
- Re-engagement campaigns (inactive users)

### 10.3 Push Notifications (Phase 2)
- Practice reminders
- Upcoming interview prep alerts
- Milestone celebrations

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 10, 2024 | Heejin Jo | Initial user flow documentation |

---

**Approval:**
- **Product Owner:** Heejin Jo
- **Date:** December 10, 2024
- **Status:** Approved for Development

---

**Next Steps:**
1. Create wireframes based on these flows
2. Build interactive prototype
3. Conduct user testing with beta users
4. Iterate based on feedback
5. Begin development of MVP flows
