import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-center py-16 px-8 bg-white dark:bg-black">
        <div className="flex flex-col items-center gap-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-black dark:text-zinc-50">
            InterviewMate
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-zinc-600 dark:text-zinc-400">
            Real-time AI interview assistant powered by Claude AI and Deepgram.
            Get instant, personalized answer suggestions during live video interviews
            on Zoom, Google Meet, and Microsoft Teams.
          </p>

          {/* Launch Discount Banner */}
          <div className="w-full max-w-2xl rounded-lg border-2 border-green-500 bg-green-50 p-4 dark:bg-green-950 dark:border-green-400">
            <p className="text-sm font-semibold text-green-800 dark:text-green-200">
              Launch Special: Use code LAUNCH50 for 50% off all plans. Valid until January 30, 2026.
            </p>
          </div>

          {/* Main Value Proposition */}
          <div className="w-full max-w-2xl rounded-lg border-2 border-blue-500 bg-blue-50 p-6 dark:bg-blue-950 dark:border-blue-400">
            <h2 className="text-xl font-bold text-blue-900 dark:text-blue-100 mb-3">
              Works During REAL Interviews - Not a Practice Platform
            </h2>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              Unlike interview practice platforms, InterviewMate assists you DURING actual live video calls
              with recruiters at Google, Amazon, Microsoft, Meta, and other companies.
              Get AI-powered answer suggestions in under 2 seconds while you are interviewing.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
            <Link
              href="/interview"
              className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-zinc-900 px-8 text-white transition-colors hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 sm:w-auto"
            >
              Start Interview
            </Link>
            <Link
              href="/pricing"
              className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-zinc-300 px-8 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900 sm:w-auto"
            >
              View Pricing
            </Link>
          </div>

          {/* How It Works */}
          <div className="mt-8 w-full">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-6">
              How InterviewMate Works
            </h2>
            <div className="grid gap-4 text-left sm:grid-cols-3">
              <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                  1. Upload Your Context
                </h3>
                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                  Upload your resume, target company info, and job description.
                  Our AI learns your background and experience.
                </p>
              </div>
              <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                  2. AI Generates Q&A Pairs
                </h3>
                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                  Claude AI creates 30+ personalized interview Q&A pairs
                  tailored to your experience and the target role.
                </p>
              </div>
              <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                  3. Use During Real Interviews
                </h3>
                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                  Deepgram transcribes questions in real-time. Claude AI
                  generates personalized answers in under 2 seconds.
                </p>
              </div>
            </div>
          </div>

          {/* Technology Stack */}
          <div className="mt-8 w-full">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-6">
              Powered by Leading AI Technology
            </h2>
            <div className="grid gap-4 text-left sm:grid-cols-2">
              <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                  Deepgram Speech Recognition
                </h3>
                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                  Ultra-fast, highly accurate speech-to-text transcription.
                  Captures interviewer questions in real-time with minimal latency.
                </p>
              </div>
              <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                  Claude AI Answer Generation
                </h3>
                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                  Anthropic&apos;s Claude AI generates contextually accurate,
                  personalized answers based on your resume and experience.
                </p>
              </div>
            </div>
          </div>

          {/* Use Cases */}
          <div className="mt-8 w-full">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-6">
              Perfect For All Interview Types
            </h2>
            <div className="grid gap-3 text-left sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-lg bg-zinc-100 p-3 dark:bg-zinc-900">
                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Behavioral Interviews</p>
                <p className="text-xs text-zinc-600 dark:text-zinc-400">STAR method answers</p>
              </div>
              <div className="rounded-lg bg-zinc-100 p-3 dark:bg-zinc-900">
                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Technical Interviews</p>
                <p className="text-xs text-zinc-600 dark:text-zinc-400">System design discussions</p>
              </div>
              <div className="rounded-lg bg-zinc-100 p-3 dark:bg-zinc-900">
                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">HR Interviews</p>
                <p className="text-xs text-zinc-600 dark:text-zinc-400">Culture fit questions</p>
              </div>
              <div className="rounded-lg bg-zinc-100 p-3 dark:bg-zinc-900">
                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Case Interviews</p>
                <p className="text-xs text-zinc-600 dark:text-zinc-400">Consulting frameworks</p>
              </div>
            </div>
          </div>

          {/* Platform Compatibility */}
          <div className="mt-8 w-full">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">
              Works With All Major Video Platforms
            </h2>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Zoom, Google Meet, Microsoft Teams, Webex, and any browser-based video call platform.
            </p>
          </div>

          {/* Pricing CTA */}
          <div className="mt-8 w-full max-w-2xl rounded-lg border border-zinc-200 p-6 dark:border-zinc-800">
            <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-2">
              Start at Just $2 with LAUNCH50
            </h2>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
              10 interview sessions for $4 (or $2 with launch discount).
              No subscription required. Pay as you go.
            </p>
            <Link
              href="/pricing"
              className="inline-flex h-10 items-center justify-center rounded-full bg-zinc-900 px-6 text-sm font-medium text-white transition-colors hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
            >
              View All Plans
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
