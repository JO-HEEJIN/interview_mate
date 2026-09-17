import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Engineering Case Study | InterviewMate',
  description:
    'How InterviewMate built a real-time speech, retrieval, caching, and model-routing pipeline for interview practice sessions, and how a reasoning failure became a controlled experiment.',
  alternates: {
    canonical: '/engineering',
  },
};

const pipeline = [
  {
    step: '01',
    title: 'Capture',
    detail: 'The browser records the microphone, optionally mixed with audio shared from another tab or app, as WebM/Opus chunks.',
    tech: 'MediaRecorder · 1 s chunks',
  },
  {
    step: '02',
    title: 'Transcribe',
    detail: 'An async FastAPI WebSocket pipes chunks through an FFmpeg subprocess to 16 kHz linear PCM and streams them to Deepgram.',
    tech: 'FFmpeg · WebSocket · Deepgram flux-general-en',
  },
  {
    step: '03',
    title: 'Detect',
    detail: 'Deepgram end-of-turn events and lexical checks mark likely questions; low-confidence short utterances are verified by a model call.',
    tech: 'EOT threshold 0.7 · 800 ms EOT timeout',
  },
  {
    step: '04',
    title: 'Retrieve',
    detail: 'Compound questions are split into up to three sub-queries; each searches only the user’s own prepared Q&A pairs.',
    tech: 'Qdrant user_id filter · 5 s per-search timeout',
  },
  {
    step: '05',
    title: 'Respond',
    detail: 'A closely matching prepared answer, or a streamed model response, is sent back over the same socket.',
    tech: 'Prepared-answer match · Claude streaming · prompt caching',
  },
];

const latencyRows = [
  ['Client chunk interval', '1,000 ms', 'Set in the practice page recorder; trades socket chatter for turn latency'],
  ['End-of-turn timeout', '800 ms', 'Deepgram EOT timeout; server-side end-of-turn events decide when a question is complete'],
  ['Retrieval bound', '5 s per sub-query', 'Up to three parallel searches; a timeout yields partial context, not a stalled turn'],
];

const incidentRows = [
  {
    issue: 'Thread bridge created 5-second stalls',
    change: 'Moved audio forwarding to a fully async subprocess and direct await.',
    lesson: 'Keep the hot path on one async event loop; avoid blocking waits around streaming I/O.',
  },
  {
    issue: 'Long questions could hang during decomposition',
    change: 'Replaced a model round-trip for decomposition with heuristic splitting (max three sub-queries) and added 5-second per-search timeouts.',
    lesson: 'A useful partial result is better than an unbounded wait in a real-time turn.',
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
              A real-time speech and retrieval pipeline for interview practice
            </h1>
            <p className="mt-7 max-w-3xl text-xl leading-8 text-zinc-600 dark:text-zinc-400">
              InterviewMate turns spoken practice questions into personalized response suggestions
              in real time. This page documents the production path: what the system does, where
              latency budget goes, which safeguards matter, and what has and has not been measured.
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
            InterviewMate was first marketed for use during live interviews; it is now positioned
            for preparation and mock sessions. The pipeline can process any live audio it is given,
            so the product states the boundary plainly: use it for rehearsal or where AI assistance
            is explicitly allowed, and disclose it when an organizer requires.
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
              These are the configured bounds in the code, not measured end-to-end numbers. Turn
              detection alone spends most of a second by design, so first-token and complete-response
              latency need separate measurement rather than one headline figure.
            </p>
          </div>
          <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-200 text-xs uppercase tracking-wider text-zinc-500 dark:border-zinc-800">
                <tr>
                  <th className="px-5 py-4 font-semibold">Stage</th>
                  <th className="px-5 py-4 font-semibold">Bound</th>
                  <th className="px-5 py-4 font-semibold">Why</th>
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
                Prepared Q&A pairs are embedded and searched semantically. Vector searches are
                filtered by the authenticated user ID, so a faster answer is not allowed to come at
                the cost of another user&apos;s context.
              </p>
              <ul className="mt-7 space-y-4 text-sm leading-6 text-zinc-700 dark:text-zinc-300">
                <li><span className="font-semibold">Direct match:</span> a prepared answer at ≥0.85 similarity is returned without a generation call. The threshold was raised from 0.70 after a wrong prepared answer surfaced in production.</li>
                <li><span className="font-semibold">Compound question:</span> retrieve several relevant pairs, then synthesize one response while tracking examples already used in the session.</li>
                <li><span className="font-semibold">Graceful degradation:</span> if Qdrant is unavailable, the model is given the user&apos;s own prepared Q&amp;A pairs directly; a search timeout returns partial context rather than blocking the turn.</li>
              </ul>
            </div>
            <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-7 dark:border-zinc-800 dark:bg-zinc-950">
              <p className="text-sm font-semibold text-zinc-500">Cache layers</p>
              <div className="mt-6 space-y-5">
                {[
                  ['Prepared-answer match', 'Exact and lexical similarity (max of substring, token Jaccard, and sequence ratio) against the user&apos;s own prepared Q&A. At 0.85 or above the prepared answer is returned without a generation call.'],
                  ['Semantic retrieval', 'Qdrant finds paraphrases and related prepared answers inside the current user scope.'],
                  ['Prompt caching', 'The stable system prompt is marked for Anthropic prompt caching so repeated turns avoid re-processing it.'],
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
              ['Model choice', 'A lower-cost GLM-first hybrid was tried and turned off in February 2026 because it ignored the user profile, prepared Q&A, and session context. Claude is the only answer model.'],
              ['Operational bounds', 'Timeouts, partial retrieval, connection cleanup, and user-scoped filters keep a failed search from stalling the turn.'],
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
              The useful unit is a question-to-response turn. The repository contains benchmark
              scripts for question detection, Q&amp;A cache lookup, and model latency, plus
              reproducible prompt experiments with raw outputs and summaries. What it does not yet
              have is an automated regression suite or committed production latency data.
            </p>
          </div>
          <div className="mt-10 grid gap-5 md:grid-cols-4">
            {[
              ['Component benchmarks', 'Scripts time regex question detection, cache lookup, and GLM vs Claude responses. They print results; they do not assert thresholds.'],
              ['Controlled prompt runs', 'Fixed question, fixed model and temperature, 20–100 runs per condition, automatic pass/fail scoring with ambiguous cases kept separate.'],
              ['Production A/B signal', 'Each user is assigned a prompt variant through Statsig; thumbs up/down on suggestions is logged against that variant. Session transcripts can be exported for review.'],
              ['Known gap', 'No automated regression suite, committed production latency data, or independently audited SLO yet.'],
            ].map(([title, detail]) => (
              <article key={title} className="rounded-2xl border border-zinc-200 p-5 dark:border-zinc-800">
                <h3 className="font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{detail}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-zinc-50 px-6 py-20 dark:bg-zinc-950">
        <div className="mx-auto max-w-5xl">
          <div className="max-w-3xl">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500">06 / Research</p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">A lucky answer became a controlled experiment</h2>
            <p className="mt-4 leading-7 text-zinc-600 dark:text-zinc-400">
              A widely shared prompt (&ldquo;The car wash is 50 meters away. Should I walk or
              drive?&rdquo;) trips many models because the car must be at the car wash. In one practice
              session InterviewMate answered &ldquo;drive&rdquo;. We did not know which prompt layer
              caused it, so we isolated them.
            </p>
          </div>
          <ol className="mt-10 grid gap-5 md:grid-cols-3">
            {[
              ['Ablation', 'Six prompt conditions, 20 runs each, claude-sonnet-4-5 at temperature 0.7. A short role + STAR scaffold passed 17/20; role + profile context passed 6/20; bare and role-only passed 0/20.'],
              ['Reproduction on production', 'The same STAR scaffold inside the full production prompt passed 0/20 and 6/20 depending on profile. Standalone it passed 20/20, then 100/100 on claude-sonnet-4-6. The earlier production “drive” used distance-based reasoning. It was right for the wrong reason.'],
              ['What changed', 'The investigation also found a similarity bug that returned 0.95 for unrelated equal-length strings and a too-loose 0.70 retrieval threshold. Both were fixed. New profiles now default to the short STAR prompt, and session scenario hints are added to the user turn instead of the system prompt.'],
            ].map(([title, detail]) => (
              <li key={title} className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
                <h3 className="text-lg font-semibold">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{detail}</p>
              </li>
            ))}
          </ol>
          <p className="mt-8 max-w-3xl text-sm leading-6 text-zinc-500 dark:text-zinc-400">
            Limits: one question, small samples, Anthropic models only in these runs. The result
            supports a narrow claim, that instruction ordering in a long prompt can suppress a
            reasoning scaffold. It does not show that any prompt works for every topic.{' '}
            <a
              href="https://github.com/JO-HEEJIN/interview_mate/tree/main/car_wash"
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold text-zinc-900 underline dark:text-zinc-100"
            >
              Code, raw outputs, and summaries
            </a>
            .
          </p>
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
              Start practicing
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
