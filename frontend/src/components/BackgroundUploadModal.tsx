'use client';

import { useEffect } from 'react';

/**
 * AI Background Generation modal.
 *
 * Reuses the conceptual flow of /profile/context-upload — resume +
 * organization + interview details → AI extraction — but produces a
 * plain-text background summary instead of 30+ Q&A pairs. The output
 * streams back into the Your Background textarea on the parent
 * interview-settings page (handled by the parent via onResult).
 *
 * Differences from the AI Generator tab (per diary_v2 § 2.3):
 *   - Header: "AI Background Generation" (not "AI-Powered Q&A Generation")
 *   - File hint in amber: "only PDF, md, docx"
 *   - English-only disclaimer underneath
 *   - Organization Information + Interview Details = REQUIRED (not optional)
 *   - No user mini-card ("Default / Solutions Architect @ OpenAI")
 *   - Action button: "Result" (not "Generate Q&A Pairs")
 *
 * This commit is scaffold-only — form fields + Result button are wired
 * to the backend in commits 7-8 of the profiles branch.
 */

interface BackgroundUploadModalProps {
    open: boolean;
    onClose: () => void;
    onResult: (backgroundText: string) => void;
}

export function BackgroundUploadModal({ open, onClose }: BackgroundUploadModalProps) {
    // Close on Escape so users have a non-mouse exit
    useEffect(() => {
        if (!open) return;
        const onKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [open, onClose]);

    if (!open) return null;

    return (
        <div
            className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 sm:items-center"
            onClick={onClose}
            role="dialog"
            aria-modal="true"
            aria-labelledby="bg-upload-title"
        >
            <div
                onClick={(e) => e.stopPropagation()}
                className="w-full max-w-3xl rounded-2xl bg-white shadow-2xl dark:bg-zinc-950"
            >
                {/* Header */}
                <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
                    <h2
                        id="bg-upload-title"
                        className="text-2xl font-bold text-zinc-900 dark:text-zinc-100"
                    >
                        AI Background Generation
                    </h2>
                    <button
                        type="button"
                        onClick={onClose}
                        aria-label="Close"
                        className="rounded-lg p-2 text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
                    >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Body — scaffold. Form fields + Result wiring land in next commits */}
                <div className="space-y-6 px-6 py-6">
                    {/* File upload */}
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            Upload your background document
                        </label>
                        <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
                            only PDF, md, docx
                        </p>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400">
                            (we support English only now)
                        </p>
                        {/* Real <input type="file"> + dropzone wired in a follow-up commit */}
                        <div className="mt-3 flex h-32 items-center justify-center rounded-lg border-2 border-dashed border-zinc-300 bg-zinc-50 text-sm text-zinc-400 dark:border-zinc-700 dark:bg-zinc-900">
                            [ file picker — next commit ]
                        </div>
                    </div>

                    {/* Organization Information — REQUIRED */}
                    <div>
                        <h3 className="mb-2 flex items-center gap-2 text-base font-semibold text-zinc-900 dark:text-zinc-100">
                            <span>🏢 Organization Information</span>
                            <span className="text-sm font-normal text-red-600 dark:text-red-400">required</span>
                        </h3>
                        <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4 text-sm text-zinc-400 dark:border-zinc-700 dark:bg-zinc-900">
                            [ org name / overview / job posting fields — next commit ]
                        </div>
                    </div>

                    {/* Interview Details — REQUIRED */}
                    <div>
                        <h3 className="mb-2 flex items-center gap-2 text-base font-semibold text-zinc-900 dark:text-zinc-100">
                            <span>📋 Interview Details</span>
                            <span className="text-sm font-normal text-red-600 dark:text-red-400">required</span>
                        </h3>
                        <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4 text-sm text-zinc-400 dark:border-zinc-700 dark:bg-zinc-900">
                            [ role / interview type / answer style fields — next commit ]
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-3 border-t border-zinc-200 px-6 py-4 dark:border-zinc-800">
                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        disabled
                        title="Wired to backend in the next commit"
                        className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
                    >
                        Result
                    </button>
                </div>
            </div>
        </div>
    );
}
