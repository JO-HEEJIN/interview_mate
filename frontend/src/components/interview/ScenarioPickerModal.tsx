'use client';

/**
 * Onboarding scenario picker — appears on the first /interview visit
 * (localStorage flag) and via the "Change scenario" link any time after.
 *
 * Design follows the Option 4 user-turn cue strategy: the chosen text
 * becomes a per-question "[Round: X] " prefix on the LLM side — the
 * system prompt is never touched (car_wash dilution avoidance).
 *
 * Free text input + a few domain-neutral suggestion chips. Domain-
 * neutral on purpose: InterviewMate users span SWE, PhD admission, F1
 * visa, marketing, etc. We don't want SWE-flavored defaults to bias
 * away non-SWE users.
 */

import { useEffect, useState, useRef } from 'react';

interface ScenarioPickerModalProps {
    open: boolean;
    initialValue?: string;
    /** Title/CTA copy switches: first-visit modal vs "Change" reopen */
    isFirstVisit: boolean;
    onSkip: () => void;
    onConfirm: (scenario: string) => void;
}

const SUGGESTIONS = [
    'Behavioral / STAR',
    'System design',
    'Case interview',
    'Coding round',
    'PhD admission',
    'Visa interview',
];

export function ScenarioPickerModal({
    open,
    initialValue = '',
    isFirstVisit,
    onSkip,
    onConfirm,
}: ScenarioPickerModalProps) {
    const [value, setValue] = useState(initialValue);
    const inputRef = useRef<HTMLInputElement>(null);

    // Reset whenever modal reopens (so reopen-after-skip shows fresh)
    useEffect(() => {
        if (open) setValue(initialValue);
    }, [open, initialValue]);

    // Focus input on open for keyboard-first users
    useEffect(() => {
        if (open && inputRef.current) inputRef.current.focus();
    }, [open]);

    // Esc closes (acts as skip)
    useEffect(() => {
        if (!open) return;
        const onKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onSkip();
            if (e.key === 'Enter' && value.trim()) onConfirm(value.trim());
        };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [open, value, onSkip, onConfirm]);

    if (!open) return null;

    const trimmed = value.trim();

    return (
        <div
            className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 sm:items-center"
            onClick={onSkip}
            role="dialog"
            aria-modal="true"
            aria-labelledby="scenario-picker-title"
        >
            <div
                onClick={(e) => e.stopPropagation()}
                className="w-full max-w-lg rounded-2xl bg-white shadow-2xl dark:bg-zinc-950"
            >
                <div className="border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
                    <h2
                        id="scenario-picker-title"
                        className="text-xl font-bold text-zinc-900 dark:text-zinc-100"
                    >
                        {isFirstVisit ? '오늘 어떤 인터뷰인가요?' : 'Change scenario'}
                    </h2>
                    <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                        {isFirstVisit
                            ? '한 줄로 알려주시면 답변을 그 라운드에 맞춰드려요. 비워두고 시작해도 됩니다.'
                            : 'New value will apply to the next question.'}
                    </p>
                </div>

                <div className="space-y-4 px-6 py-6">
                    <div>
                        <label
                            htmlFor="scenario-input"
                            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                        >
                            Scenario
                        </label>
                        <input
                            ref={inputRef}
                            id="scenario-input"
                            type="text"
                            value={value}
                            onChange={(e) => setValue(e.target.value)}
                            placeholder="e.g. system design, PhD admission, F1 visa…"
                            maxLength={80}
                            className="mt-2 w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                        />
                    </div>

                    <div>
                        <p className="mb-2 text-xs text-zinc-500 dark:text-zinc-400">
                            Common types:
                        </p>
                        <div className="flex flex-wrap gap-2">
                            {SUGGESTIONS.map((s) => (
                                <button
                                    key={s}
                                    type="button"
                                    onClick={() => setValue(s)}
                                    className="rounded-full border border-zinc-300 px-3 py-1 text-xs text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="flex items-center justify-end gap-3 border-t border-zinc-200 px-6 py-4 dark:border-zinc-800">
                    <button
                        type="button"
                        onClick={onSkip}
                        className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                    >
                        {isFirstVisit ? 'Skip for now' : 'Cancel'}
                    </button>
                    <button
                        type="button"
                        onClick={() => onConfirm(trimmed)}
                        disabled={!trimmed}
                        className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                    >
                        {isFirstVisit ? 'Start with this' : 'Save'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export const SCENARIO_STORAGE_KEY = 'interview_mate_scenario';
export const ONBOARDED_FLAG_KEY = 'interview_mate_onboarded';
