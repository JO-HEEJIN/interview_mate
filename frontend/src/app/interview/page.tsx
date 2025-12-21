'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
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
    source?: string;
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

interface QAPair {
    id: string;
    question: string;
    answer: string;
    question_type: string;
    source: string;
    usage_count: number;
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/transcribe';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function PracticePage() {
    const router = useRouter();
    const [userId, setUserId] = useState<string | null>(null);
    const [currentText, setCurrentText] = useState('');
    const [accumulatedText, setAccumulatedText] = useState('');
    const [answers, setAnswers] = useState<Answer[]>([]);
    const [temporaryAnswer, setTemporaryAnswer] = useState<string | null>(null);
    const [streamingAnswer, setStreamingAnswer] = useState<string>('');
    const [streamingQuestion, setStreamingQuestion] = useState<string>('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [sessionTime, setSessionTime] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [starStories, setStarStories] = useState<StarStory[]>([]);
    const [qaPairs, setQaPairs] = useState<QAPair[]>([]);
    const [contextLoaded, setContextLoaded] = useState(false);
    const [processingState, setProcessingState] = useState<'idle' | 'transcribing' | 'detecting' | 'generating'>('idle');

    // Refs to track streaming state (avoids closure issues)
    const streamingAnswerRef = useRef<string>('');
    const streamingQuestionRef = useRef<string>('');

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
            // Just detection, do not auto-generate
            // setIsGenerating(true);
            // setProcessingState('generating');
            console.log('Question detected:', question);
        },
        onTemporaryAnswer: (question, answer) => {
            setTemporaryAnswer(answer);
            setIsGenerating(true);
            setProcessingState('generating');
            setAccumulatedText('');  // Clear when answer generation starts
        },
        onAnswer: (question, answer, source) => {
            setAnswers(prev => [{
                question,
                answer,
                timestamp: new Date(),
                source,
            }, ...prev]);
            setTemporaryAnswer(null);
            streamingAnswerRef.current = '';
            streamingQuestionRef.current = '';
            setStreamingAnswer('');
            setStreamingQuestion('');
            setIsGenerating(false);
            setProcessingState('idle');
            setAccumulatedText('');
        },
        onAnswerStreamStart: (question) => {
            console.log('Streaming answer started for:', question);
            streamingQuestionRef.current = question;
            streamingAnswerRef.current = '';
            setStreamingQuestion(question);
            setStreamingAnswer('');
            setTemporaryAnswer(null);
            setIsGenerating(true);
            setProcessingState('generating');
            setAccumulatedText('');  // Clear immediately when answer generation starts
        },
        onAnswerStreamChunk: (chunk) => {
            streamingAnswerRef.current += chunk;
            setStreamingAnswer(prev => prev + chunk);
        },
        onAnswerStreamEnd: (question) => {
            console.log('Streaming answer completed for:', question);
            // Move streaming answer to final answers using ref (avoids closure issue)
            const finalAnswer = streamingAnswerRef.current;
            const finalQuestion = streamingQuestionRef.current || question;

            if (finalAnswer.trim()) {
                setAnswers(prev => [{
                    question: finalQuestion,
                    answer: finalAnswer,
                    timestamp: new Date(),
                    source: 'streamed',
                }, ...prev]);
            } else {
                console.warn('Streaming ended but answer is empty');
            }

            // Clear refs and state
            streamingAnswerRef.current = '';
            streamingQuestionRef.current = '';
            setStreamingAnswer('');
            setStreamingQuestion('');
            setIsGenerating(false);
            setProcessingState('idle');
            setAccumulatedText('');
        },
        onError: (message) => {
            setError(message);
            setTemporaryAnswer(null);
            streamingAnswerRef.current = '';
            streamingQuestionRef.current = '';
            setStreamingAnswer('');
            setStreamingQuestion('');
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

    // Check authentication on mount
    useEffect(() => {
        const checkAuth = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push('/auth/login');
                return;
            }
            setUserId(session.user.id);
        };
        checkAuth();

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            if (!session) {
                router.push('/auth/login');
            } else {
                setUserId(session.user.id);
            }
        });

        return () => subscription.unsubscribe();
    }, [router]);

    // Fetch user context (STAR stories and Q&A pairs) when userId is available
    useEffect(() => {
        if (!userId) return;

        const fetchAll = async () => {
            try {
                // Fetch both context and Q&A pairs in parallel
                const [contextResponse, qaPairsResponse] = await Promise.all([
                    fetch(`${API_URL}/api/profile/context/${userId}`),
                    fetch(`${API_URL}/api/qa-pairs/${userId}`)
                ]);

                if (contextResponse.ok) {
                    const contextData = await contextResponse.json();
                    setStarStories(contextData.star_stories || []);
                }

                if (qaPairsResponse.ok) {
                    const qaPairsData = await qaPairsResponse.json();
                    setQaPairs(qaPairsData || []);
                    console.log(`Loaded ${qaPairsData?.length || 0} Q&A pairs`);
                }

                // Set contextLoaded only after BOTH are loaded
                setContextLoaded(true);
            } catch (err) {
                console.error('Failed to fetch user context:', err);
            }
        };

        fetchAll();
    }, [userId]);

    // Send context when connected
    useEffect(() => {
        if (isConnected && contextLoaded && userId) {
            sendContext({
                user_id: userId,
                resume_text: '',
                star_stories: starStories,
                talking_points: [],
                qa_pairs: qaPairs
            });
        }
    }, [isConnected, contextLoaded, userId, starStories, qaPairs, sendContext]);

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
    // Handle clear
    const handleClear = async () => {
        const wasRecording = isRecording;

        // 1. Stop recording first to flush final data
        if (wasRecording) {
            stopRecording();
            // Wait for data to flush
            await new Promise(resolve => setTimeout(resolve, 200));
        }

        // 2. Clear backend session (safe now, no more chunks from old stream)
        clearSession();

        // 3. Reset local state
        setCurrentText('');
        setAccumulatedText('');
        setAnswers([]);
        setSessionTime(0);
        setError(null);

        // 4. Restart recording if it was active
        if (wasRecording) {
            // Small buffer before starting new
            await new Promise(resolve => setTimeout(resolve, 100));
            await startRecording();
        }
    };

    // Handle regenerate
    const handleRegenerate = useCallback((question: string) => {
        setIsGenerating(true);
        requestAnswer(question);
    }, [requestAnswer]);

    // Handle stop generating
    const handleStopGenerating = useCallback(() => {
        setIsGenerating(false);
        console.log('Answer generation stopped by user');
    }, []);

    // Handle manual answer generation
    const handleManualGenerate = useCallback(() => {
        if (accumulatedText.trim()) {
            console.log('Manually requesting answer for:', accumulatedText);
            setIsGenerating(true);
            setProcessingState('generating');
            requestAnswer(accumulatedText);
        }
    }, [accumulatedText, requestAnswer]);

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
                            onGenerateAnswer={handleManualGenerate}
                            canGenerate={isPaused && accumulatedText.length > 0 && !isGenerating}
                        />
                    </div>

                    {/* Right: Answer suggestions */}
                    <div>
                        <AnswerDisplay
                            answers={answers}
                            isGenerating={isGenerating}
                            temporaryAnswer={temporaryAnswer}
                            streamingAnswer={streamingAnswer}
                            streamingQuestion={streamingQuestion}
                            onRegenerate={handleRegenerate}
                            onStopGenerating={handleStopGenerating}
                        />
                    </div>
                </div>

                {/* Instructions */}
                <div className="mt-4 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
                    <h3 className="mb-2 font-medium text-blue-900 dark:text-blue-100">
                        How to use (Manual Control)
                    </h3>
                    <ol className="list-inside list-decimal space-y-2 text-sm text-blue-800 dark:text-blue-200">
                        <li><strong>Start Recording</strong> - Begin recording session</li>
                        <li><strong>Speak your question</strong> - Audio will be transcribed in real-time</li>
                        <li><strong>Pause</strong> when finished speaking - This enables answer generation</li>
                        <li><strong>Click "Generate Answer"</strong> - Get AI-powered feedback</li>
                        <li><strong>Resume</strong> to continue the interview</li>
                        <li><strong>Clear</strong> to reset everything</li>
                    </ol>
                    <div className="mt-3 rounded bg-blue-100 dark:bg-blue-900 p-2 text-xs text-blue-700 dark:text-blue-300">
                        <strong>Tip:</strong> Pause during questions, Resume to process. This gives you control and better accuracy.
                    </div>
                </div>
            </main>
        </div>
    );
}