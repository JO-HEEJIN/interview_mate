import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center py-16 px-8 bg-white dark:bg-black">
        <div className="flex flex-col items-center gap-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-black dark:text-zinc-50">
            InterviewMate
          </h1>
          <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
            Real-time AI interview assistant. Get instant answer suggestions
            based on your experience during live video interviews.
          </p>

          <div className="w-full max-w-2xl rounded-lg border-2 border-blue-500 bg-blue-50 p-6 dark:bg-blue-950 dark:border-blue-400">
            <h2 className="text-xl font-bold text-blue-900 dark:text-blue-100 mb-3">
              NOT a Practice Platform - Works During REAL Interviews
            </h2>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              Unlike practice platforms, InterviewMate assists you DURING actual live video calls with recruiters on Zoom, Teams, or Google Meet.
              Get AI-powered answer suggestions in real-time (2 seconds) while you are interviewing.
            </p>
            <p className="text-xs text-blue-700 dark:text-blue-300 mt-2">
              Use it right now in your next interview with Google, Amazon, Microsoft recruiters.
            </p>
          </div>

          <div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
            <Link
              href="/interview"
              className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-zinc-900 px-8 text-white transition-colors hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 sm:w-auto"
            >
              Start Interview
            </Link>
            <Link
              href="/profile/qa-pairs"
              className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-zinc-300 px-8 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900 sm:w-auto"
            >
              Manage Q&A Pairs
            </Link>
          </div>

          <div className="mt-8 grid gap-4 text-left sm:grid-cols-3">
            <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                1. Upload Your Context
              </h3>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                Upload resume, company info, and job posting
              </p>
            </div>
            <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                2. AI Generates Q&A
              </h3>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                AI creates 30+ personalized interview Q&A pairs
              </p>
            </div>
            <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                3. Use During Real Interviews
              </h3>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                Get real-time AI suggestions during your video interviews
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
