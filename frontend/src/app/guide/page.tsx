import Link from 'next/link';
import Image from 'next/image';
import { CopyButton } from '@/components/CopyButton';

// Kept in sync with backend/app/api/interview_profile.py:DEFAULT_STAR_PROMPT.
// If you edit one, edit the other.
const STAR_CUSTOM_INSTRUCTIONS = `You are an expert advisor helping people make practical decisions. Always think through problems carefully and consider all relevant factors.
When answering any question, use the STAR method:
- Situation: What is the actual situation being described?
- Task: What needs to be accomplished?
- Action: What action achieves the task given the situation?
- Result: What outcome does this action produce?

Provide clear, actionable recommendations.`;

const BACKGROUND_PROMPT_TEMPLATE = `I'm using InterviewMate — a real-time interview assistant. It has a "Background Summary" field where I describe my key achievements, projects, and experiences. The AI references this during live interviews to generate personalized answers.

Write a Background Summary for my profile. Here's my info:

- Name: [Your name]
- Position I'm applying for: [e.g., Software Engineer, PhD Candidate, MBA Applicant]
- Target company/school: [e.g., Google, MIT, US Embassy]
- Years of experience: [e.g., 3 years, fresh graduate]

Also attached:
- My resume/CV
- The job posting / program description (if available)

Based on all of this, generate a Background Summary I can paste directly into InterviewMate's Settings. It should:
1. Use STAR format (Situation → Task → Action → Result) for each achievement
2. List key achievements with specific metrics (e.g., "Built system serving 100K+ daily users")
3. Highlight 3-5 most relevant projects or experiences for the target role
4. Include technical details the AI can reference when answering domain-specific questions
5. Keep each bullet point concise (1-2 sentences max)
6. Focus on what makes me stand out for this specific role

Also suggest:
- Skills & Expertise (comma-separated list for the "Skills & Expertise" field)
- Key Strengths (comma-separated list for the "Key Strengths" field)

Output format:
BACKGROUND SUMMARY:
[the summary text]

SKILLS & EXPERTISE:
[comma-separated list]

KEY STRENGTHS:
[comma-separated list]`;

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

      {/* How InterviewMate Works (moved from landing — too much on first view) */}
      <section className="px-6 pb-16">
        <div className="mx-auto w-full max-w-5xl">
          <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100 mb-3 text-center">
            How InterviewMate Works
          </h2>
          <p className="text-base text-zinc-600 dark:text-zinc-400 mb-10 text-center max-w-2xl mx-auto">
            Three simple steps to ace your next interview
          </p>
          <div className="grid gap-6 text-left md:grid-cols-3">
            <div className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-zinc-900 text-xl font-bold text-white dark:bg-zinc-100 dark:text-zinc-900">
                1
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                Upload Your Context
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Upload your resume, target company info, and job description.
                Our AI learns your background and experience.
              </p>
            </div>
            <div className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-zinc-900 text-xl font-bold text-white dark:bg-zinc-100 dark:text-zinc-900">
                2
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                AI Generates Q&amp;A Pairs
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Claude AI creates 30+ personalized interview Q&amp;A pairs
                tailored to your experience and the target role.
              </p>
            </div>
            <div className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-zinc-900 text-xl font-bold text-white dark:bg-zinc-100 dark:text-zinc-900">
                3
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                Use During Real Interviews
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Deepgram transcribes questions in real-time. Claude AI
                generates personalized answers in under 2 seconds.
              </p>
            </div>
          </div>
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

      {/* Settings Prompt Templates */}
      <section className="px-6 pb-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100 text-center">
            Need Help Writing Your Background Summary?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-center text-zinc-600 dark:text-zinc-400">
            The <strong>Background Summary</strong> field in{' '}
            <Link href="/profile/interview-settings" className="text-blue-600 underline dark:text-blue-400">
              Settings
            </Link>{' '}
            tells the AI about your achievements, projects, and experiences. Use the
            prompt below with any AI to generate a well-structured summary from your resume.
          </p>

          <div className="mt-8 rounded-xl border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
              <div className="flex flex-col">
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                  Prompt Template
                </h3>
                <span className="text-xs text-zinc-500 dark:text-zinc-400">
                  Copy &rarr; fill in blanks &rarr; send to any AI with your resume
                </span>
              </div>
              <CopyButton text={BACKGROUND_PROMPT_TEMPLATE} label="Copy prompt" />
            </div>

            <div className="p-6">
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-700 dark:text-zinc-300 font-mono">
{BACKGROUND_PROMPT_TEMPLATE}
              </pre>
            </div>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-green-100 text-sm font-bold text-green-700 dark:bg-green-900 dark:text-green-300">
                1
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Copy the prompt</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Fill in the bracketed fields with your real information.
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-green-100 text-sm font-bold text-green-700 dark:bg-green-900 dark:text-green-300">
                2
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Send to any AI</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Paste it into ChatGPT, Claude, Gemini, etc. — attach your resume too.
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-green-100 text-sm font-bold text-green-700 dark:bg-green-900 dark:text-green-300">
                3
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Paste each section</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Copy each part into the matching field in{' '}
                <Link href="/profile/interview-settings" className="text-blue-600 underline dark:text-blue-400">
                  Settings
                </Link>{' '}
                — Background Summary, Skills &amp; Expertise, and Key Strengths.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Custom Instruction STAR Template */}
      <section className="px-6 pb-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100 text-center">
            Your Default Custom Instructions: STAR Template
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-center text-zinc-600 dark:text-zinc-400">
            Every new profile ships with this STAR-based prompt already in the{' '}
            <Link href="/profile/interview-settings" className="text-blue-600 underline dark:text-blue-400">
              Custom Instructions
            </Link>{' '}
            field. It forces the AI to structure every answer through Situation → Task → Action → Result —
            the single biggest lever for interview-grade responses. Try it as-is, then tune.
          </p>

          <div className="mt-8 rounded-xl border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
              <div className="flex flex-col">
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                  STAR Custom Instructions (default)
                </h3>
                <span className="text-xs text-zinc-500 dark:text-zinc-400">
                  Paste into Custom Instructions if your profile is older than this update
                </span>
              </div>
              <CopyButton text={STAR_CUSTOM_INSTRUCTIONS} label="Copy template" />
            </div>

            <div className="p-6">
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-700 dark:text-zinc-300 font-mono">
{STAR_CUSTOM_INSTRUCTIONS}
              </pre>
            </div>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                1
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Already in new profiles</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Brand-new profiles created from now on ship with this prompt pre-filled. Profiles created
                before this update — paste it in via the Copy button above.
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                2
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Tweak or replace</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Add company framing, tone, or domain hints once you see what the AI produces. Keep the
                STAR scaffold as the spine — that&apos;s what does the heavy lifting.
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                3
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Test on a few questions</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Run practice questions on the{' '}
                <Link href="/interview" className="text-blue-600 underline dark:text-blue-400">
                  Interview page
                </Link>{' '}
                to confirm STAR structure is showing up in the answers — then go live.
              </p>
            </div>
          </div>
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

      {/* Ready Callout */}
      <section className="px-6 py-20">
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
    </div>
  );
}
