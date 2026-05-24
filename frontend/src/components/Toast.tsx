'use client';

import { useEffect } from 'react';

export type ToastVariant = 'info' | 'warning' | 'success';

interface ToastProps {
    message: string;
    onDismiss: () => void;
    durationMs?: number;
    variant?: ToastVariant;
}

/**
 * Minimal self-contained toast — no library needed.
 * Lives in the bottom-right, auto-dismisses after `durationMs`,
 * and is also dismissable via the × button.
 */
export function Toast({
    message,
    onDismiss,
    durationMs = 6000,
    variant = 'info',
}: ToastProps) {
    useEffect(() => {
        const timer = setTimeout(onDismiss, durationMs);
        return () => clearTimeout(timer);
    }, [onDismiss, durationMs]);

    const variantClass = {
        info:    'bg-blue-600 text-white',
        warning: 'bg-amber-500 text-white',
        success: 'bg-green-600 text-white',
    }[variant];

    return (
        <div
            role="status"
            aria-live="polite"
            className="fixed bottom-6 right-6 z-50 max-w-sm animate-in slide-in-from-bottom-4 duration-200"
        >
            <div className={`flex items-start gap-3 rounded-lg ${variantClass} p-4 shadow-lg`}>
                <p className="flex-1 text-sm leading-relaxed">{message}</p>
                <button
                    type="button"
                    onClick={onDismiss}
                    aria-label="Dismiss"
                    className="flex-shrink-0 text-white/80 transition-colors hover:text-white"
                >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>
    );
}
