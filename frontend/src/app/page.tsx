import Link from "next/link";

export default function Home() {
  return (
    <div className="scroll-smooth bg-white dark:bg-black">
      {/* Hero Section */}
      <section className="flex min-h-screen flex-col items-center justify-center px-6 py-20">
        <div className="flex max-w-4xl flex-col items-center gap-8 text-center">
          <h1 className="text-5xl font-bold tracking-tight text-black dark:text-zinc-50 sm:text-6xl">
            InterviewMate
          </h1>
          <p className="max-w-2xl text-xl leading-8 text-zinc-600 dark:text-zinc-400">
            Real-time cheating for any interview. Job interviews, PhD defenses, visa interviews,
            school admissions - get AI-powered answers in under 2 seconds while you&apos;re being interviewed.
          </p>

          {/* Launch Discount Banner */}
          <div className="w-full max-w-2xl rounded-xl border-2 border-green-500 bg-green-50 p-5 dark:bg-green-950 dark:border-green-400">
            <p className="text-base font-semibold text-green-800 dark:text-green-200">
              Launch Special: Use code LAUNCH50 for 50% off all plans. Valid until January 30, 2026.
            </p>
          </div>

          {/* Main Value Proposition */}
          <div className="w-full max-w-2xl rounded-xl border-2 border-blue-500 bg-blue-50 p-8 dark:bg-blue-950 dark:border-blue-400">
            <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-100 mb-4">
              Works During REAL Interviews - Not a Practice Platform
            </h2>
            <p className="text-base text-blue-800 dark:text-blue-200">
              Unlike interview practice platforms, InterviewMate assists you DURING actual live interviews.
              Whether it&apos;s a job interview, PhD defense, visa interview, or school admission -
              get AI-powered answer suggestions in under 2 seconds.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col gap-4 text-base font-medium sm:flex-row mt-4">
            <Link
              href="/interview"
              className="flex h-14 w-full items-center justify-center gap-2 rounded-full bg-zinc-900 px-10 text-lg text-white transition-colors hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 sm:w-auto"
            >
              Start Interview
            </Link>
            <Link
              href="/pricing"
              className="flex h-14 w-full items-center justify-center rounded-full border-2 border-solid border-zinc-300 px-10 text-lg transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900 sm:w-auto"
            >
              View Pricing
            </Link>
          </div>

          {/* Scroll Indicator */}
          <div className="mt-12 animate-bounce">
            <svg className="h-8 w-8 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 px-6 py-20 dark:bg-zinc-950">
        <div className="w-full max-w-5xl">
          <h2 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-4 text-center">
            How InterviewMate Works
          </h2>
          <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-16 text-center max-w-2xl mx-auto">
            Three simple steps to ace your next interview
          </p>
          <div className="grid gap-8 text-left md:grid-cols-3">
            <div className="rounded-2xl border border-zinc-200 bg-white p-8 dark:border-zinc-800 dark:bg-zinc-900 shadow-sm">
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-zinc-900 text-2xl font-bold text-white dark:bg-zinc-100 dark:text-zinc-900">
                1
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                Upload Your Context
              </h3>
              <p className="text-base text-zinc-600 dark:text-zinc-400">
                Upload your resume, target company info, and job description.
                Our AI learns your background and experience.
              </p>
            </div>
            <div className="rounded-2xl border border-zinc-200 bg-white p-8 dark:border-zinc-800 dark:bg-zinc-900 shadow-sm">
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-zinc-900 text-2xl font-bold text-white dark:bg-zinc-100 dark:text-zinc-900">
                2
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                AI Generates Q&A Pairs
              </h3>
              <p className="text-base text-zinc-600 dark:text-zinc-400">
                Claude AI creates 30+ personalized interview Q&A pairs
                tailored to your experience and the target role.
              </p>
            </div>
            <div className="rounded-2xl border border-zinc-200 bg-white p-8 dark:border-zinc-800 dark:bg-zinc-900 shadow-sm">
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-zinc-900 text-2xl font-bold text-white dark:bg-zinc-100 dark:text-zinc-900">
                3
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                Use During Real Interviews
              </h3>
              <p className="text-base text-zinc-600 dark:text-zinc-400">
                Deepgram transcribes questions in real-time. Claude AI
                generates personalized answers in under 2 seconds.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack Section */}
      <section className="flex min-h-screen flex-col items-center justify-center px-6 py-20">
        <div className="w-full max-w-5xl">
          <h2 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-4 text-center">
            Powered by Leading AI Technology
          </h2>
          <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-16 text-center max-w-2xl mx-auto">
            Industry-leading speech recognition and AI for accurate, instant responses
          </p>
          <div className="grid gap-8 text-left md:grid-cols-2">
            <div className="rounded-2xl border border-zinc-200 p-10 dark:border-zinc-800 shadow-sm">
              <div className="mb-6 h-16 w-16 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
                Deepgram Speech Recognition
              </h3>
              <p className="text-base text-zinc-600 dark:text-zinc-400 leading-relaxed">
                Ultra-fast, highly accurate speech-to-text transcription.
                Captures interviewer questions in real-time with minimal latency.
                Industry-leading accuracy for clear understanding.
              </p>
            </div>
            <div className="rounded-2xl border border-zinc-200 p-10 dark:border-zinc-800 shadow-sm">
              <div className="mb-6 h-16 w-16 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
                <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
                Claude AI Answer Generation
              </h3>
              <p className="text-base text-zinc-600 dark:text-zinc-400 leading-relaxed">
                Anthropic&apos;s Claude AI generates contextually accurate,
                personalized answers based on your resume and experience.
                Smart, relevant responses tailored to each question.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 px-6 py-20 dark:bg-zinc-950">
        <div className="w-full max-w-5xl">
          <h2 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-4 text-center">
            Works For Any Interview
          </h2>
          <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-16 text-center max-w-2xl mx-auto">
            Job interviews, academic defenses, visa interviews, admissions - we&apos;ve got you covered
          </p>
          <div className="grid gap-6 text-left sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl bg-white p-8 dark:bg-zinc-900 shadow-sm border border-zinc-200 dark:border-zinc-800">
              <div className="mb-4 h-12 w-12 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                <svg className="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">Job Interviews</h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">Tech, consulting, finance, and more</p>
            </div>
            <div className="rounded-2xl bg-white p-8 dark:bg-zinc-900 shadow-sm border border-zinc-200 dark:border-zinc-800">
              <div className="mb-4 h-12 w-12 rounded-lg bg-green-100 dark:bg-green-900 flex items-center justify-center">
                <svg className="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 7l9-5-9-5-9 5 9 5z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">PhD & Academic</h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">Thesis defense, committee meetings</p>
            </div>
            <div className="rounded-2xl bg-white p-8 dark:bg-zinc-900 shadow-sm border border-zinc-200 dark:border-zinc-800">
              <div className="mb-4 h-12 w-12 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                <svg className="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">Visa & Immigration</h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">Embassy interviews, immigration cases</p>
            </div>
            <div className="rounded-2xl bg-white p-8 dark:bg-zinc-900 shadow-sm border border-zinc-200 dark:border-zinc-800">
              <div className="mb-4 h-12 w-12 rounded-lg bg-orange-100 dark:bg-orange-900 flex items-center justify-center">
                <svg className="h-6 w-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">School Admissions</h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">MBA, graduate, undergraduate</p>
            </div>
          </div>

          {/* Platform Compatibility */}
          <div className="mt-20 text-center">
            <h3 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-6">
              Works With All Major Video Platforms
            </h3>
            <div className="flex flex-wrap justify-center gap-6 text-lg text-zinc-600 dark:text-zinc-400">
              <span className="px-4 py-2 rounded-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">Zoom</span>
              <span className="px-4 py-2 rounded-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">Google Meet</span>
              <span className="px-4 py-2 rounded-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">Microsoft Teams</span>
              <span className="px-4 py-2 rounded-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">Webex</span>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing CTA Section */}
      <section className="flex min-h-screen flex-col items-center justify-center px-6 py-20">
        <div className="w-full max-w-3xl text-center">
          <div className="mb-8">
            <span className="inline-block px-4 py-2 rounded-full bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-sm font-semibold mb-6">
              Most Affordable on the Market
            </span>
          </div>
          <h2 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-6 sm:text-5xl">
            Start at Just $0.20 per Session
          </h2>
          <p className="text-xl text-zinc-600 dark:text-zinc-400 mb-8 max-w-2xl mx-auto">
            10 sessions for just $2 with LAUNCH50 discount (regular $4).
            Works for any interview type. No subscription. Pay as you go.
          </p>

          <div className="rounded-2xl border-2 border-zinc-200 bg-zinc-50 p-10 dark:border-zinc-700 dark:bg-zinc-900 mb-10">
            <div className="text-6xl font-bold text-zinc-900 dark:text-zinc-100 mb-2">
              $2
              <span className="text-2xl font-normal text-zinc-500 dark:text-zinc-400"> / 10 sessions</span>
            </div>
            <p className="text-zinc-500 dark:text-zinc-400 mb-6">
              <span className="line-through">$4</span> with code LAUNCH50
            </p>
            <ul className="text-left max-w-md mx-auto space-y-3 mb-8">
              <li className="flex items-center gap-3 text-zinc-700 dark:text-zinc-300">
                <svg className="h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Real-time speech transcription
              </li>
              <li className="flex items-center gap-3 text-zinc-700 dark:text-zinc-300">
                <svg className="h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                AI-powered answer suggestions
              </li>
              <li className="flex items-center gap-3 text-zinc-700 dark:text-zinc-300">
                <svg className="h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Works on all video platforms
              </li>
              <li className="flex items-center gap-3 text-zinc-700 dark:text-zinc-300">
                <svg className="h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Under 2-second response time
              </li>
            </ul>
          </div>

          <div className="flex flex-col gap-4 justify-center sm:flex-row">
            <Link
              href="/interview"
              className="flex h-14 items-center justify-center rounded-full bg-zinc-900 px-10 text-lg font-medium text-white transition-colors hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
            >
              Start Interview Now
            </Link>
            <Link
              href="/pricing"
              className="flex h-14 items-center justify-center rounded-full border-2 border-zinc-300 px-10 text-lg font-medium transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
            >
              View All Plans
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
