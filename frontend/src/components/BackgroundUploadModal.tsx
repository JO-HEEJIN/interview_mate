'use client';

import { useEffect, useState, useRef } from 'react';

/**
 * AI Background Generation modal.
 *
 * Reuses the conceptual flow of /profile/context-upload — resume +
 * organization + interview details → AI extraction — but:
 *   - produces a plain-text background summary instead of 30+ Q&A pairs
 *   - lives in a modal so users don't leave Settings
 *   - simplified form (no screenshot OCR for org/interview, just textareas)
 *
 * Differences from the AI Generator tab (per diary_v2 § 2.3):
 *   - Header: "AI Background Generation" (not "AI-Powered Q&A Generation")
 *   - File hint in amber: "only PDF, md, docx"
 *   - English-only disclaimer underneath
 *   - Organization Information + Interview Details = REQUIRED (not optional)
 *   - No user mini-card ("Default / Solutions Architect @ OpenAI")
 *   - Action button: "Result" (not "Generate Q&A Pairs")
 *
 * Result button is wired to the streaming /extract-background endpoint
 * in commit 8 of this branch (10 in the overall block 2 numbering).
 * For now it validates the form and shows a "wired next commit" toast.
 */

interface BackgroundUploadModalProps {
    open: boolean;
    onClose: () => void;
    onResult: (backgroundText: string) => void;
}

const ACCEPTED_EXTENSIONS = '.pdf,.md,.docx';

export function BackgroundUploadModal({ open, onClose }: BackgroundUploadModalProps) {
    // Form state — local to the modal; cleared on close
    const [resumeFile, setResumeFile] = useState<File | null>(null);
    const [orgText, setOrgText] = useState('');
    const [interviewText, setInterviewText] = useState('');
    const [validationError, setValidationError] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    // Close on Escape so users have a non-mouse exit
    useEffect(() => {
        if (!open) return;
        const onKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [open, onClose]);

    // Reset form whenever the modal closes (so the next open is clean)
    useEffect(() => {
        if (!open) {
            setResumeFile(null);
            setOrgText('');
            setInterviewText('');
            setValidationError(null);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    }, [open]);

    const isFormValid =
        resumeFile !== null && orgText.trim().length > 0 && interviewText.trim().length > 0;

    const handleResult = () => {
        if (!isFormValid) {
            setValidationError(
                !resumeFile
                    ? 'Please upload a background document (PDF, md, or docx).'
                    : !orgText.trim()
                    ? 'Organization information is required.'
                    : 'Interview details are required.',
            );
            return;
        }
        setValidationError(null);
        // Placeholder until commit 10 wires the streaming endpoint
        alert(
            'Backend background-extraction endpoint lands in the next commit.\n' +
            'When wired, this button will stream the extracted background text into the Your Background textarea.',
        );
    };

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

                {/* Body */}
                <div className="space-y-6 px-6 py-6">
                    {/* File upload */}
                    <div>
                        <label
                            htmlFor="bg-resume-file"
                            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                        >
                            Upload your background document
                        </label>
                        <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
                            only PDF, md, docx
                        </p>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400">
                            (we support English only now)
                        </p>
                        <input
                            ref={fileInputRef}
                            id="bg-resume-file"
                            type="file"
                            accept={ACCEPTED_EXTENSIONS}
                            onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                            className="mt-3 block w-full cursor-pointer rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-700 file:mr-3 file:rounded-md file:border-0 file:bg-zinc-100 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-zinc-700 hover:file:bg-zinc-200 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:file:bg-zinc-800 dark:file:text-zinc-300 dark:hover:file:bg-zinc-700"
                        />
                        {resumeFile && (
                            <p className="mt-2 text-xs text-zinc-600 dark:text-zinc-400">
                                Selected: <span className="font-medium">{resumeFile.name}</span> ({(resumeFile.size / 1024).toFixed(1)} KB)
                            </p>
                        )}
                    </div>

                    {/* Organization Information — REQUIRED */}
                    <div>
                        <label
                            htmlFor="bg-org-text"
                            className="mb-2 flex items-center gap-2 text-base font-semibold text-zinc-900 dark:text-zinc-100"
                        >
                            <span>🏢 Organization Information</span>
                            <span className="text-sm font-normal text-red-600 dark:text-red-400">required</span>
                        </label>
                        <p className="mb-2 text-xs text-zinc-500 dark:text-zinc-400">
                            Company, university, or organization details — mission, values, program description, etc.
                        </p>
                        <textarea
                            id="bg-org-text"
                            value={orgText}
                            onChange={(e) => setOrgText(e.target.value)}
                            placeholder="Paste organization info here..."
                            rows={4}
                            className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                        />
                    </div>

                    {/* Interview Details — REQUIRED */}
                    <div>
                        <label
                            htmlFor="bg-interview-text"
                            className="mb-2 flex items-center gap-2 text-base font-semibold text-zinc-900 dark:text-zinc-100"
                        >
                            <span>📋 Interview Details</span>
                            <span className="text-sm font-normal text-red-600 dark:text-red-400">required</span>
                        </label>
                        <p className="mb-2 text-xs text-zinc-500 dark:text-zinc-400">
                            Job posting, thesis abstract, program requirements, interview topics, etc.
                        </p>
                        <textarea
                            id="bg-interview-text"
                            value={interviewText}
                            onChange={(e) => setInterviewText(e.target.value)}
                            placeholder="Paste interview details here..."
                            rows={4}
                            className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                        />
                    </div>

                    {validationError && (
                        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
                            {validationError}
                        </div>
                    )}
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
                        onClick={handleResult}
                        disabled={!isFormValid}
                        className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                    >
                        Result
                    </button>
                </div>
            </div>
        </div>
    );
}
