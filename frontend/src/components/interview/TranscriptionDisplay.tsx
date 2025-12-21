'use client';

/**
 * Display for real-time transcription
 * Enhanced with better visual feedback and text highlighting
 */

interface TranscriptionDisplayProps {
    currentText: string;
    accumulatedText: string;
    isProcessing?: boolean;
    processingState?: 'idle' | 'transcribing' | 'detecting' | 'generating';
    onGenerateAnswer?: () => void;
    canGenerate?: boolean;
}

export function TranscriptionDisplay({
    currentText,
    accumulatedText,
    isProcessing = false,
    processingState = 'idle',
    onGenerateAnswer,
    canGenerate = false
}: TranscriptionDisplayProps) {
    const hasContent = accumulatedText.length > 0 || currentText.length > 0;

    const getProcessingLabel = () => {
        switch (processingState) {
            case 'transcribing':
                return 'Transcribing';
            case 'detecting':
                return 'Detecting question';
            case 'generating':
                return 'Generating answer';
            default:
                return 'Processing';
        }
    };

    const getProcessingColor = () => {
        switch (processingState) {
            case 'transcribing':
                return 'bg-blue-500 text-blue-600 dark:text-blue-400';
            case 'detecting':
                return 'bg-yellow-500 text-yellow-600 dark:text-yellow-400';
            case 'generating':
                return 'bg-green-500 text-green-600 dark:text-green-400';
            default:
                return 'bg-blue-500 text-blue-600 dark:text-blue-400';
        }
    };

    return (
        <div className="w-full rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
            <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                    Live Transcription
                </h2>

                {(isProcessing || processingState !== 'idle') && (
                    <div className="flex items-center gap-2">
                        <div className={`h-2 w-2 rounded-full ${getProcessingColor().split(' ')[0]} animate-pulse`}></div>
                        <span className={`text-xs ${getProcessingColor().split(' ').slice(1).join(' ')}`}>
                            {getProcessingLabel()}
                        </span>
                    </div>
                )}
            </div>

            <div className="min-h-[120px] rounded-md border border-zinc-100 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-950">
                {hasContent ? (
                    <div className="space-y-2">
                        {accumulatedText && (
                            <p className="whitespace-pre-wrap text-zinc-700 dark:text-zinc-300 leading-relaxed">
                                {accumulatedText}
                            </p>
                        )}

                        {currentText && (
                            <span className="inline-block text-zinc-900 dark:text-zinc-100 font-medium animate-pulse">
                                {' '}{currentText}
                            </span>
                        )}
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-center py-8">
                        <div className="mb-3 rounded-full bg-zinc-100 p-3 dark:bg-zinc-800">
                            <svg className="h-6 w-6 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                            </svg>
                        </div>
                        <p className="text-zinc-400 dark:text-zinc-600 max-w-md">
                            Start recording to see real-time transcription of the interview questions.
                        </p>
                    </div>
                )}
            </div>

            {hasContent && (
                <div className="mt-3 flex items-center justify-between">
                    <div className="text-xs text-zinc-500 dark:text-zinc-400">
                        {accumulatedText.split(' ').length + currentText.split(' ').length} words
                    </div>

                    {onGenerateAnswer && (
                        <button
                            onClick={onGenerateAnswer}
                            disabled={!canGenerate}
                            className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all ${canGenerate
                                    ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md shadow-blue-500/20'
                                    : 'bg-zinc-100 text-zinc-400 cursor-not-allowed dark:bg-zinc-800 dark:text-zinc-600'
                                }`}
                        >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            Generate Answer
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}