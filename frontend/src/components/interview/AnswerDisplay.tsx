'use client';

/**
 * Display for AI-generated answer suggestions
 * Enhanced with better UI, loading states, and interaction feedback
 */

import { useState } from 'react';

interface Answer {
    question: string;
    answer: string;
    timestamp: Date;
    questionType?: string;
    isRegenerating?: boolean;
    source?: string;
    hasPlaceholder?: boolean;
}

interface AnswerDisplayProps {
    answers: Answer[];
    isGenerating: boolean;
    temporaryAnswer?: string | null;
    streamingAnswer?: string;
    streamingQuestion?: string;
    onRegenerate?: (question: string) => void;
    onRateAnswer?: (question: string, rating: 'up' | 'down') => void;
    onStopGenerating?: () => void;
    aiGeneratorAvailable?: boolean;
}

// Helper function to highlight placeholder text [like this] with purple-pink color
function highlightPlaceholders(text: string) {
    const parts: JSX.Element[] = [];
    const regex = /(\[.*?\])/g;
    let lastIndex = 0;
    let match;
    let key = 0;

    while ((match = regex.exec(text)) !== null) {
        // Add text before the placeholder
        if (match.index > lastIndex) {
            parts.push(
                <span key={`text-${key++}`}>
                    {text.substring(lastIndex, match.index)}
                </span>
            );
        }

        // Add the placeholder with purple-pink styling
        parts.push(
            <span
                key={`placeholder-${key++}`}
                className="text-fuchsia-500 dark:text-fuchsia-400 font-semibold"
            >
                {match[0]}
            </span>
        );

        lastIndex = match.index + match[0].length;
    }

    // Add remaining text after the last placeholder
    if (lastIndex < text.length) {
        parts.push(
            <span key={`text-${key++}`}>
                {text.substring(lastIndex)}
            </span>
        );
    }

    return parts.length > 0 ? parts : text;
}

// Inline SVG Icons
const CopyIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
);

const CheckIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
);

const RefreshCwIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
);

const ThumbsUpIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
    </svg>
);

const ThumbsDownIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
    </svg>
);

const XIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
);

export function AnswerDisplay({ answers, isGenerating, temporaryAnswer, streamingAnswer, streamingQuestion, onRegenerate, onRateAnswer, onStopGenerating, aiGeneratorAvailable }: AnswerDisplayProps) {
    const [expandedAnswers, setExpandedAnswers] = useState<Set<number>>(new Set());
    const [copiedAnswer, setCopiedAnswer] = useState<number | null>(null);
    const [ratedAnswers, setRatedAnswers] = useState<Map<string, 'up' | 'down'>>(new Map());

    const toggleExpanded = (index: number) => {
        const newExpanded = new Set(expandedAnswers);
        if (newExpanded.has(index)) {
            newExpanded.delete(index);
        } else {
            newExpanded.add(index);
        }
        setExpandedAnswers(newExpanded);
    };

    const copyToClipboard = async (text: string, index: number) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopiedAnswer(index);
            setTimeout(() => setCopiedAnswer(null), 2000);
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
    };

    const rateAnswer = (question: string, rating: 'up' | 'down') => {
        setRatedAnswers(new Map(ratedAnswers.set(question, rating)));
        onRateAnswer?.(question, rating);
    };

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const getQuestionTypeColor = (type?: string) => {
        switch (type) {
            case 'behavioral':
                return 'text-blue-600 dark:text-blue-400';
            case 'technical':
                return 'text-purple-600 dark:text-purple-400';
            case 'situational':
                return 'text-green-600 dark:text-green-400';
            default:
                return 'text-gray-600 dark:text-gray-400';
        }
    };

    if (answers.length === 0 && !isGenerating) {
        return (
            <div className="w-full rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
                <div className="mb-4 flex items-center justify-between">
                    <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                        Answer Suggestions
                    </h2>
                    <div className="text-sm text-zinc-500 dark:text-zinc-400">
                        {answers.length} answers
                    </div>
                </div>

                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="mb-4 rounded-full bg-zinc-100 p-3 dark:bg-zinc-800">
                        <svg className="h-6 w-6 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                        </svg>
                    </div>
                    <p className="text-zinc-500 dark:text-zinc-400 max-w-md">
                        When a question is detected, AI-generated answer suggestions will appear here to help guide your response.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                    Answer Suggestions
                </h2>
                <div className="text-sm text-zinc-500 dark:text-zinc-400">
                    {answers.length} answers
                </div>
            </div>

            {isGenerating && (
                <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-900 dark:bg-blue-950">
                    <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                            <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
                            <span className="text-blue-700 dark:text-blue-300 font-medium">
                                {streamingAnswer ? 'Streaming answer...' : temporaryAnswer ? 'Finding best answer...' : 'Generating answer...'}
                            </span>
                        </div>
                        {onStopGenerating && (
                            <button
                                onClick={onStopGenerating}
                                className="flex items-center gap-2 rounded bg-red-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-600 transition-colors"
                                title="Stop generating"
                            >
                                <XIcon className="h-4 w-4" />
                                Stop
                            </button>
                        )}
                    </div>

                    {/* Show streaming question if available */}
                    {streamingQuestion && (
                        <div className="mt-3">
                            <span className="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wide">
                                Question
                            </span>
                            <p className="mt-1 text-sm font-medium text-blue-900 dark:text-blue-100">
                                {streamingQuestion}
                            </p>
                        </div>
                    )}

                    {/* Show streaming answer as it arrives */}
                    {streamingAnswer ? (
                        <div className="mt-3 rounded border border-green-300 bg-green-50 p-3 dark:border-green-800 dark:bg-green-950">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-xs font-medium text-green-700 dark:text-green-300 uppercase tracking-wide">
                                    Suggested Answer
                                </span>
                                <span className="inline-block h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                            </div>
                            <p className="whitespace-pre-wrap text-sm text-green-900 dark:text-green-100 leading-relaxed">
                                {highlightPlaceholders(streamingAnswer)}
                            </p>
                        </div>
                    ) : temporaryAnswer ? (
                        <div className="mt-3 rounded border border-blue-300 bg-blue-100 p-3 dark:border-blue-800 dark:bg-blue-900">
                            <p className="text-sm text-blue-800 dark:text-blue-200 italic">
                                {highlightPlaceholders(temporaryAnswer)}
                            </p>
                        </div>
                    ) : (
                        <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-blue-100 dark:bg-blue-900">
                            <div className="h-full w-1/3 animate-pulse rounded-full bg-blue-500"></div>
                        </div>
                    )}
                </div>
            )}

            {answers.map((answer, index) => {
                const isExpanded = expandedAnswers.has(index);
                const isCopied = copiedAnswer === index;
                const rating = ratedAnswers.get(answer.question);
                const shouldTruncate = answer.answer.length > 300;

                return (
                    <div
                        key={index}
                        className={`rounded-lg border bg-white p-4 transition-all dark:bg-zinc-900 ${answer.isRegenerating
                                ? 'border-yellow-200 dark:border-yellow-800'
                                : 'border-zinc-200 dark:border-zinc-800'
                            }`}
                    >
                        {answer.isRegenerating && (
                            <div className="mb-3 flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400">
                                <RefreshCwIcon className="h-4 w-4 animate-spin" />
                                Regenerating answer...
                            </div>
                        )}

                        <div className="mb-3">
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex-1">
                                    <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
                                        Question Detected
                                    </span>
                                    {answer.questionType && (
                                        <span className={`ml-2 text-xs font-medium ${getQuestionTypeColor(answer.questionType)}`}>
                                            {answer.questionType}
                                        </span>
                                    )}
                                </div>
                                <span className="text-xs text-zinc-500 dark:text-zinc-400">
                                    {formatTime(answer.timestamp)}
                                </span>
                            </div>
                            <p className="mt-1 font-medium text-zinc-900 dark:text-zinc-100">
                                {answer.question}
                            </p>
                        </div>

                        <div className="border-t border-zinc-100 pt-3 dark:border-zinc-800">
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs font-medium text-green-600 dark:text-green-400 uppercase tracking-wide">
                                        Suggested Answer
                                    </span>
                                    {answer.source && (
                                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                                            answer.source === 'uploaded'
                                                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                                                : 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
                                        }`}>
                                            {answer.source === 'uploaded' ? '⚡ Pre-loaded' : '🤖 AI Generated'}
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center gap-1">
                                    <button
                                        onClick={() => copyToClipboard(answer.answer, index)}
                                        className="rounded p-1 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
                                        title="Copy answer"
                                    >
                                        {isCopied ? (
                                            <CheckIcon className="h-4 w-4 text-green-500" />
                                        ) : (
                                            <CopyIcon className="h-4 w-4" />
                                        )}
                                    </button>
                                    {onRegenerate && (
                                        <button
                                            onClick={() => onRegenerate(answer.question)}
                                            className="rounded p-1 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
                                            title="Regenerate answer"
                                        >
                                            <RefreshCwIcon className="h-4 w-4" />
                                        </button>
                                    )}
                                </div>
                            </div>

                            <div className="mt-2">
                                <p className={`whitespace-pre-wrap text-zinc-700 dark:text-zinc-300 leading-relaxed ${shouldTruncate && !isExpanded ? 'line-clamp-3' : ''
                                    }`}>
                                    {highlightPlaceholders(answer.answer)}
                                </p>

                                {shouldTruncate && (
                                    <button
                                        onClick={() => toggleExpanded(index)}
                                        className="mt-2 text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                                    >
                                        {isExpanded ? 'Show less' : 'Show more'}
                                    </button>
                                )}
                            </div>

                            {/* Show tip for placeholder answers if AI Generator not purchased */}
                            {answer.hasPlaceholder && !aiGeneratorAvailable && (
                                <div className="mt-3 rounded-lg bg-blue-50 border border-blue-200 p-3 dark:bg-blue-950 dark:border-blue-800">
                                    <p className="text-sm text-blue-700 dark:text-blue-300">
                                        💡 Want personalized answers?{' '}
                                        <a
                                            href="/pricing"
                                            className="font-medium underline hover:text-blue-800 dark:hover:text-blue-200"
                                        >
                                            Try our AI Q&A Generator!
                                        </a>
                                    </p>
                                </div>
                            )}

                            {onRateAnswer && (
                                <div className="mt-3 flex items-center gap-2">
                                    <span className="text-xs text-zinc-500 dark:text-zinc-400">Was this helpful?</span>
                                    <button
                                        onClick={() => rateAnswer(answer.question, 'up')}
                                        className={`rounded p-1 transition-colors ${rating === 'up'
                                                ? 'text-green-600 dark:text-green-400'
                                                : 'text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300'
                                            }`}
                                        title="Helpful"
                                    >
                                        <ThumbsUpIcon className="h-4 w-4" />
                                    </button>
                                    <button
                                        onClick={() => rateAnswer(answer.question, 'down')}
                                        className={`rounded p-1 transition-colors ${rating === 'down'
                                                ? 'text-red-600 dark:text-red-400'
                                                : 'text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300'
                                            }`}
                                        title="Not helpful"
                                    >
                                        <ThumbsDownIcon className="h-4 w-4" />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}