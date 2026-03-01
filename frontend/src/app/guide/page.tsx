import Link from 'next/link';
import Image from 'next/image';

export default function GuidePage() {
  const steps = [
    {
      number: 1,
      title: 'Settings',
      description:
        'Configure your interview profile and preferences — language, role, and how you want AI answers formatted.',
      href: '/profile/interview-settings',
      linkText: 'Go to Settings',
    },
    {
      number: 2,
      title: 'AI Generate',
      description:
        'Upload your context (resume, research papers, notes) and let AI auto-generate Q&A pairs tailored to your background.',
      href: '/profile/context-upload',
      linkText: 'Go to AI Generate',
    },
    {
      number: 3,
      title: 'Q&A Pairs',
      description:
        'Review and refine the generated pairs so the AI gives precise, personalized answers during your interviews.',
      href: '/profile/qa-pairs',
      linkText: 'Go to Q&A Pairs',
    },
  ];

  return (
    <div className="scroll-smooth bg-white dark:bg-black">
      {/* Hero */}
      <section className="flex flex-col items-center justify-center px-6 py-20">
        <div className="w-full max-w-4xl text-center">
          <h1 className="text-4xl font-bold tracking-tight text-black dark:text-zinc-50 sm:text-5xl">
            How to Get 100% Out of InterviewMate
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-zinc-600 dark:text-zinc-400">
            Follow these three steps to set up your account, then jump into any
            live interview with full AI support.
          </p>
        </div>
      </section>

      {/* 3-Step Setup */}
      <section className="px-6 pb-16">
        <div className="mx-auto grid max-w-4xl gap-6 sm:grid-cols-3">
          {steps.map((step) => (
            <div
              key={step.number}
              className="rounded-xl border border-zinc-200 bg-zinc-50 p-6 dark:border-zinc-800 dark:bg-zinc-950"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-zinc-900 text-lg font-bold text-white dark:bg-zinc-100 dark:text-zinc-900">
                {step.number}
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
                {step.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                {step.description}
              </p>
              <Link
                href={step.href}
                className="mt-4 inline-block text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
              >
                {step.linkText} &rarr;
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Audio Capture Warning */}
      <section className="px-6 pb-16">
        <div className="mx-auto max-w-4xl rounded-xl border-2 border-amber-400 bg-amber-50 p-6 dark:border-amber-500 dark:bg-amber-950/40">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 text-2xl leading-none">&#9888;&#65039;</span>
            <div>
              <h3 className="text-lg font-semibold text-amber-900 dark:text-amber-200">
                Important: Enable Audio Capture Before Your Call
              </h3>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-amber-800 dark:text-amber-300">
                <li>
                  Before joining Zoom, Google Meet, or Teams, open the{' '}
                  <Link href="/interview" className="font-medium underline">
                    Interview page
                  </Link>{' '}
                  first and make sure <strong>&ldquo;Capture system audio&rdquo;</strong> is
                  toggled ON.
                </li>
                <li>
                  You must enable all audio capture toggles <strong>before</strong> entering the
                  video call — if you do it after, the browser may not pick up system audio.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Ready Callout */}
      <section className="px-6 pb-20">
        <div className="mx-auto max-w-4xl rounded-xl bg-zinc-900 p-8 text-center dark:bg-zinc-100">
          <h2 className="text-2xl font-bold text-white dark:text-zinc-900">
            Then you&apos;re ready!
          </h2>
          <p className="mt-2 text-zinc-300 dark:text-zinc-600">
            Start your interview and get real-time AI answers as questions come in.
          </p>
          <Link
            href="/interview"
            className="mt-6 inline-flex items-center justify-center rounded-full bg-white px-8 py-3 text-sm font-semibold text-zinc-900 transition-colors hover:bg-zinc-200 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
          >
            Go to Interview
          </Link>
        </div>
      </section>

      {/* Real-World Example */}
      <section className="bg-zinc-50 px-6 py-20 dark:bg-zinc-950">
        <div className="mx-auto max-w-4xl">
          <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100 text-center">
            See It In Action: Car Wash Research Paper
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-center text-zinc-600 dark:text-zinc-400">
            We uploaded context from a real research paper about car wash systems,
            and the AI answered domain-specific questions perfectly — proving that
            InterviewMate works for any topic when you provide the right context.
          </p>

          <div className="mt-10 overflow-hidden rounded-xl border border-zinc-200 dark:border-zinc-800">
            <Image
              src="/guide-carwash-demo.png"
              alt="Car wash research paper demo — AI answering domain-specific questions"
              width={1200}
              height={800}
              className="w-full"
            />
          </div>

          <div className="mt-8 text-center">
            <a
              href="https://github.com/JO-HEEJIN/interview_mate/tree/main/car_wash"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
            >
              View the full car wash example on GitHub
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
