'use client';

/**
 * Session detail — paginated Q&A view + per-session export buttons.
 * Backed by GET /api/interview-sessions/{session_id}/export?format=json
 * which returns {session, messages, examples_used}.
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { authFetch } from '@/lib/authFetch';

interface SessionMeta {
    id: string;
    title: string;
    status: string;
    started_at: string;
    ended_at: string | null;
    duration_seconds: number | null;
    question_count: number;
}

interface SessionMessage {
    id: string;
    role: string;            // interviewer | candidate | system
    message_type: string;    // question | answer | transcription | note
    content: string;
    question_type: string | null;
    source: string | null;
    examples_used: string[] | null;
    timestamp: string;
}

interface SessionHistory {
    session: SessionMeta;
    messages: SessionMessage[];
    examples_used: string[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function formatDate(iso: string): string {
    try {
        return new Date(iso).toLocaleString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit',
        });
    } catch { return iso; }
}

export default function SessionDetailPage() {
    const router = useRouter();
    const params = useParams();
    const sessionId = params?.id as string;

    const [authChecked, setAuthChecked] = useState(false);
    const [data, setData] = useState<SessionHistory | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        supabase.auth.getUser().then(({ data: { user } }) => {
            if (!user) {
                router.push('/auth/login');
                return;
            }
            setAuthChecked(true);
        });
    }, [router]);

    useEffect(() => {
        if (!authChecked || !sessionId) return;
        (async () => {
            setIsLoading(true);
            try {
                const res = await authFetch(`${API_URL}/api/interview-sessions/${sessionId}/export?format=json`);
                if (!res.ok) throw new Error(`Failed (${res.status})`);
                const body = await res.json();
                setData(body);
                setError(null);
            } catch (e) {
                setError(e instanceof Error ? e.message : 'Failed to load session');
            } finally {
                setIsLoading(false);
            }
        })();
    }, [authChecked, sessionId]);

    const triggerDownload = (format: 'anki-csv' | 'text' | 'markdown') => {
        const a = document.createElement('a');
        a.href = `${API_URL}/api/interview-sessions/${sessionId}/export?format=${format}`;
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    if (!authChecked || isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black">
                <div className="text-zinc-500">Loading session…</div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="min-h-screen bg-zinc-50 dark:bg-black">
                <div className="mx-auto max-w-3xl px-4 py-12">
                    <Link href="/profile/sessions" className="text-sm text-zinc-500 hover:underline">
                        ← Back to sessions
                    </Link>
                    <div className="mt-6 rounded-lg bg-red-50 p-4 text-red-700 dark:bg-red-950 dark:text-red-300">
                        {error || 'Session not found'}
                    </div>
                </div>
            </div>
        );
    }

    // Only show user-visible message types — drop raw transcription partials,
    // system notes, etc. Q&A is what the user came here to read.
    const visibleMessages = data.messages.filter(
        (m) => m.message_type === 'question' || m.message_type === 'answer'
    );

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-black">
            <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
                <div className="mx-auto max-w-3xl px-4 py-6">
                    <Link href="/profile/sessions" className="text-sm text-zinc-500 hover:underline">
                        ← Back to sessions
                    </Link>
                    <div className="mt-3 flex flex-wrap items-start justify-between gap-3">
                        <div>
                            <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                                {data.session.title || 'Interview Session'}
                            </h1>
                            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                                {formatDate(data.session.started_at)} · {data.session.question_count} {data.session.question_count === 1 ? 'turn' : 'turns'}
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => triggerDownload('anki-csv')}
                                className="rounded-md border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                            >
                                ⬇ Anki CSV
                            </button>
                            <button
                                onClick={() => triggerDownload('text')}
                                className="rounded-md border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                            >
                                ⬇ Text
                            </button>
                            <button
                                onClick={() => triggerDownload('markdown')}
                                className="rounded-md border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                            >
                                ⬇ Markdown
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="mx-auto max-w-3xl px-4 py-6">
                {visibleMessages.length === 0 ? (
                    <div className="rounded-lg border border-zinc-200 bg-white p-12 text-center text-zinc-500 dark:border-zinc-800 dark:bg-zinc-950">
                        No Q&A captured in this session.
                    </div>
                ) : (
                    <div className="space-y-4">
                        {visibleMessages.map((m) => (
                            <div
                                key={m.id}
                                className={
                                    m.message_type === 'question'
                                        ? 'rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950'
                                        : 'rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-900'
                                }
                            >
                                <div className="mb-2 text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                                    {m.message_type === 'question' ? 'Q' : 'A'}
                                    {m.question_type && ` · ${m.question_type}`}
                                </div>
                                <p className="whitespace-pre-wrap text-sm text-zinc-900 dark:text-zinc-100">
                                    {m.content}
                                </p>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
