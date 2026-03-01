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

      {/* Settings Prompt Templates */}
      <section className="px-6 pb-20">
        <div className="mx-auto max-w-4xl">
          {/* Testing Warning */}
          <div className="mb-10 rounded-xl border-2 border-amber-400 bg-amber-50 p-6 dark:border-amber-500 dark:bg-amber-950/40">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 text-2xl leading-none">&#9888;&#65039;</span>
              <div>
                <h3 className="text-lg font-semibold text-amber-900 dark:text-amber-200">
                  Always Test Before Your Real Interview
                </h3>
                <p className="mt-2 text-sm text-amber-800 dark:text-amber-300">
                  If your system prompt gets too long, the AI&apos;s answer quality can actually
                  get <strong>worse</strong> — not better. After filling in your Background Summary
                  and Custom Instructions, run a few practice questions on the{' '}
                  <Link href="/interview" className="font-medium underline">
                    Interview page
                  </Link>{' '}
                  to make sure the answers are accurate and relevant before your real interview.
                </p>
              </div>
            </div>
          </div>

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
            <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                Prompt Template
              </h3>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                Copy &rarr; fill in blanks &rarr; send to any AI with your resume
              </span>
            </div>

            <div className="p-6">
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-700 dark:text-zinc-300 font-mono">
{`I'm using InterviewMate — a real-time interview assistant. It has a "Background Summary" field where I describe my key achievements, projects, and experiences. The AI references this during live interviews to generate personalized answers.

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
[comma-separated list]`}
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

      {/* Custom Instruction Helper */}
      <section className="px-6 pb-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100 text-center">
            Need Help Writing Your Custom Instructions?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-center text-zinc-600 dark:text-zinc-400">
            The <strong>Custom Instructions</strong> field in{' '}
            <Link href="/profile/interview-settings" className="text-blue-600 underline dark:text-blue-400">
              Settings
            </Link>{' '}
            controls how the AI generates answers during your interview. Copy the prompt
            below, fill in the blanks, and paste it into your favorite AI (ChatGPT, Claude,
            Gemini, etc.) along with your resume and the job/program description. Then paste
            the result straight into InterviewMate.
          </p>

          <div className="mt-8 rounded-xl border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
            {/* Prompt header */}
            <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                Prompt Template
              </h3>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                Copy &rarr; fill in blanks &rarr; send to any AI with your resume
              </span>
            </div>

            {/* Prompt body */}
            <div className="p-6">
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-700 dark:text-zinc-300 font-mono">
{`I'm using InterviewMate — a real-time interview assistant that listens to interviewer questions and generates answers live. It has a "Custom Instructions" field that gets appended to the AI system prompt under "# YOUR SPECIFIC INTERVIEW CONTEXT & STYLE".

Write Custom Instructions for my profile. Here's my info:

- Name: [Your name]
- Position I'm applying for: [e.g., Software Engineer, PhD Candidate, MBA Applicant]
- Target company/school: [e.g., Google, MIT, US Embassy]
- Interview type: [Job interview / PhD defense / Visa interview / School admission]
- Interview language: [e.g., English, Korean, etc.]
- Key things I want to emphasize: [e.g., leadership experience, specific project, research outcomes]
- Preferred answer tone: [e.g., confident, humble, fact-driven, conversational]

Also attached:
- My resume/CV
- The job posting / program description / any relevant context

Based on all of this, generate a Custom Instructions block I can paste directly into InterviewMate's Settings. It should include:
1. Use STAR format (Situation → Task → Action → Result) for structuring answers — this is critical for InterviewMate's AI
2. Answer style rules (tone, length, structure)
3. Domain-specific context (industry jargon, frameworks, methodologies to reference)
4. Personal branding notes (strengths, achievements, stories to weave in)
5. Cultural or format considerations (e.g., brief answers for visa interviews, technical depth for PhD defense)
6. Any "always do / never do" rules

Output ONLY the Custom Instructions text — no explanations, no markdown headers. Just the raw text I can paste in.`}
              </pre>
            </div>
          </div>

          {/* Step-by-step instructions */}
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                1
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Copy the prompt</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Fill in the bracketed fields with your real information.
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                2
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Send to any AI</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Paste it into ChatGPT, Claude, Gemini, etc. — attach your resume and the job description too.
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                3
              </div>
              <h4 className="font-medium text-zinc-900 dark:text-zinc-100">Paste the result</h4>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                Copy the AI&apos;s output and paste it into the Custom Instructions field in{' '}
                <Link href="/profile/interview-settings" className="text-blue-600 underline dark:text-blue-400">
                  Settings
                </Link>.
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
