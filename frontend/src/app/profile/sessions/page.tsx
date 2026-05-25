'use client';

/**
 * Sessions list page — every interview the user has ever held, with one-
 * click Anki / Text export per session. Data is already persisted by the
 * WebSocket flow (backend/app/api/websocket.py:89), so this page is
 * read-only over that.
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';

interface SessionRow {
    id: string;
    user_id: string;
    title: string;
    session_type: string;
    status: string;
    started_at: string;
    ended_at: string | null;
    duration_seconds: number | null;
    question_count: number;
    notes: string | null;
    created_at: string;
    updated_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function formatDate(iso: string): string {
    try {
        const d = new Date(iso);
        return d.toLocaleString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit',
        });
    } catch {
        return iso;
    }
}

function formatDuration(seconds: number | null): string {
    if (!seconds || seconds < 1) return '—';
    if (seconds < 60) return `${seconds}s`;
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return s ? `${m}m ${s}s` : `${m}m`;
}

export default function SessionsListPage() {
    const router = useRouter();
    const [userId, setUserId] = useState<string | null>(null);
    const [sessions, setSessions] = useState<SessionRow[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Resolve userId from supabase auth
    useEffect(() => {
        supabase.auth.getUser().then(({ data: { user } }) => {
            if (!user) {
                router.push('/auth/login');
                return;
            }
            setUserId(user.id);
        });
    }, [router]);

    useEffect(() => {
        if (!userId) return;
        (async () => {
            setIsLoading(true);
            try {
                const res = await fetch(`${API_URL}/api/interview-sessions/${userId}/sessions?limit=50`);
                if (!res.ok) throw new Error(`Failed (${res.status})`);
                const data = await res.json();
                setSessions(data || []);
                setError(null);
            } catch (e) {
                setError(e instanceof Error ? e.message : 'Failed to load sessions');
            } finally {
                setIsLoading(false);
            }
        })();
    }, [userId]);

    // Download via anchor click so the server-set filename is honored
    const triggerDownload = (sessionId: string, format: 'anki-csv' | 'text') => {
        const url = `${API_URL}/api/interview-sessions/${sessionId}/export?format=${format}`;
        const a = document.createElement('a');
        a.href = url;
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    const handleDelete = async (sessionId: string) => {
        if (!confirm('Delete this session and all its messages? This cannot be undone.')) return;
        try {
            const res = await fetch(`${API_URL}/api/interview-sessions/${sessionId}`, { method: 'DELETE' });
            if (!res.ok) throw new Error(`Failed (${res.status})`);
            setSessions((prev) => prev.filter((s) => s.id !== sessionId));
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Failed to delete session');
        }
    };

    if (!userId || isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black">
                <div className="text-zinc-500">Loading sessions…</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-black">
            <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
                <div className="mx-auto max-w-4xl px-4 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                                Interview Sessions
                            </h1>
                            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                                Every interview is saved automatically. Export to Anki or plain text any time.
                            </p>
                        </div>
                        <Link
                            href="/interview"
                            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                        >
                            Start new
                        </Link>
                    </div>
                </div>
            </header>

            <main className="mx-auto max-w-4xl px-4 py-6">
                {error && (
                    <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
                        {error}
                        <button onClick={() => setError(null)} className="ml-2 underline">Dismiss</button>
                    </div>
                )}

                {sessions.length === 0 ? (
                    <div className="rounded-lg border border-zinc-200 bg-white p-12 text-center dark:border-zinc-800 dark:bg-zinc-950">
                        <p className="text-zinc-600 dark:text-zinc-400">
                            No interview sessions yet.
                        </p>
                        <Link
                            href="/interview"
                            className="mt-4 inline-block rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                        >
                            Start your first interview
                        </Link>
                    </div>
                ) : (
                    <ul className="space-y-3">
                        {sessions.map((s) => (
                            <li
                                key={s.id}
                                className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950"
                            >
                                <div className="flex flex-wrap items-center justify-between gap-3">
                                    <div className="min-w-0 flex-1">
                                        <div className="flex flex-wrap items-baseline gap-2">
                                            <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                                                📅 {formatDate(s.started_at)}
                                            </span>
                                            <span className="text-xs text-zinc-500 dark:text-zinc-400">
                                                · {s.question_count} {s.question_count === 1 ? 'turn' : 'turns'}
                                            </span>
                                            <span className="text-xs text-zinc-500 dark:text-zinc-400">
                                                · {formatDuration(s.duration_seconds)}
                                            </span>
                                            {s.status !== 'completed' && (
                                                <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                                                    {s.status}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex shrink-0 gap-2">
                                        <Link
                                            href={`/profile/sessions/${s.id}`}
                                            className="rounded-md border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                                        >
                                            Open
                                        </Link>
                                        <button
                                            onClick={() => triggerDownload(s.id, 'anki-csv')}
                                            title="Download as Anki-compatible CSV"
                                            className="rounded-md border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                                        >
                                            ⬇ Anki
                                        </button>
                                        <button
                                            onClick={() => triggerDownload(s.id, 'text')}
                                            title="Download as plain text"
                                            className="rounded-md border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                                        >
                                            ⬇ Text
                                        </button>
                                        <button
                                            onClick={() => handleDelete(s.id)}
                                            title="Delete this session"
                                            className="rounded-md border border-red-300 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400 dark:hover:bg-red-950"
                                        >
                                            ×
                                        </button>
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </main>
        </div>
    );
}
