'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useUserFeatures } from '@/hooks/useUserFeatures';
import { useProfile } from '@/contexts/ProfileContext';
import { AudioLevelIndicator } from '@/components/interview/AudioLevelIndicator';
import { TranscriptionDisplay } from '@/components/interview/TranscriptionDisplay';
import { AnswerDisplay } from '@/components/interview/AnswerDisplay';
import { RecordingControls } from '@/components/interview/RecordingControls';

interface Answer {
    question: string;
    answer: string;
    timestamp: Date;
    source?: string;
    hasPlaceholder?: boolean;
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

    // Profile context
    const { activeProfile, isLoading: profileLoading } = useProfile();

    // Feature gating - check interview credits and AI generator
    const { interview_credits, ai_generator_available, isLoading: featuresLoading } = useUserFeatures(userId);
    const hasCredits = interview_credits > 0;

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
    const [captureSystemAudio, setCaptureSystemAudio] = useState<boolean>(() => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('captureSystemAudio') === 'true';
        }
        return false;
    });
    const [systemAudioError, setSystemAudioError] = useState<string | null>(null);

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
        notifyStartRecording,
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
        onAnswerStreamEnd: (question, hasPlaceholder) => {
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
                    hasPlaceholder: hasPlaceholder || false,
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
        onCreditConsumed: (remainingCredits) => {
            console.log('Credit consumed, remaining:', remainingCredits);
        },
        onNoCredits: () => {
            setError('No interview credits available. Please purchase more credits.');
            stopRecording();
            router.push('/pricing');
        },
    });

    // System audio handlers
    const handleCaptureSystemAudioChange = useCallback((enabled: boolean) => {
        setCaptureSystemAudio(enabled);
        localStorage.setItem('captureSystemAudio', String(enabled));
    }, []);

    const handleSystemAudioError = useCallback((error: string) => {
        setSystemAudioError(error);
        setTimeout(() => setSystemAudioError(null), 5000);
    }, []);

    const handleSystemAudioStopped = useCallback(() => {
        setSystemAudioError('System audio sharing stopped. Continuing with microphone only.');
        setTimeout(() => setSystemAudioError(null), 5000);
    }, []);

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
        isCapturingSystemAudio,
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
        captureSystemAudio,
        onSystemAudioError: handleSystemAudioError,
        onSystemAudioStopped: handleSystemAudioStopped,
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

    // Fetch user context (STAR stories and Q&A pairs) when userId and profile are available
    useEffect(() => {
        if (!userId || !activeProfile) return;

        const fetchAll = async () => {
            try {
                // Build URLs with profile_id
                const contextUrl = new URL(`${API_URL}/api/profile/context/${userId}`);
                contextUrl.searchParams.set('profile_id', activeProfile.id);

                const qaPairsUrl = new URL(`${API_URL}/api/qa-pairs/${userId}`);
                qaPairsUrl.searchParams.set('profile_id', activeProfile.id);

                // Fetch both context and Q&A pairs in parallel
                const [contextResponse, qaPairsResponse] = await Promise.all([
                    fetch(contextUrl.toString()),
                    fetch(qaPairsUrl.toString())
                ]);

                if (contextResponse.ok) {
                    const contextData = await contextResponse.json();
                    setStarStories(contextData.star_stories || []);
                }

                if (qaPairsResponse.ok) {
                    const qaPairsData = await qaPairsResponse.json();
                    setQaPairs(qaPairsData || []);
                    console.log(`Loaded ${qaPairsData?.length || 0} Q&A pairs for profile ${activeProfile.profile_name}`);
                }

                // Set contextLoaded only after BOTH are loaded
                setContextLoaded(true);
            } catch (err) {
                console.error('Failed to fetch user context:', err);
            }
        };

        fetchAll();
    }, [userId, activeProfile]);

    // Send context when connected
    useEffect(() => {
        if (isConnected && contextLoaded && userId && activeProfile) {
            sendContext({
                user_id: userId,
                profile_id: activeProfile.id,
                resume_text: '',
                star_stories: starStories,
                talking_points: [],
                qa_pairs: qaPairs
            });
        }
    }, [isConnected, contextLoaded, userId, activeProfile, starStories, qaPairs, sendContext]);

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
        // Wait for features to load before checking credits
        if (featuresLoading) {
            console.log('Still loading user features, please wait...');
            return;
        }

        // Redirect to pricing if no credits
        if (!hasCredits) {
            router.push('/pricing');
            return;
        }
        setError(null);
        await startRecording();
        // Notify backend to consume credit when recording actually starts
        notifyStartRecording();
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
        // Clear previous answer immediately for fast UI response
        setTemporaryAnswer(null);
        setStreamingAnswer('');
        setStreamingQuestion('');
        streamingAnswerRef.current = '';
        streamingQuestionRef.current = '';

        // Start new generation
        setIsGenerating(true);
        setProcessingState('generating');
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

    // Show message if no profile is selected
    if (!profileLoading && !activeProfile) {
        return (
            <div className="min-h-screen bg-zinc-50 dark:bg-black">
                <div className="mx-auto max-w-4xl px-4 py-6">
                    <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 dark:border-amber-800 dark:bg-amber-950">
                        <h2 className="text-lg font-semibold text-amber-900 dark:text-amber-100">
                            No Profile Selected
                        </h2>
                        <p className="mt-2 text-amber-700 dark:text-amber-300">
                            Please create or select a profile before starting an interview practice session.
                        </p>
                        <button
                            onClick={() => router.push('/profile/manage')}
                            className="mt-4 rounded-lg bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700"
                        >
                            Manage Profiles
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-black">
            {/* Header */}
            <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
                <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
                    <div>
                        {/* Profile Indicator */}
                        {activeProfile && (
                            <div className="mb-1 flex items-center gap-2">
                                <div className="flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-bold text-white">
                                    {activeProfile.profile_name.charAt(0).toUpperCase()}
                                </div>
                                <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
                                    {activeProfile.profile_name}
                                </span>
                            </div>
                        )}
                        <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
                            Interview Practice
                        </h1>
                    </div>
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

                {/* System audio warning */}
                {systemAudioError && (
                    <div className="mb-4 rounded-lg bg-amber-50 p-4 text-amber-700 dark:bg-amber-950 dark:text-amber-300">
                        {systemAudioError}
                    </div>
                )}

                {/* Credits Display */}
                {!featuresLoading && (
                    <div className="mb-4 text-sm text-zinc-500 dark:text-zinc-400">
                        Credits remaining: <span className="font-medium text-zinc-700 dark:text-zinc-300">{interview_credits}</span>
                    </div>
                )}

                {/* Recording controls and audio level */}
                <div className="mb-6 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
                    <div className="mb-4">
                        <RecordingControls
                            isRecording={isRecording}
                            isPaused={isPaused}
                            isConnected={isConnected}
                            disabled={featuresLoading}
                            captureSystemAudio={captureSystemAudio}
                            isCapturingSystemAudio={isCapturingSystemAudio}
                            onCaptureSystemAudioChange={handleCaptureSystemAudioChange}
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
                            aiGeneratorAvailable={ai_generator_available}
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