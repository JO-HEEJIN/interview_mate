# UML Diagrams for InterviewMate.ai
## System Architecture and Design

**Document Version:** 1.0
**Date:** December 10, 2024
**Project:** InterviewMate.ai

---

## 1. System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Microphone[Microphone Input]
        UI[Next.js UI]
    end
    
    subgraph "Application Layer"
        NextJS[Next.js Frontend]
        FastAPI[FastAPI Backend]
        WS[WebSocket Server]
        Auth[Authentication Service]
    end
    
    subgraph "AI Services Layer"
        Whisper[OpenAI Whisper API]
        Claude[Anthropic Claude API]
        GPT4[OpenAI GPT-4 API]
    end
    
    subgraph "Data Layer"
        Supabase[(Supabase PostgreSQL)]
        Storage[Supabase Storage]
        Cache[Redis Cache]
    end
    
    subgraph "External Services"
        Stripe[Stripe Payments]
        Email[Email Service]
        Analytics[PostHog Analytics]
    end
    
    Browser --> UI
    Microphone --> UI
    UI --> NextJS
    NextJS <--> WS
    WS <--> FastAPI
    NextJS --> Auth
    Auth --> Supabase
    
    FastAPI --> Whisper
    FastAPI --> Claude
    FastAPI --> GPT4
    FastAPI <--> Supabase
    FastAPI <--> Storage
    FastAPI <--> Cache
    
    NextJS --> Stripe
    FastAPI --> Email
    NextJS --> Analytics
```

---

## 2. Component Diagram

```mermaid
graph LR
    subgraph "Frontend Components"
        AC[Audio Capture]
        TR[Transcription Display]
        AG[Answer Generator UI]
        PM[Profile Manager]
        SH[Session History]
    end
    
    subgraph "Backend Components"
        AP[Audio Processor]
        QD[Question Detector]
        AG_Backend[Answer Generator]
        UD[User Data Manager]
        SM[Session Manager]
    end
    
    subgraph "Data Models"
        User[User Model]
        Profile[Profile Model]
        Session[Session Model]
        Question[Question Model]
        Answer[Answer Model]
    end
    
    AC --> AP
    AP --> QD
    QD --> AG_Backend
    AG_Backend --> AG
    
    PM --> UD
    UD --> User
    UD --> Profile
    
    SH --> SM
    SM --> Session
    SM --> Question
    SM --> Answer
```

---

## 3. Class Diagram

```mermaid
classDiagram
    class User {
        +String id
        +String email
        +String name
        +DateTime createdAt
        +DateTime updatedAt
        +String subscriptionTier
        +register()
        +login()
        +updateProfile()
    }
    
    class Profile {
        +String id
        +String userId
        +String resumeText
        +JSON starStories
        +JSON talkingPoints
        +String[] skills
        +uploadResume()
        +addStarStory()
        +updateTalkingPoints()
    }
    
    class Session {
        +String id
        +String userId
        +DateTime startTime
        +DateTime endTime
        +String sessionType
        +Integer questionCount
        +Float duration
        +startSession()
        +endSession()
        +getTranscript()
    }
    
    class Question {
        +String id
        +String sessionId
        +String questionText
        +DateTime timestamp
        +String category
        +String difficulty
        +detectQuestion()
        +categorize()
    }
    
    class Answer {
        +String id
        +String questionId
        +String answerText
        +String userResponse
        +Float confidence
        +Boolean wasUsed
        +generate()
        +evaluate()
        +save()
    }
    
    class AudioStream {
        +String id
        +String sessionId
        +Blob audioData
        +Float duration
        +capture()
        +process()
        +transcribe()
    }
    
    class AIService {
        +String apiKey
        +String model
        +transcribe(audio)
        +generateAnswer(question, context)
        +evaluateResponse(response)
    }
    
    User "1" --> "1" Profile
    User "1" --> "*" Session
    Session "1" --> "*" Question
    Question "1" --> "1" Answer
    Session "1" --> "1" AudioStream
    AIService --> Answer
    AIService --> AudioStream
```

---

## 4. Sequence Diagram - Real-time Interview Practice

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant WS as WebSocket
    participant BE as Backend
    participant W as Whisper API
    participant C as Claude API
    participant DB as Database
    
    U->>UI: Start Practice Session
    UI->>BE: Create Session
    BE->>DB: Save Session
    DB-->>BE: Session ID
    BE-->>UI: Session Created
    
    UI->>WS: Open WebSocket Connection
    WS-->>UI: Connection Established
    
    U->>UI: Speak (Audio Input)
    UI->>WS: Stream Audio Chunks
    WS->>BE: Forward Audio Stream
    BE->>W: Transcribe Audio
    W-->>BE: Transcription Text
    BE->>UI: Real-time Transcription
    UI-->>U: Display Transcription
    
    BE->>BE: Detect Complete Question
    BE->>DB: Fetch User Profile
    DB-->>BE: Profile Data
    
    BE->>C: Generate Answer (Question + Profile)
    C-->>BE: AI-Generated Answer
    
    BE->>DB: Save Question & Answer
    BE->>UI: Send Answer
    UI-->>U: Display Suggested Answer
    
    U->>UI: End Session
    UI->>WS: Close Connection
    UI->>BE: End Session
    BE->>DB: Update Session Record
    DB-->>BE: Confirmed
    BE-->>UI: Session Summary
    UI-->>U: Show Session Results
```

---

## 5. State Diagram - Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Initializing: Start Session
    Initializing --> Ready: Setup Complete
    Ready --> Listening: User Speaks
    
    Listening --> Processing: Audio Chunk Received
    Processing --> Transcribing: Send to Whisper
    Transcribing --> QuestionDetection: Text Received
    
    QuestionDetection --> Listening: Incomplete Question
    QuestionDetection --> GeneratingAnswer: Complete Question
    
    GeneratingAnswer --> DisplayingAnswer: Answer Ready
    DisplayingAnswer --> Listening: Continue Session
    
    Listening --> Paused: Pause Requested
    Paused --> Listening: Resume Requested
    
    Listening --> Ending: End Session
    Paused --> Ending: End Session
    DisplayingAnswer --> Ending: End Session
    
    Ending --> Saving: Save Session Data
    Saving --> Complete: Data Saved
    Complete --> [*]
    
    Processing --> Error: API Error
    Transcribing --> Error: Transcription Failed
    GeneratingAnswer --> Error: Generation Failed
    Error --> Ready: Retry
    Error --> [*]: Cancel
```

---

## 6. Use Case Diagram

```mermaid
graph TB
    User((User))
    Admin((Admin))
    
    subgraph "InterviewMate.ai System"
        UC1[Register Account]
        UC2[Upload Resume]
        UC3[Add STAR Stories]
        UC4[Start Practice Session]
        UC5[Real-time Transcription]
        UC6[Get Answer Suggestions]
        UC7[Review Session History]
        UC8[Export Transcripts]
        UC9[Manage Subscription]
        UC10[View Analytics]
        UC11[Manage Users]
        UC12[Monitor System Health]
    end
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
    
    Admin --> UC11
    Admin --> UC12
    
    UC4 --> UC5
    UC5 --> UC6
```

---

## 7. Data Flow Diagram

```mermaid
graph LR
    subgraph "Input"
        AudioInput[User Audio]
        ResumeFile[Resume File]
        UserInput[User Input]
    end
    
    subgraph "Processing"
        STT[Speech-to-Text]
        QuestionParser[Question Parser]
        ContextBuilder[Context Builder]
        AnswerGen[Answer Generator]
        DataValidator[Data Validator]
    end
    
    subgraph "Storage"
        UserDB[(User Database)]
        SessionDB[(Session Database)]
        FileStorage[(File Storage)]
    end
    
    subgraph "Output"
        Transcription[Live Transcription]
        SuggestedAnswer[Suggested Answer]
        SessionSummary[Session Summary]
    end
    
    AudioInput --> STT
    STT --> QuestionParser
    QuestionParser --> ContextBuilder
    
    ResumeFile --> DataValidator
    UserInput --> DataValidator
    DataValidator --> UserDB
    
    UserDB --> ContextBuilder
    ContextBuilder --> AnswerGen
    AnswerGen --> SuggestedAnswer
    
    STT --> Transcription
    QuestionParser --> SessionDB
    AnswerGen --> SessionDB
    SessionDB --> SessionSummary
    
    ResumeFile --> FileStorage
```

---

## 8. Deployment Diagram

```mermaid
graph TB
    subgraph "Client Devices"
        Desktop[Desktop Browser]
        Mobile[Mobile Browser]
        Tablet[Tablet Browser]
    end
    
    subgraph "CDN / Edge Network"
        Vercel[Vercel Edge Network]
    end
    
    subgraph "Application Servers"
        NextServer[Next.js Server - Vercel]
        APIServer[FastAPI Server - Railway]
    end
    
    subgraph "External APIs"
        WhisperAPI[Whisper API]
        ClaudeAPI[Claude API]
        StripeAPI[Stripe API]
    end
    
    subgraph "Data Services"
        PostgreSQL[(Supabase PostgreSQL)]
        ObjectStorage[Supabase Storage]
        RedisCache[(Redis Cache)]
    end
    
    subgraph "Monitoring"
        Sentry[Sentry Error Tracking]
        PostHog[PostHog Analytics]
    end
    
    Desktop --> Vercel
    Mobile --> Vercel
    Tablet --> Vercel
    
    Vercel --> NextServer
    NextServer --> APIServer
    
    APIServer --> WhisperAPI
    APIServer --> ClaudeAPI
    APIServer --> PostgreSQL
    APIServer --> ObjectStorage
    APIServer --> RedisCache
    
    NextServer --> StripeAPI
    NextServer --> PostHog
    APIServer --> Sentry
```

---

## 9. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USER ||--o{ PROFILE : has
    USER ||--o{ SESSION : creates
    USER ||--o{ SUBSCRIPTION : subscribes
    
    PROFILE ||--o{ STAR_STORY : contains
    PROFILE ||--o{ TALKING_POINT : includes
    PROFILE ||--o| RESUME : has
    
    SESSION ||--o{ QUESTION : includes
    SESSION ||--o{ AUDIO_CHUNK : contains
    
    QUESTION ||--|| ANSWER : generates
    QUESTION ||--o{ USER_RESPONSE : receives
    
    USER {
        uuid id PK
        string email
        string name
        timestamp created_at
        timestamp updated_at
        string subscription_tier
        string auth_provider
    }
    
    PROFILE {
        uuid id PK
        uuid user_id FK
        text resume_text
        jsonb star_stories
        jsonb talking_points
        string[] skills
        timestamp updated_at
    }
    
    SESSION {
        uuid id PK
        uuid user_id FK
        timestamp start_time
        timestamp end_time
        string session_type
        integer question_count
        float duration_seconds
        jsonb metadata
    }
    
    QUESTION {
        uuid id PK
        uuid session_id FK
        text question_text
        timestamp timestamp
        string category
        string difficulty
        string source
    }
    
    ANSWER {
        uuid id PK
        uuid question_id FK
        text answer_text
        text user_response
        float confidence_score
        boolean was_used
        timestamp generated_at
    }
    
    STAR_STORY {
        uuid id PK
        uuid profile_id FK
        string title
        text situation
        text task
        text action
        text result
        string[] tags
    }
    
    SUBSCRIPTION {
        uuid id PK
        uuid user_id FK
        string tier
        timestamp start_date
        timestamp end_date
        boolean is_active
        string stripe_subscription_id
    }
    
    RESUME {
        uuid id PK
        uuid profile_id FK
        string file_url
        string file_name
        text parsed_text
        timestamp uploaded_at
    }
```

---

## 10. Activity Diagram - Complete User Journey

```mermaid
graph TB
    Start([User Opens App]) --> A{Authenticated?}
    A -->|No| B[Show Login Page]
    A -->|Yes| C[Load Dashboard]
    
    B --> D[User Logs In]
    D --> E{First Time?}
    E -->|Yes| F[Show Onboarding]
    E -->|No| C
    
    F --> G[Upload Resume]
    G --> H[Add STAR Stories]
    H --> C
    
    C --> I{User Action}
    I -->|Start Practice| J[Initialize Session]
    I -->|View History| K[Load Past Sessions]
    I -->|Edit Profile| L[Profile Editor]
    
    J --> M[Start Audio Capture]
    M --> N[User Speaks]
    N --> O[Transcribe Audio]
    O --> P{Question Complete?}
    P -->|No| N
    P -->|Yes| Q[Generate Answer]
    
    Q --> R[Display Answer]
    R --> S{Continue?}
    S -->|Yes| N
    S -->|No| T[End Session]
    
    T --> U[Save Session Data]
    U --> V[Show Summary]
    V --> C
    
    K --> W[Display Session List]
    W --> X{View Details?}
    X -->|Yes| Y[Show Transcript]
    X -->|No| C
    
    L --> Z[Update Profile]
    Z --> C
    
    C --> End([User Exits])
```

---

## 11. System Context Diagram

```mermaid
graph TB
    subgraph "External Systems"
        OpenAI[OpenAI APIs]
        Anthropic[Anthropic API]
        Stripe[Stripe Payments]
        EmailService[Email Service]
        OAuth[OAuth Providers]
    end
    
    subgraph "InterviewMate.ai System"
        Frontend[Frontend Application]
        Backend[Backend API]
        Database[(Database)]
    end
    
    User((Job Seeker))
    Admin((Administrator))
    
    User --> Frontend
    Admin --> Frontend
    
    Frontend <--> Backend
    Backend <--> Database
    
    Backend --> OpenAI
    Backend --> Anthropic
    Backend --> EmailService
    Frontend --> Stripe
    Frontend --> OAuth
```

---

## 12. Microphone to Answer Flow Diagram

```mermaid
graph LR
    A[Microphone] --> B[Audio Capture]
    B --> C[Audio Buffer]
    C --> D[WebSocket Stream]
    D --> E[Backend Receiver]
    E --> F[Audio Processing]
    F --> G[Whisper API]
    G --> H[Transcription Text]
    H --> I[Question Detection]
    I --> J{Complete Question?}
    J -->|No| C
    J -->|Yes| K[Context Building]
    K --> L[User Profile]
    L --> M[Claude API]
    M --> N[Answer Generation]
    N --> O[Post-processing]
    O --> P[Frontend Display]
    P --> Q[User Sees Answer]
```

---

## 13. Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        HTTPS[HTTPS/TLS]
        CORS[CORS Policy]
        RateLimit[Rate Limiting]
        Auth[JWT Authentication]
        RBAC[Role-Based Access Control]
        Encryption[Data Encryption at Rest]
        InputVal[Input Validation]
        XSS[XSS Protection]
    end
    
    subgraph "Application"
        Frontend[Frontend]
        API[Backend API]
        DB[(Database)]
    end
    
    User((User)) --> HTTPS
    HTTPS --> CORS
    CORS --> RateLimit
    RateLimit --> Frontend
    
    Frontend --> Auth
    Auth --> RBAC
    RBAC --> API
    
    API --> InputVal
    InputVal --> XSS
    XSS --> DB
    DB --> Encryption
```

---

## Document Metadata

**Created:** December 10, 2024
**Version:** 1.0
**Author:** Heejin Jo
**Status:** Approved for Development
**Next Review:** Post-MVP Launch

---

## Notes

1. All diagrams use Mermaid syntax for easy rendering in Markdown viewers
2. Diagrams can be updated as system evolves
3. High-level diagrams focus on core functionality (MVP scope)
4. Detailed diagrams can be expanded in Phase 2 and beyond
5. Security architecture prioritizes user data protection and API key safety
