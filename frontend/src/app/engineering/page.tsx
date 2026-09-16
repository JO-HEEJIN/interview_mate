import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Engineering Case Study | InterviewMate',
  description:
    'How InterviewMate built a low-latency speech, retrieval, caching, and model-routing pipeline for high-pressure communication.',
  alternates: {
    canonical: '/engineering',
  },
};

const pipeline = [
  {
    step: '01',
    title: 'Capture',
    detail: 'The browser captures short WebM/Opus chunks from the microphone or system audio.',
    tech: 'MediaRecorder · 16 kHz mono',
  },
  {
    step: '02',
    title: 'Transcribe',
    detail: 'An async FastAPI service converts chunks to linear PCM and streams them to Deepgram.',
    tech: 'FFmpeg · WebSocket · Deepgram Flux',
  },
  {
    step: '03',
    title: 'Detect',
    detail: 'Fast lexical checks identify likely question boundaries before invoking slower reasoning.',
    tech: 'Heuristics · end-of-turn signals',
  },
  {
    step: '04',
    title: 'Retrieve',
    detail: 'Search is constrained to the user’s own prepared Q&A pairs and relevant profile context.',
    tech: 'Qdrant · text-embedding-3-small',
  },
  {
    step: '05',
    title: 'Respond',
    detail: 'A cached answer or streamed model response is sent back over the persistent socket.',
    tech: 'In-memory cache · GLM → Claude fallback',
  },
];

const latencyRows = [
  ['Audio chunking', '~100 ms', 'Client-side chunk interval'],
  ['Transcription', '300–500 ms', 'Documented Deepgram Flux path'],
  ['First token', '400–600 ms', 'With prompt caching; provider and network vary'],
  ['Complete answer', '~2.4 s', 'Documented end-to-end example, not a universal SLO'],
];

const incidentRows = [
  {
    issue: 'Thread bridge created 5-second stalls',
    change: 'Moved audio forwarding to a fully async subprocess and direct await.',
    lesson: 'Keep the hot path on one async event loop; avoid blocking waits around streaming I/O.',
  },
  {
    issue: 'Long questions could hang during decomposition',
    change: 'Added a 10-second decomposition timeout, heuristic splitting, and 5-second search timeouts.',
    lesson: 'A useful partial result is better than an unbounded wait in a live interaction.',
  },
  {
    issue: 'RAG was silently bypassed',
    change: 'Replaced an unconfigured global service with lazy Supabase-aware service construction.',
    lesson: 'Dependency wiring is part of retrieval correctness, not just application plumbing.',
  },
  {
    issue: 'Early Deepgram streaming was timeout-prone',
    change: 'Moved to Flux-style end-of-turn detection with eager thresholds and explicit cleanup.',
    lesson: 'Turn detection and resource cleanup deserve first-class reliability tests.',
  },
];

export default function EngineeringPage() {
  return (
    <main className="bg-white text-zinc-900 dark:bg-black dark:text-zinc-100">
      <section className="border-b border-zinc-200 px-6 py-24 dark:border-zinc-800">
        <div className="mx-auto max-w-5xl">
          <Link
            href="/"
            className="text-sm font-semibold text-blue-600 hover:text-blue-500 dark:text-blue-400"
          >
            ← Back to InterviewMate
          </Link>
          <div className="mt-10 max-w-4xl">
            <p className="text-sm font-bold uppercase tracking-[0.24em] text-blue-600 dark:text-blue-400">
              Engineering case study
            </p>
            <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-6xl">
              Real-time speech pipeline for high-pressure communication
            </h1>
            <p className="mt-7 max-w-3xl text-xl leading-8 text-zinc-600 dark:text-zinc-400">
              InterviewMate began as a live-session assistant. This page documents the production
              path honestly: what the system does, where latency goes, which safeguards matter, and
              which numbers are design targets rather than promises.
            </p>
          </div>
          <div className="mt-10 flex flex-wrap gap-3 text-sm">
            {['Next.js + React', 'FastAPI + WebSockets', 'Deepgram Flux', 'Qdrant + Supabase'].map((item) => (
              <span
                key={item}
                className="rounded-full border border-zinc-300 px-4 py-2 text-zinc-700 dark:border-zinc-700 dark:text-zinc-300"
              >
                {item}
              </span>
            ))}
          </div>
          <p className="mt-8 max-w-3xl text-sm leading-6 text-zinc-500 dark:text-zinc-500">
            The current product can process live audio sessions and generate suggestions. Use it
            only for preparation or in settings where AI assistance is explicitly allowed.
          </p>
        </div>
      </section>

      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="max-w-2xl">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500">01 / System</p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">The pipeline is a sequence of small latency budgets</h2>
            <p className="mt-4 leading-7 text-zinc-600 dark:text-zinc-400">
              Streaming quality comes from keeping each boundary explicit: capture, transcode,
              turn detection, retrieval, generation, and delivery.
            </p>
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-5">
            {pipeline.map((item) => (
              <article
                key={item.step}
                className="rounded-2xl border border-zinc-200 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-950"
              >
                <span className="text-xs font-bold tracking-[0.2em] text-blue-600 dark:text-blue-400">{item.step}</span>
                <h3 className="mt-4 text-lg font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{item.detail}</p>
                <p className="mt-5 border-t border-zinc-200 pt-4 text-xs font-medium leading-5 text-zinc-500 dark:border-zinc-800">
                  {item.tech}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-zinc-50 px-6 py-20 dark:bg-zinc-950">
        <div className="mx-auto grid max-w-5xl gap-12 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500">02 / Latency</p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">Latency is a budget, not a slogan</h2>
            <p className="mt-4 leading-7 text-zinc-600 dark:text-zinc-400">
              The early transcription and first-token paths are faster than a complete response.
              Keeping that distinction visible prevents a fast demo metric from becoming a false
              end-to-end promise.
            </p>
          </div>
          <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-200 text-xs uppercase tracking-wider text-zinc-500 dark:border-zinc-800">
                <tr>
                  <th className="px-5 py-4 font-semibold">Stage</th>
                  <th className="px-5 py-4 font-semibold">Time</th>
                  <th className="px-5 py-4 font-semibold">Context</th>
                </tr>
              </thead>
              <tbody>
                {latencyRows.map(([stage, time, context]) => (
                  <tr key={stage} className="border-b border-zinc-100 last:border-0 dark:border-zinc-800/70">
                    <td className="px-5 py-4 font-medium">{stage}</td>
                    <td className="px-5 py-4 font-mono text-blue-700 dark:text-blue-300">{time}</td>
                    <td className="px-5 py-4 text-zinc-600 dark:text-zinc-400">{context}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="grid gap-12 lg:grid-cols-2">
            <div>
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500">03 / Retrieval</p>
              <h2 className="mt-3 text-3xl font-bold sm:text-4xl">User-specific retrieval keeps context useful and isolated</h2>
              <p className="mt-4 leading-7 text-zinc-600 dark:text-zinc-400">
                Prepared Q&A pairs are embedded and searched semantically. Every retrieval path is
                scoped by user identity, so a faster answer is not allowed to come at the cost of
                another user&apos;s context.
              </p>
              <ul className="mt-7 space-y-4 text-sm leading-6 text-zinc-700 dark:text-zinc-300">
                <li><span className="font-semibold">Direct match:</span> a similarity threshold can return a prepared answer without a new generation call.</li>
                <li><span className="font-semibold">Compound question:</span> retrieve several relevant pairs, then synthesize one response while tracking examples already used.</li>
                <li><span className="font-semibold">Graceful degradation:</span> Qdrant failure falls back to a slower but bounded path rather than silently mixing identities.</li>
              </ul>
            </div>
            <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-7 dark:border-zinc-800 dark:bg-zinc-950">
              <p className="text-sm font-semibold text-zinc-500">Cache layers</p>
              <div className="mt-6 space-y-5">
                {[
                  ['Exact / normalized lookup', 'Cheap hash-based matching handles repeated prepared questions before semantic search.'],
                  ['Semantic retrieval', 'Qdrant finds paraphrases and related examples inside the current user scope.'],
                  ['Prompt caching', 'Stable profile context can be reused so repeated requests spend less time rebuilding the prompt.'],
                ].map(([title, detail], index) => (
                  <div key={title} className="flex gap-4">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                      {index + 1}
                    </span>
                    <div>
                      <h3 className="font-semibold">{title}</h3>
                      <p className="mt-1 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-zinc-50 px-6 py-20 dark:bg-zinc-950">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500">04 / Routing</p>
          <h2 className="mt-3 max-w-2xl text-3xl font-bold sm:text-4xl">Routing and fallback protect the interaction</h2>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {[
              ['Question detection', 'Fast pattern checks handle obvious turns. Low-confidence cases can fall back to model verification instead of blocking every turn.'],
              ['Model routing', 'The current hybrid strategy tries a lower-cost primary model first and falls back to Claude when the primary path fails.'],
              ['Operational bounds', 'Timeouts, partial retrieval, connection cleanup, and user-scoped filters keep failure local and observable.'],
            ].map(([title, detail]) => (
              <article key={title} className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
                <h3 className="text-lg font-semibold">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{detail}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="max-w-3xl">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500">05 / Evaluation</p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">Evaluation methodology: measure quality and failure, not just speed</h2>
            <p className="mt-4 leading-7 text-zinc-600 dark:text-zinc-400">
              The useful unit is a question-to-response turn. Tests should replay representative
              questions, compare cached and generated paths, inspect retrieval scope, and record
              first-token plus complete-response latency. Quality review covers relevance,
              structure, factual grounding, and whether the response actually addresses the
              question.
            </p>
          </div>
          <div className="mt-10 grid gap-5 md:grid-cols-4">
            {[
              ['Deterministic', 'Unit-test normalization, question detection, cache hits, timeout behavior, and user filters.'],
              ['Replay-based', 'Run a fixed question set through cached, retrieved, and fallback paths so changes are comparable.'],
              ['Human review', 'Check relevance, clarity, grounding in the user context, and answer completeness.'],
              ['Known gap', 'The repository documents component benchmarks, but not a public production cohort or independently audited SLO.'],
            ].map(([title, detail]) => (
              <article key={title} className="rounded-2xl border border-zinc-200 p-5 dark:border-zinc-800">
                <h3 className="font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{detail}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-zinc-200 bg-[#0f1530] px-6 py-20 text-white dark:border-zinc-800">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-300">Reliability notes</p>
          <h2 className="mt-3 max-w-2xl text-3xl font-bold sm:text-4xl">Incidents became architecture decisions</h2>
          <div className="mt-10 overflow-hidden rounded-2xl border border-white/15 bg-white/5">
            <div className="hidden grid-cols-[1fr_1.2fr_1fr] gap-6 border-b border-white/10 px-6 py-4 text-xs font-semibold uppercase tracking-wider text-blue-200 md:grid">
              <span>Observed failure</span>
              <span>Change made</span>
              <span>Lesson</span>
            </div>
            {incidentRows.map((row) => (
              <div key={row.issue} className="grid gap-3 border-b border-white/10 px-6 py-6 last:border-0 md:grid-cols-[1fr_1.2fr_1fr] md:gap-6">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-blue-200 md:hidden">Observed failure</p>
                  <p className="mt-1 font-semibold">{row.issue}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-blue-200 md:hidden">Change made</p>
                  <p className="mt-1 text-sm leading-6 text-zinc-200">{row.change}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-blue-200 md:hidden">Lesson</p>
                  <p className="mt-1 text-sm leading-6 text-zinc-300">{row.lesson}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-12 flex flex-col gap-4 sm:flex-row">
            <Link href="/auth/register" className="inline-flex h-12 items-center justify-center rounded-full bg-white px-7 font-semibold text-[#0f1530] hover:bg-blue-50">
              Start preparing
            </Link>
            <Link href="/" className="inline-flex h-12 items-center justify-center rounded-full border border-white/30 px-7 font-semibold text-white hover:bg-white/10">
              Return home
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
