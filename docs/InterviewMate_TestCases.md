# Test Cases for InterviewMate.ai
## Comprehensive Testing Documentation

**Document Version:** 1.0  
**Date:** December 10, 2024  
**Project:** InterviewMate.ai  
**QA Lead:** Heejin Jo  
**Status:** Ready for Testing

---

## 1. Introduction

### 1.1 Purpose
This document provides comprehensive test cases for InterviewMate.ai to ensure all functional and non-functional requirements are met before launch.

### 1.2 Scope
This document covers:
- Functional testing (all features)
- Integration testing (API integrations)
- Performance testing (latency, throughput)
- Security testing (authentication, data protection)
- Usability testing (UX, accessibility)
- Edge case testing

### 1.3 Test Environment
- **Frontend:** Chrome 120+, Firefox 120+, Safari 17+
- **Backend:** Staging environment (Railway)
- **Database:** Staging database (Supabase)
- **APIs:** Staging API keys (OpenAI, Anthropic)

### 1.4 Test Data
- 10 test user accounts (various tiers)
- 50 sample resumes
- 100 sample STAR stories
- 200 sample interview questions

---

## 2. Test Case Template

Each test case follows this format:

**Test ID:** Unique identifier  
**Feature:** Feature being tested  
**Priority:** Critical/High/Medium/Low  
**Preconditions:** Required setup  
**Test Steps:** Step-by-step instructions  
**Expected Result:** What should happen  
**Actual Result:** What actually happened (to be filled during testing)  
**Status:** Pass/Fail/Blocked (to be filled during testing)  
**Notes:** Additional observations

---

## 3. Functional Test Cases

### 3.1 User Authentication

**TC-AUTH-001: User Registration with Email**
- **Priority:** Critical
- **Preconditions:** User not registered
- **Test Steps:**
  1. Navigate to registration page
  2. Enter valid email: test@example.com
  3. Enter valid password: TestPass123!
  4. Click "Sign Up"
- **Expected Result:**
  - User account created
  - Verification email sent
  - User redirected to dashboard
- **Status:** [To be filled]

**TC-AUTH-002: User Registration with Invalid Email**
- **Priority:** High
- **Preconditions:** None
- **Test Steps:**
  1. Navigate to registration page
  2. Enter invalid email: invalid-email
  3. Enter valid password: TestPass123!
  4. Click "Sign Up"
- **Expected Result:**
  - Error message: "Please enter a valid email address"
  - Registration blocked
- **Status:** [To be filled]

**TC-AUTH-003: User Registration with Weak Password**
- **Priority:** High
- **Preconditions:** None
- **Test Steps:**
  1. Navigate to registration page
  2. Enter valid email: test@example.com
  3. Enter weak password: 123
  4. Click "Sign Up"
- **Expected Result:**
  - Error message: "Password must be at least 8 characters"
  - Registration blocked
- **Status:** [To be filled]

**TC-AUTH-004: User Registration with Duplicate Email**
- **Priority:** High
- **Preconditions:** User already registered with test@example.com
- **Test Steps:**
  1. Navigate to registration page
  2. Enter existing email: test@example.com
  3. Enter valid password: TestPass123!
  4. Click "Sign Up"
- **Expected Result:**
  - Error message: "Email already registered"
  - Registration blocked
- **Status:** [To be filled]

**TC-AUTH-005: User Login with Valid Credentials**
- **Priority:** Critical
- **Preconditions:** User registered and verified
- **Test Steps:**
  1. Navigate to login page
  2. Enter email: test@example.com
  3. Enter password: TestPass123!
  4. Click "Log In"
- **Expected Result:**
  - User authenticated
  - JWT token issued
  - User redirected to dashboard
- **Status:** [To be filled]

**TC-AUTH-006: User Login with Invalid Password**
- **Priority:** High
- **Preconditions:** User registered
- **Test Steps:**
  1. Navigate to login page
  2. Enter email: test@example.com
  3. Enter wrong password: WrongPass123
  4. Click "Log In"
- **Expected Result:**
  - Error message: "Invalid email or password"
  - Login blocked
- **Status:** [To be filled]

**TC-AUTH-007: Account Lockout After Failed Attempts**
- **Priority:** High
- **Preconditions:** User registered
- **Test Steps:**
  1. Attempt login with wrong password 5 times
  2. Attempt 6th login with wrong password
- **Expected Result:**
  - After 5th attempt: Error message
  - After 6th attempt: "Account locked. Please reset password."
  - Account locked for 15 minutes
- **Status:** [To be filled]

**TC-AUTH-008: User Logout**
- **Priority:** High
- **Preconditions:** User logged in
- **Test Steps:**
  1. Click "Logout" button
- **Expected Result:**
  - User logged out
  - JWT token invalidated
  - User redirected to login page
  - Local storage cleared
- **Status:** [To be filled]

**TC-AUTH-009: Password Reset Request**
- **Priority:** High
- **Preconditions:** User registered
- **Test Steps:**
  1. Navigate to login page
  2. Click "Forgot Password"
  3. Enter email: test@example.com
  4. Click "Send Reset Link"
- **Expected Result:**
  - Reset email sent
  - Message: "Password reset link sent to your email"
- **Status:** [To be filled]

**TC-AUTH-010: OAuth Login with Google**
- **Priority:** Medium
- **Preconditions:** User has Google account
- **Test Steps:**
  1. Navigate to login page
  2. Click "Continue with Google"
  3. Authenticate with Google
- **Expected Result:**
  - User authenticated via Google OAuth
  - User redirected to dashboard
  - Account created if first time
- **Status:** [To be filled]

---

### 3.2 Profile Management

**TC-PROFILE-001: Upload Resume (PDF)**
- **Priority:** Critical
- **Preconditions:** User logged in
- **Test Steps:**
  1. Navigate to Profile page
  2. Click "Upload Resume"
  3. Select valid PDF file (< 5MB)
  4. Click "Upload"
- **Expected Result:**
  - File uploaded successfully
  - Text extracted and displayed
  - Success message shown
- **Status:** [To be filled]

**TC-PROFILE-002: Upload Resume (File Too Large)**
- **Priority:** High
- **Preconditions:** User logged in
- **Test Steps:**
  1. Navigate to Profile page
  2. Click "Upload Resume"
  3. Select PDF file (> 5MB)
  4. Click "Upload"
- **Expected Result:**
  - Error message: "File size must be less than 5MB"
  - Upload blocked
- **Status:** [To be filled]

**TC-PROFILE-003: Upload Resume (Invalid Format)**
- **Priority:** High
- **Preconditions:** User logged in
- **Test Steps:**
  1. Navigate to Profile page
  2. Click "Upload Resume"
  3. Select .exe file
  4. Click "Upload"
- **Expected Result:**
  - Error message: "Only PDF and DOCX files are supported"
  - Upload blocked
- **Status:** [To be filled]

**TC-PROFILE-004: Create STAR Story**
- **Priority:** Critical
- **Preconditions:** User logged in
- **Test Steps:**
  1. Navigate to Profile page
  2. Click "Add STAR Story"
  3. Enter Title: "Led Team Project"
  4. Enter Situation: "Team was behind schedule"
  5. Enter Task: "Deliver project on time"
  6. Enter Action: "Reorganized workflow, delegated tasks"
  7. Enter Result: "Delivered 2 weeks early"
  8. Add tags: "Leadership", "Project Management"
  9. Click "Save"
- **Expected Result:**
  - STAR story saved
  - Story appears in list
  - Success message shown
- **Status:** [To be filled]

**TC-PROFILE-005: Edit STAR Story**
- **Priority:** High
- **Preconditions:** STAR story exists
- **Test Steps:**
  1. Navigate to Profile page
  2. Click "Edit" on existing story
  3. Modify Result field
  4. Click "Save"
- **Expected Result:**
  - Story updated
  - Changes reflected immediately
  - Success message shown
- **Status:** [To be filled]

**TC-PROFILE-006: Delete STAR Story**
- **Priority:** High
- **Preconditions:** STAR story exists
- **Test Steps:**
  1. Navigate to Profile page
  2. Click "Delete" on existing story
  3. Confirm deletion
- **Expected Result:**
  - Story deleted
  - Story removed from list
  - Confirmation message shown
- **Status:** [To be filled]

**TC-PROFILE-007: Add Talking Points**
- **Priority:** Medium
- **Preconditions:** User logged in
- **Test Steps:**
  1. Navigate to Profile page
  2. Click "Add Talking Point"
  3. Enter category: "Technical Skills"
  4. Enter point: "5 years Python experience"
  5. Click "Save"
- **Expected Result:**
  - Talking point saved
  - Appears in profile
  - Success message shown
- **Status:** [To be filled]

---

### 3.3 Audio Capture and Transcription

**TC-AUDIO-001: Request Microphone Permission**
- **Priority:** Critical
- **Preconditions:** User on practice session page, microphone available
- **Test Steps:**
  1. Navigate to practice session page
  2. Observe browser permission prompt
- **Expected Result:**
  - Browser requests microphone permission
  - Clear explanation of why permission needed
- **Status:** [To be filled]

**TC-AUDIO-002: Start Audio Capture**
- **Priority:** Critical
- **Preconditions:** Microphone permission granted
- **Test Steps:**
  1. Start practice session
  2. Click "Start Speaking"
  3. Speak into microphone: "Hello, this is a test"
- **Expected Result:**
  - Audio level indicator shows activity
  - "Recording" status displayed
  - No errors
- **Status:** [To be filled]

**TC-AUDIO-003: Real-time Transcription**
- **Priority:** Critical
- **Preconditions:** Audio capture active
- **Test Steps:**
  1. Speak clearly: "Tell me about yourself"
  2. Observe transcription display
- **Expected Result:**
  - Transcription appears within 2 seconds
  - Text matches spoken words (>90% accuracy)
  - Transcription updates in real-time
- **Status:** [To be filled]

**TC-AUDIO-004: Handle Microphone Disconnection**
- **Priority:** High
- **Preconditions:** Audio capture active
- **Test Steps:**
  1. Start speaking
  2. Disconnect microphone
  3. Observe behavior
- **Expected Result:**
  - Error message: "Microphone disconnected"
  - Session paused
  - Option to reconnect or end session
- **Status:** [To be filled]

**TC-AUDIO-005: Audio Quality with Background Noise**
- **Priority:** Medium
- **Preconditions:** Audio capture active
- **Test Steps:**
  1. Play background music
  2. Speak: "What is your greatest weakness?"
  3. Observe transcription
- **Expected Result:**
  - Transcription still accurate (>80%)
  - Background noise filtered
- **Status:** [To be filled]

**TC-AUDIO-006: Multiple Audio Input Devices**
- **Priority:** Medium
- **Preconditions:** Multiple microphones connected
- **Test Steps:**
  1. Navigate to practice session
  2. Open audio device selector
  3. Select different microphone
- **Expected Result:**
  - Available devices listed
  - Selected device used for capture
  - Selection persists across sessions
- **Status:** [To be filled]

---

### 3.4 AI Answer Generation

**TC-AI-001: Generate Answer from Question**
- **Priority:** Critical
- **Preconditions:** User profile complete, session active
- **Test Steps:**
  1. Speak question: "Tell me about a time you failed"
  2. Wait for AI response
- **Expected Result:**
  - Answer generated within 3 seconds
  - Answer uses user's STAR stories
  - Answer is 60-90 seconds when spoken
  - Natural, conversational tone
- **Status:** [To be filled]

**TC-AI-002: Answer Personalization**
- **Priority:** High
- **Preconditions:** User has resume and STAR stories
- **Test Steps:**
  1. Ask behavioral question
  2. Review generated answer
  3. Verify answer references user profile
- **Expected Result:**
  - Answer includes specific details from resume
  - Answer uses relevant STAR story
  - Answer mentions user's skills/experiences
- **Status:** [To be filled]

**TC-AI-003: Regenerate Answer**
- **Priority:** Medium
- **Preconditions:** Answer already generated
- **Test Steps:**
  1. Click "Regenerate Answer"
  2. Wait for new answer
- **Expected Result:**
  - New answer generated
  - Different from previous answer
  - Still relevant and high quality
- **Status:** [To be filled]

**TC-AI-004: Handle API Failure**
- **Priority:** High
- **Preconditions:** Simulate API failure (rate limit or error)
- **Test Steps:**
  1. Ask question
  2. Trigger API error
- **Expected Result:**
  - System retries (up to 3 times)
  - If still fails: Error message shown
  - Option to try again
  - Session state preserved
- **Status:** [To be filled]

**TC-AI-005: Answer for Technical Question**
- **Priority:** High
- **Preconditions:** Session active
- **Test Steps:**
  1. Ask: "Explain the difference between REST and GraphQL"
  2. Wait for answer
- **Expected Result:**
  - Answer is technically accurate
  - Appropriate level of detail
  - Structured clearly
- **Status:** [To be filled]

**TC-AI-006: Multiple Answer Variations (Pro Tier)**
- **Priority:** Medium
- **Preconditions:** User has Pro subscription
- **Test Steps:**
  1. Ask question
  2. Wait for answers
- **Expected Result:**
  - 2-3 answer variations provided
  - Variations have different approaches
  - All answers are high quality
- **Status:** [To be filled]

---

### 3.5 Practice Sessions

**TC-SESSION-001: Start Practice Session**
- **Priority:** Critical
- **Preconditions:** User logged in
- **Test Steps:**
  1. Navigate to dashboard
  2. Click "Start Practice"
  3. Select session type: "Behavioral"
  4. Select difficulty: "Medium"
  5. Click "Begin"
- **Expected Result:**
  - Session initialized
  - Unique session ID created
  - First question displayed
  - Timer starts
- **Status:** [To be filled]

**TC-SESSION-002: Answer Multiple Questions**
- **Priority:** Critical
- **Preconditions:** Session active
- **Test Steps:**
  1. Answer first question
  2. Click "Next Question"
  3. Answer second question
  4. Click "Next Question"
  5. Repeat for 5 questions
- **Expected Result:**
  - Questions progress sequentially
  - Each answer saved
  - Progress indicator updates
  - No data loss
- **Status:** [To be filled]

**TC-SESSION-003: Pause and Resume Session**
- **Priority:** High
- **Preconditions:** Session active
- **Test Steps:**
  1. Answer 2 questions
  2. Click "Pause"
  3. Wait 1 minute
  4. Click "Resume"
- **Expected Result:**
  - Session paused
  - Timer stops
  - Resume continues from same point
  - No data loss
- **Status:** [To be filled]

**TC-SESSION-004: End Session Early**
- **Priority:** High
- **Preconditions:** Session active, 3 questions answered
- **Test Steps:**
  1. Click "End Session"
  2. Confirm end
- **Expected Result:**
  - Session ended
  - Partial data saved
  - Session summary displayed
- **Status:** [To be filled]

**TC-SESSION-005: Session Auto-save**
- **Priority:** High
- **Preconditions:** Session active
- **Test Steps:**
  1. Answer questions for 2 minutes
  2. Simulate network disconnection
  3. Reconnect network
- **Expected Result:**
  - Session auto-saved every 30 seconds
  - Data recovered on reconnect
  - No data loss
- **Status:** [To be filled]

**TC-SESSION-006: Session Time Limit (Free Tier)**
- **Priority:** Medium
- **Preconditions:** Free tier user, session active for 29 minutes
- **Test Steps:**
  1. Continue session past 30 minutes
  2. Observe behavior
- **Expected Result:**
  - Warning at 28 minutes
  - Session ends at 30 minutes
  - Prompt to upgrade to Pro
  - Data saved
- **Status:** [To be filled]

**TC-SESSION-007: Random Question Selection**
- **Priority:** Medium
- **Preconditions:** None
- **Test Steps:**
  1. Start 3 practice sessions
  2. Observe questions in each session
- **Expected Result:**
  - Questions are different each time
  - No duplicate questions within session
  - Questions match selected category/difficulty
- **Status:** [To be filled]

**TC-SESSION-008: Session Summary Display**
- **Priority:** High
- **Preconditions:** Session completed
- **Test Steps:**
  1. Complete practice session
  2. Review session summary
- **Expected Result:**
  - Summary shows: duration, questions asked, answers generated
  - Transcript available for download
  - Insights/areas for improvement highlighted
  - Next steps suggested
- **Status:** [To be filled]

---

### 3.6 Session History and Analytics

**TC-HISTORY-001: View Session History List**
- **Priority:** High
- **Preconditions:** User has completed 5 sessions
- **Test Steps:**
  1. Navigate to "History" page
  2. Observe session list
- **Expected Result:**
  - All sessions displayed
  - Each session shows: date, duration, type
  - Sessions sorted by date (newest first)
- **Status:** [To be filled]

**TC-HISTORY-002: Filter Session History**
- **Priority:** Medium
- **Preconditions:** User has sessions of different types
- **Test Steps:**
  1. Navigate to "History" page
  2. Select filter: "Behavioral"
  3. Observe filtered results
- **Expected Result:**
  - Only behavioral sessions shown
  - Filter updates results instantly
  - Count of filtered sessions displayed
- **Status:** [To be filled]

**TC-HISTORY-003: View Session Details**
- **Priority:** High
- **Preconditions:** Session exists in history
- **Test Steps:**
  1. Navigate to "History" page
  2. Click on a session
  3. Review session details
- **Expected Result:**
  - Full transcript displayed
  - All questions and answers shown
  - Timestamps for each interaction
  - Export option available
- **Status:** [To be filled]

**TC-HISTORY-004: Export Session Transcript**
- **Priority:** Medium
- **Preconditions:** Session details open
- **Test Steps:**
  1. Click "Export as PDF"
  2. Save file
  3. Open PDF
- **Expected Result:**
  - PDF generated and downloaded
  - PDF contains full transcript
  - PDF formatted cleanly
- **Status:** [To be filled]

**TC-HISTORY-005: Analytics Dashboard**
- **Priority:** Medium
- **Preconditions:** User has 10+ sessions
- **Test Steps:**
  1. Navigate to "Analytics" page
  2. Review dashboard
- **Expected Result:**
  - Total practice time displayed
  - Number of sessions shown
  - Most practiced categories shown
  - Improvement trends visualized
- **Status:** [To be filled]

---

### 3.7 Subscription Management

**TC-SUB-001: View Subscription Plans**
- **Priority:** High
- **Preconditions:** User logged in (Free tier)
- **Test Steps:**
  1. Navigate to "Pricing" page
  2. Review plans
- **Expected Result:**
  - Free, Pro, Premium tiers displayed
  - Features clearly listed for each tier
  - Pricing shown clearly
  - Current tier highlighted
- **Status:** [To be filled]

**TC-SUB-002: Upgrade to Pro (Monthly)**
- **Priority:** Critical
- **Preconditions:** User on Free tier
- **Test Steps:**
  1. Navigate to "Pricing" page
  2. Click "Upgrade to Pro"
  3. Select "Monthly" billing
  4. Enter payment details (test card: 4242 4242 4242 4242)
  5. Click "Subscribe"
- **Expected Result:**
  - Redirected to Stripe checkout
  - Payment processed successfully
  - Subscription activated immediately
  - Confirmation email sent
  - User tier updated to Pro
- **Status:** [To be filled]

**TC-SUB-003: Upgrade to Pro (Annual)**
- **Priority:** High
- **Preconditions:** User on Free tier
- **Test Steps:**
  1. Navigate to "Pricing" page
  2. Click "Upgrade to Pro"
  3. Select "Annual" billing
  4. Observe pricing
  5. Complete payment
- **Expected Result:**
  - 20% discount applied ($182 vs $228)
  - Annual price shown clearly
  - Payment successful
  - Subscription valid for 12 months
- **Status:** [To be filled]

**TC-SUB-004: Failed Payment Handling**
- **Priority:** High
- **Preconditions:** User attempting to upgrade
- **Test Steps:**
  1. Navigate to "Pricing" page
  2. Click "Upgrade to Pro"
  3. Enter invalid card (test card: 4000 0000 0000 0002)
  4. Click "Subscribe"
- **Expected Result:**
  - Payment fails
  - Error message: "Payment failed. Please check your card details."
  - User remains on Free tier
  - Option to retry
- **Status:** [To be filled]

**TC-SUB-005: Usage Limit Enforcement (Free Tier)**
- **Priority:** High
- **Preconditions:** Free user has completed 4 sessions this month
- **Test Steps:**
  1. Complete 5th session
  2. Attempt to start 6th session
- **Expected Result:**
  - 5th session completes successfully
  - When starting 6th: Error message "You've reached your monthly limit"
  - Prompt to upgrade to Pro
  - Session blocked
- **Status:** [To be filled]

**TC-SUB-006: Cancel Subscription**
- **Priority:** High
- **Preconditions:** User has Pro subscription
- **Test Steps:**
  1. Navigate to "Account" page
  2. Click "Manage Subscription"
  3. Click "Cancel Subscription"
  4. Confirm cancellation
- **Expected Result:**
  - Subscription cancelled
  - Access continues until end of billing period
  - Confirmation email sent
  - No further charges
- **Status:** [To be filled]

**TC-SUB-007: Reactivate Cancelled Subscription**
- **Priority:** Medium
- **Preconditions:** User cancelled Pro subscription
- **Test Steps:**
  1. Navigate to "Account" page
  2. Click "Reactivate Subscription"
- **Expected Result:**
  - Subscription reactivated
  - Billing resumes
  - Access restored immediately
- **Status:** [To be filled]

---

## 4. Integration Test Cases

### 4.1 OpenAI Whisper API Integration

**TC-INT-001: Whisper API Authentication**
- **Priority:** Critical
- **Preconditions:** Valid API key configured
- **Test Steps:**
  1. Send test audio to Whisper API
  2. Verify authentication
- **Expected Result:**
  - API authenticates successfully
  - No authentication errors
- **Status:** [To be filled]

**TC-INT-002: Whisper API Rate Limiting**
- **Priority:** High
- **Preconditions:** None
- **Test Steps:**
  1. Send 60 requests within 1 minute
  2. Observe behavior
- **Expected Result:**
  - Requests processed up to rate limit
  - Rate limit errors handled gracefully
  - Retry logic implemented
- **Status:** [To be filled]

**TC-INT-003: Whisper API Response Parsing**
- **Priority:** Critical
- **Preconditions:** Audio sent to API
- **Test Steps:**
  1. Send audio: "This is a test transcription"
  2. Parse response
- **Expected Result:**
  - Response parsed correctly
  - Transcription text extracted
  - Confidence score available
- **Status:** [To be filled]

---

### 4.2 Anthropic Claude API Integration

**TC-INT-004: Claude API Authentication**
- **Priority:** Critical
- **Preconditions:** Valid API key configured
- **Test Steps:**
  1. Send test request to Claude API
  2. Verify authentication
- **Expected Result:**
  - API authenticates successfully
  - No authentication errors
- **Status:** [To be filled]

**TC-INT-005: Claude API Answer Generation**
- **Priority:** Critical
- **Preconditions:** None
- **Test Steps:**
  1. Send question and user context to Claude
  2. Receive answer
- **Expected Result:**
  - Answer generated successfully
  - Answer relevant to question
  - Answer uses provided context
  - Response within 3 seconds
- **Status:** [To be filled]

**TC-INT-006: Claude API Error Handling**
- **Priority:** High
- **Preconditions:** Simulate API error
- **Test Steps:**
  1. Send malformed request
  2. Observe error handling
- **Expected Result:**
  - Error caught and logged
  - User-friendly error message shown
  - System remains stable
- **Status:** [To be filled]

---

### 4.3 Stripe Payment Integration

**TC-INT-007: Stripe Checkout Session**
- **Priority:** Critical
- **Preconditions:** User upgrading to Pro
- **Test Steps:**
  1. Initiate checkout
  2. Complete payment with test card
- **Expected Result:**
  - Checkout session created
  - Payment processed successfully
  - Webhook received
  - Subscription activated
- **Status:** [To be filled]

**TC-INT-008: Stripe Webhook Handling**
- **Priority:** Critical
- **Preconditions:** Subscription event occurs
- **Test Steps:**
  1. Trigger subscription.created webhook
  2. Verify webhook processing
- **Expected Result:**
  - Webhook received
  - Signature verified
  - Database updated
  - User tier changed
- **Status:** [To be filled]

---

### 4.4 Supabase Database Integration

**TC-INT-009: Database Connection**
- **Priority:** Critical
- **Preconditions:** None
- **Test Steps:**
  1. Start application
  2. Verify database connection
- **Expected Result:**
  - Connection established
  - No connection errors
  - Connection pooling works
- **Status:** [To be filled]

**TC-INT-010: User Data CRUD Operations**
- **Priority:** Critical
- **Preconditions:** Database connected
- **Test Steps:**
  1. Create user
  2. Read user data
  3. Update user data
  4. Delete user
- **Expected Result:**
  - All CRUD operations successful
  - Data consistency maintained
  - No data loss
- **Status:** [To be filled]

---

## 5. Performance Test Cases

**TC-PERF-001: Page Load Time**
- **Priority:** High
- **Preconditions:** None
- **Test Steps:**
  1. Clear cache
  2. Navigate to landing page
  3. Measure load time
- **Expected Result:**
  - Page loads in <2 seconds
  - First Contentful Paint <1 second
- **Status:** [To be filled]

**TC-PERF-002: Audio Transcription Latency**
- **Priority:** Critical
- **Preconditions:** Session active
- **Test Steps:**
  1. Speak a sentence
  2. Measure time to transcription display
- **Expected Result:**
  - Transcription appears in <2 seconds
  - No noticeable lag
- **Status:** [To be filled]

**TC-PERF-003: Answer Generation Speed**
- **Priority:** Critical
- **Preconditions:** Question detected
- **Test Steps:**
  1. Ask question
  2. Measure time to answer display
- **Expected Result:**
  - Answer generated in <3 seconds (95th percentile)
  - No timeout errors
- **Status:** [To be filled]

**TC-PERF-004: Concurrent Users**
- **Priority:** High
- **Preconditions:** Load testing tool configured
- **Test Steps:**
  1. Simulate 100 concurrent users
  2. All users start practice sessions
  3. Monitor performance
- **Expected Result:**
  - System handles 100 concurrent users
  - No performance degradation
  - No crashes
- **Status:** [To be filled]

**TC-PERF-005: Database Query Performance**
- **Priority:** Medium
- **Preconditions:** Database has 1000+ users
- **Test Steps:**
  1. Execute common queries (fetch user, fetch sessions)
  2. Measure query time
- **Expected Result:**
  - Queries execute in <100ms (average)
  - No slow queries (>1 second)
- **Status:** [To be filled]

---

## 6. Security Test Cases

**TC-SEC-001: Password Hashing**
- **Priority:** Critical
- **Preconditions:** None
- **Test Steps:**
  1. Create user with password: TestPass123!
  2. Inspect database
- **Expected Result:**
  - Password hashed using bcrypt
  - Plain text password not visible
  - Hash cost factor >=12
- **Status:** [To be filled]

**TC-SEC-002: JWT Token Validation**
- **Priority:** Critical
- **Preconditions:** User logged in
- **Test Steps:**
  1. Capture JWT token
  2. Tamper with token
  3. Send request with tampered token
- **Expected Result:**
  - Tampered token rejected
  - 401 Unauthorized error
  - User not authenticated
- **Status:** [To be filled]

**TC-SEC-003: SQL Injection Prevention**
- **Priority:** Critical
- **Preconditions:** None
- **Test Steps:**
  1. Enter SQL injection in input field: ' OR '1'='1
  2. Submit form
- **Expected Result:**
  - Input sanitized
  - SQL injection prevented
  - No database access
- **Status:** [To be filled]

**TC-SEC-004: XSS Prevention**
- **Priority:** Critical
- **Preconditions:** None
- **Test Steps:**
  1. Enter script tag in input: <script>alert('XSS')</script>
  2. Submit form
- **Expected Result:**
  - Script tag sanitized
  - XSS attack prevented
  - Script not executed
- **Status:** [To be filled]

**TC-SEC-005: HTTPS Enforcement**
- **Priority:** Critical
- **Preconditions:** None
- **Test Steps:**
  1. Access site via HTTP
  2. Observe behavior
- **Expected Result:**
  - Redirected to HTTPS
  - All communication encrypted
- **Status:** [To be filled]

**TC-SEC-006: Rate Limiting**
- **Priority:** High
- **Preconditions:** None
- **Test Steps:**
  1. Send 150 requests in 1 minute
  2. Observe response
- **Expected Result:**
  - Requests limited to 100/minute
  - 429 Too Many Requests error after limit
  - User not blocked permanently
- **Status:** [To be filled]

**TC-SEC-007: API Key Protection**
- **Priority:** Critical
- **Preconditions:** None
- **Test Steps:**
  1. Inspect frontend source code
  2. Search for API keys
- **Expected Result:**
  - No API keys in frontend code
  - API keys stored securely in backend
  - Environment variables used
- **Status:** [To be filled]

---

## 7. Usability Test Cases

**TC-USABILITY-001: Keyboard Navigation**
- **Priority:** Medium
- **Preconditions:** None
- **Test Steps:**
  1. Navigate site using only keyboard (Tab, Enter, Arrow keys)
  2. Test all major flows
- **Expected Result:**
  - All interactive elements accessible
  - Focus indicators visible
  - Logical tab order
- **Status:** [To be filled]

**TC-USABILITY-002: Screen Reader Compatibility**
- **Priority:** Medium
- **Preconditions:** Screen reader installed
- **Test Steps:**
  1. Enable screen reader
  2. Navigate through application
- **Expected Result:**
  - All content readable by screen reader
  - ARIA labels present
  - Semantic HTML used
- **Status:** [To be filled]

**TC-USABILITY-003: Mobile Responsiveness**
- **Priority:** High
- **Preconditions:** None
- **Test Steps:**
  1. Open site on mobile device (375x667)
  2. Test all features
- **Expected Result:**
  - Layout adapts to mobile
  - All features accessible
  - Touch targets adequate (44x44px)
  - No horizontal scroll
- **Status:** [To be filled]

**TC-USABILITY-004: Dark Mode Toggle**
- **Priority:** Medium
- **Preconditions:** None
- **Test Steps:**
  1. Toggle dark mode on
  2. Navigate through application
  3. Toggle dark mode off
- **Expected Result:**
  - Theme changes instantly
  - All components styled correctly
  - Preference saved
- **Status:** [To be filled]

**TC-USABILITY-005: Error Message Clarity**
- **Priority:** High
- **Preconditions:** None
- **Test Steps:**
  1. Trigger various errors
  2. Review error messages
- **Expected Result:**
  - Error messages clear and specific
  - Suggest how to fix
  - No technical jargon
- **Status:** [To be filled]

---

## 8. Edge Case Test Cases

**TC-EDGE-001: Very Long Session (2 hours)**
- **Priority:** Medium
- **Preconditions:** Pro user
- **Test Steps:**
  1. Start practice session
  2. Continue for 2 hours
  3. End session
- **Expected Result:**
  - Session completes successfully
  - All data saved
  - No memory leaks
  - No performance degradation
- **Status:** [To be filled]

**TC-EDGE-002: Extremely Long Resume (10,000 words)**
- **Priority:** Low
- **Preconditions:** None
- **Test Steps:**
  1. Upload very long resume PDF
  2. Process resume
- **Expected Result:**
  - Resume processed successfully
  - Text extraction completes
  - No timeout errors
  - Or: Error message if too long
- **Status:** [To be filled]

**TC-EDGE-003: Very Fast Speaking**
- **Priority:** Medium
- **Preconditions:** Session active
- **Test Steps:**
  1. Speak very quickly for 30 seconds
  2. Observe transcription
- **Expected Result:**
  - Transcription keeps up
  - Accuracy maintained (>80%)
  - No crashes
- **Status:** [To be filled]

**TC-EDGE-004: Silent Audio Input**
- **Priority:** Medium
- **Preconditions:** Session active
- **Test Steps:**
  1. Remain silent for 2 minutes
  2. Observe behavior
- **Expected Result:**
  - System waits patiently
  - No errors or crashes
  - Session remains active
  - Or: Timeout warning after 5 minutes
- **Status:** [To be filled]

**TC-EDGE-005: Network Instability**
- **Priority:** High
- **Preconditions:** Session active
- **Test Steps:**
  1. Start practice session
  2. Simulate intermittent network (on/off every 10 seconds)
  3. Continue for 5 minutes
- **Expected Result:**
  - System handles reconnections gracefully
  - Data saved during connectivity
  - No data loss
  - Clear status indicators
- **Status:** [To be filled]

---

## 9. Test Execution Summary

### 9.1 Test Coverage
- **Total Test Cases:** 80+
- **Critical Priority:** 25
- **High Priority:** 30
- **Medium Priority:** 20
- **Low Priority:** 5

### 9.2 Testing Schedule
- **Week 1:** Authentication, Profile, Audio (TC-AUTH, TC-PROFILE, TC-AUDIO)
- **Week 2:** AI, Sessions, History (TC-AI, TC-SESSION, TC-HISTORY)
- **Week 3:** Subscription, Integration, Performance (TC-SUB, TC-INT, TC-PERF)
- **Week 4:** Security, Usability, Edge Cases (TC-SEC, TC-USABILITY, TC-EDGE)
- **Week 5:** Regression testing, bug fixes, final validation

### 9.3 Acceptance Criteria
- 100% of Critical test cases pass
- 95%+ of High priority test cases pass
- 90%+ of Medium priority test cases pass
- No critical bugs in production

### 9.4 Bug Severity Definitions
- **Critical:** System crash, data loss, security breach
- **High:** Major feature broken, significant UX issue
- **Medium:** Minor feature issue, cosmetic bug
- **Low:** Enhancement, nice-to-have

---

## 10. Defect Tracking

**Defect Template:**
- **Bug ID:** Unique identifier
- **Title:** Brief description
- **Severity:** Critical/High/Medium/Low
- **Steps to Reproduce:** Detailed steps
- **Expected Result:** What should happen
- **Actual Result:** What actually happened
- **Screenshots:** If applicable
- **Environment:** Browser, OS, version
- **Assigned To:** Developer
- **Status:** Open/In Progress/Resolved/Closed

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 10, 2024 | Heejin Jo | Initial test case document created |

---

**Approval:**
- **QA Lead:** Heejin Jo
- **Date:** December 10, 2024
- **Status:** Ready for Test Execution
