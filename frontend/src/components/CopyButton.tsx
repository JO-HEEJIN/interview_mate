'use client';

import { useState } from 'react';

interface CopyButtonProps {
    text: string;
    label?: string;
    className?: string;
}

/**
 * Small inline "Copy" button for prompt templates.
 * Falls back silently on browsers without the clipboard API
 * (vanishingly rare on the target audience).
 */
export function CopyButton({ text, label = 'Copy', className = '' }: CopyButtonProps) {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            // No-op: modern browsers all support clipboard.writeText over HTTPS.
        }
    };

    return (
        <button
            type="button"
            onClick={handleCopy}
            aria-label={copied ? 'Copied to clipboard' : `Copy ${label.toLowerCase()} to clipboard`}
            className={`inline-flex items-center gap-1.5 rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800 ${className}`}
        >
            {copied ? (
                <>
                    <svg className="h-3.5 w-3.5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Copied!
                </>
            ) : (
                <>
                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    {label}
                </>
            )}
        </button>
    );
}
