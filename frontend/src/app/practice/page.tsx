'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { useWebSocket } from '@/hooks/useWebSocket';
import { AudioLevelIndicator } from '@/components/interview/AudioLevelIndicator';
import { TranscriptionDisplay } from '@/components/interview/TranscriptionDisplay';
import { AnswerDisplay } from '@/components/interview/AnswerDisplay';
import { RecordingControls } from '@/components/interview/RecordingControls';

interface Answer {
    question: string;
    answer: string;
    timestamp: Date;
}

interface StarStory {
    id: string;
    title: string;
    situation: string;
    task: string;
    action: string;
    result: string;
    tags: string[];
}

const WS_URL = 'ws://localhost:8000/ws/transcribe';
const API_URL = 'http://localhost:8000';
const USER_ID = 'heejin';

export default function PracticePage() {
    const [currentText, setCurrentText] = useState('');
    const [accumulatedText, setAccumulatedText] = useState('');
    const [answers, setAnswers] = useState<Answer[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [sessionTime, setSessionTime] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [starStories, setStarStories] = useState<StarStory[]>([]);
    const [contextLoaded, setContextLoaded] = useState(false);
    const [processingState, setProcessingState] = useState<'idle' | 'transcribing' | 'detecting' | 'generating'>('idle');

    // WebSocket connection
    const {
        isConnected,
        connect,
        disconnect,
        sendAudio,
        sendContext,
        requestAnswer,
        clearSession,
        finalizeAudio,
    } = useWebSocket({
        url: WS_URL,
        onTranscription: (text, accumulated) => {
            setCurrentText(text);
            setAccumulatedText(accumulated);
            setProcessingState('idle');
        },
        onQuestionDetected: (question, type) => {
            setIsGenerating(true);
            setProcessingState('generating');
        },
        onAnswer: (question, answer) => {
            setAnswers(prev => [{
                question,
                answer,
                timestamp: new Date(),
            }, ...prev]);
            setIsGenerating(false);
            setProcessingState('idle');
            setAccumulatedText('');
        },
        onError: (message) => {
            setError(message);
            setIsGenerating(false);
        },
        onConnectionChange: (connected) => {
            console.log('Connection status:', connected);
        },
    });

    // Handle silence detection
    const handleSilenceDetected = useCallback(() => {
        console.log('Silence detected in practice page, finalizing audio');
        finalizeAudio();
    }, [finalizeAudio]);

    // Audio recorder
    const {
        isRecording,
        isPaused,
        audioLevel,
        error: recordingError,
        startRecording,
        stopRecording,
        pauseRecording,
        resumeRecording,
    } = useAudioRecorder({
        onAudioData: sendAudio,
        onSilenceDetected: handleSilenceDetected,
        chunkInterval: 1000,
        sampleRate: 16000,
        silenceThreshold: 5,
        silenceDuration: 800,
    });

    // Fetch STAR stories on mount
    useEffect(() => {
        const fetchContext = async () => {
            try {
                const response = await fetch(`${API_URL}/api/profile/context/${USER_ID}`);
                if (response.ok) {
                    const data = await response.json();
                    setStarStories(data.star_stories || []);
                    setContextLoaded(true);
                }
            } catch (err) {
                console.error('Failed to fetch user context:', err);
            }
        };
        fetchContext();
    }, []);

    // Send context when connected
    useEffect(() => {
        if (isConnected && contextLoaded) {
            sendContext({
                resume_text: '',
                star_stories: starStories,
                talking_points: []
            });
        }
    }, [isConnected, contextLoaded, starStories, sendContext]);

    // Session timer
    useEffect(() => {
        let interval: NodeJS.Timeout | null = null;

        if (isRecording && !isPaused) {
            interval = setInterval(() => {
                setSessionTime(prev => prev + 1);
            }, 1000);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [isRecording, isPaused]);

    // Format time
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // Handle start
    const handleStart = async () => {
        setError(null);
        await startRecording();
    };

    // Handle stop
    const handleStop = () => {
        stopRecording();
    };

    // Handle clear
    const handleClear = () => {
        setCurrentText('');
        setAccumulatedText('');
        setAnswers([]);
        setSessionTime(0);
        setError(null);
        clearSession();
    };

    // Handle regenerate
    const handleRegenerate = useCallback((question: string) => {
        setIsGenerating(true);
        requestAnswer(question);
    }, [requestAnswer]);

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-black">
            {/* Header */}
            <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
                <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
                    <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
                        Interview Practice
                    </h1>
                    <div className="flex items-center gap-4">
                        <div className="text-2xl font-mono text-zinc-700 dark:text-zinc-300">
                            {formatTime(sessionTime)}
                        </div>
                        <div className="flex items-center gap-2">
                            <div
                                className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'
                                    }`}
                            />
                            <span className="text-sm text-zinc-500 dark:text-zinc-400">
                                {isConnected ? 'Connected' : 'Disconnected'}
                            </span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main content */}
            <main className="mx-auto max-w-6xl px-4 py-6">
                {/* Error display */}
                {(error || recordingError) && (
                    <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700 dark:bg-red-950 dark:text-red-300">
                        {error || recordingError}
                    </div>
                )}

                {/* Recording controls and audio level */}
                <div className="mb-6 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
                    <div className="mb-4">
                        <RecordingControls
                            isRecording={isRecording}
                            isPaused={isPaused}
                            isConnected={isConnected}
                            onStart={handleStart}
                            onStop={handleStop}
                            onPause={pauseRecording}
                            onResume={resumeRecording}
                            onClear={handleClear}
                        />
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="text-sm text-zinc-500 dark:text-zinc-400">
                            Audio Level:
                        </span>
                        <AudioLevelIndicator level={audioLevel} isRecording={isRecording} />
                    </div>
                </div>

                {/* Two column layout */}
                <div className="grid gap-6 lg:grid-cols-2">
                    {/* Left: Transcription */}
                    <div>
                        <TranscriptionDisplay
                            currentText={currentText}
                            accumulatedText={accumulatedText}
                            isProcessing={isRecording}
                            processingState={processingState}
                        />
                    </div>

                    {/* Right: Answer suggestions */}
                    <div>
                        <AnswerDisplay
                            answers={answers}
                            isGenerating={isGenerating}
                            onRegenerate={handleRegenerate}
                        />
                    </div>
                </div>

                {/* Context Status */}
                {contextLoaded && (
                    <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-950">
                        <p className="text-sm text-green-700 dark:text-green-300">
                            {starStories.length > 0
                                ? `${starStories.length} STAR stories loaded for personalized answers`
                                : 'No STAR stories found. Add some at /profile/stories for personalized answers'}
                        </p>
                    </div>
                )}

                {/* Instructions */}
                <div className="mt-4 rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-900">
                    <h3 className="mb-2 font-medium text-zinc-900 dark:text-zinc-100">
                        How to use
                    </h3>
                    <ol className="list-inside list-decimal space-y-1 text-sm text-zinc-600 dark:text-zinc-400">
                        <li>Click &quot;Start Recording&quot; to begin your practice session</li>
                        <li>Speak interview questions (or have someone ask you)</li>
                        <li>The system will transcribe audio in real-time</li>
                        <li>When a question is detected, an AI-generated answer suggestion will appear</li>
                        <li>Use suggestion as a guide for your own answer</li>
                        <li>Click &quot;Clear&quot; to reset and start fresh</li>
                    </ol>
                </div>
            </main>
        </div>
    );
}