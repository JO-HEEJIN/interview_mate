import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center py-16 px-8 bg-white dark:bg-black">
        <div className="flex flex-col items-center gap-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-black dark:text-zinc-50">
            InterviewMate.ai
          </h1>
          <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
            Real-time AI interview assistant. Get instant answer suggestions
            based on your experience while practicing for interviews.
          </p>

          <div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
            <Link
              href="/interview"
              className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-zinc-900 px-8 text-white transition-colors hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 sm:w-auto"
            >
              Start Interview
            </Link>
            <Link
              href="/profile/stories"
              className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-zinc-300 px-8 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900 sm:w-auto"
            >
              Manage STAR Stories
            </Link>
          </div>

          <div className="mt-8 grid gap-4 text-left sm:grid-cols-3">
            <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                1. Add Your Stories
              </h3>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                Enter your STAR stories and experience highlights
              </p>
            </div>
            <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                2. Start Recording
              </h3>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                Record interview questions in real-time
              </p>
            </div>
            <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                3. Get Suggestions
              </h3>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                AI generates personalized answer suggestions
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
