/**
 * Custom hook for audio recording with Web Audio API
 * Enhanced with better audio processing, error handling, and performance monitoring
 */

import { useState, useRef, useCallback, useEffect } from 'react';

interface UseAudioRecorderOptions {
    onAudioData?: (data: Blob) => void;
    onAudioLevel?: (level: number) => void;
    onSilenceDetected?: () => void;
    sampleRate?: number;
    chunkInterval?: number; // ms
    format?: 'webm' | 'wav';
    silenceThreshold?: number; // Audio level below this is silence
    silenceDuration?: number; // ms of silence to trigger detection
}

interface UseAudioRecorderReturn {
    isRecording: boolean;
    isPaused: boolean;
    audioLevel: number;
    error: string | null;
    startRecording: () => Promise<void>;
    stopRecording: () => void;
    pauseRecording: () => void;
    resumeRecording: () => void;
}

export function useAudioRecorder(options: UseAudioRecorderOptions = {}): UseAudioRecorderReturn {
    const {
        onAudioData,
        onAudioLevel,
        onSilenceDetected,
        sampleRate = 16000,
        chunkInterval = 1000, // Reduced from 3000ms to 1000ms for more frequent processing
        format = 'webm',
        silenceThreshold = 5, // Audio level below this is silence
        silenceDuration = 800, // 800ms of silence triggers detection
    } = options;

    const [isRecording, setIsRecording] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [audioLevel, setAudioLevel] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const mediaStreamRef = useRef<MediaStream | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);
    const animationFrameRef = useRef<number | null>(null);
    const chunkIntervalRef = useRef<NodeJS.Timeout | null>(null);
    const audioWorkletRef = useRef<AudioWorkletNode | null>(null);
    const lastAudioTimeRef = useRef<number>(Date.now());
    const audioChunksCountRef = useRef<number>(0);
    const silenceStartRef = useRef<number | null>(null);
    const lastSilenceDetectionRef = useRef<number>(0);

    // Initialize audio context and worklet for better audio processing
    const initializeAudioContext = useCallback(async (stream: MediaStream) => {
        try {
            audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
                sampleRate,
                latencyHint: 'interactive'
            });

            // Create analyser for level monitoring
            analyserRef.current = audioContextRef.current.createAnalyser();
            analyserRef.current.fftSize = 256;
            analyserRef.current.smoothingTimeConstant = 0.8;

            const source = audioContextRef.current.createMediaStreamSource(stream);
            source.connect(analyserRef.current);

            // Try to use AudioWorklet for better processing if available
            try {
                // Check if audio-processor.js exists
                const response = await fetch('/audio-processor.js');
                if (!response.ok) {
                    throw new Error('Audio processor not found');
                }

                await audioContextRef.current.audioWorklet.addModule('/audio-processor.js');
                audioWorkletRef.current = new AudioWorkletNode(audioContextRef.current, 'audio-processor');
                source.connect(audioWorkletRef.current);
                audioWorkletRef.current.connect(audioContextRef.current.destination);

                audioWorkletRef.current.port.onmessage = (event) => {
                    if (event.data.type === 'audio-level') {
                        setAudioLevel(event.data.level);
                        onAudioLevel?.(event.data.level);
                    }
                };
            } catch (err) {
                console.warn('AudioWorklet not available, falling back to ScriptProcessorNode:', err);

                // Fallback to ScriptProcessorNode
                const bufferSize = 4096;
                const processor = audioContextRef.current.createScriptProcessor(bufferSize, 1, 1);
                source.connect(processor);
                processor.connect(audioContextRef.current.destination);

                processor.onaudioprocess = (event) => {
                    const inputBuffer = event.inputBuffer.getChannelData(0);
                    let sum = 0;
                    for (let i = 0; i < inputBuffer.length; i++) {
                        sum += inputBuffer[i] * inputBuffer[i];
                    }
                    const rms = Math.sqrt(sum / inputBuffer.length);
                    const level = Math.min(100, rms * 200);
                    setAudioLevel(level);
                    onAudioLevel?.(level);
                };
            }
        } catch (err) {
            console.error('Error initializing audio context:', err);
            throw err;
        }
    }, [sampleRate, onAudioLevel]);

    // Analyze audio level using the analyser node
    const analyzeAudioLevel = useCallback(() => {
        if (!analyserRef.current || !isRecording || isPaused) return;

        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);

        // Calculate RMS level
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sum / dataArray.length);
        const level = Math.min(100, (rms / 128) * 100);

        setAudioLevel(level);
        onAudioLevel?.(level);

        // Silence detection
        const now = Date.now();
        if (level < silenceThreshold) {
            // Audio is silent
            if (silenceStartRef.current === null) {
                silenceStartRef.current = now;
            } else {
                const silenceDurationMs = now - silenceStartRef.current;
                // Prevent duplicate detections within 2 seconds
                const timeSinceLastDetection = now - lastSilenceDetectionRef.current;
                if (silenceDurationMs >= silenceDuration && timeSinceLastDetection >= 2000) {
                    console.log(`Silence detected: ${silenceDurationMs}ms`);
                    lastSilenceDetectionRef.current = now;
                    onSilenceDetected?.();
                    silenceStartRef.current = null;
                }
            }
        } else {
            // Audio is active, reset silence timer
            silenceStartRef.current = null;
        }

        animationFrameRef.current = requestAnimationFrame(analyzeAudioLevel);
    }, [isRecording, isPaused, onAudioLevel, onSilenceDetected, silenceThreshold, silenceDuration]);

    // Start recording
    const startRecording = useCallback(async () => {
        try {
            setError(null);

            // Request microphone access with specific constraints
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                },
            });

            mediaStreamRef.current = stream;

            // Initialize audio context for level analysis
            await initializeAudioContext(stream);

            // Set up MediaRecorder with appropriate MIME type
            let mimeType = `audio/${format}`;
            if (format === 'webm') {
                mimeType = 'audio/webm;codecs=opus';
            }

            const recorderOptions = MediaRecorder.isTypeSupported(mimeType)
                ? { mimeType }
                : undefined;

            const mediaRecorder = new MediaRecorder(stream, recorderOptions);

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                // Send any remaining chunks when recording stops
                if (chunksRef.current.length > 0 && onAudioData) {
                    const blob = new Blob(chunksRef.current, { type: mimeType });
                    onAudioData(blob);
                    chunksRef.current = [];
                }
            };

            mediaRecorderRef.current = mediaRecorder;

            // Start recording with small time slices to get frequent data
            mediaRecorder.start(100); // Collect data every 100ms

            setIsRecording(true);
            setIsPaused(false);
            lastAudioTimeRef.current = Date.now();
            audioChunksCountRef.current = 0;

            // Start audio level analysis if not using AudioWorklet
            if (!audioWorkletRef.current) {
                analyzeAudioLevel();
            }

            // Set up chunk sending interval
            chunkIntervalRef.current = setInterval(() => {
                const now = Date.now();
                const timeSinceLastAudio = now - lastAudioTimeRef.current;

                // Warn if no audio data for 5 seconds
                if (timeSinceLastAudio > 5000) {
                    console.warn('No audio data received for 5 seconds');
                }

                if (chunksRef.current.length > 0 && onAudioData) {
                    const blob = new Blob(chunksRef.current, { type: mimeType });
                    onAudioData(blob);
                    chunksRef.current = [];
                    lastAudioTimeRef.current = now;
                    audioChunksCountRef.current++;

                    // Log every 5th chunk to avoid spamming the console
                    if (audioChunksCountRef.current % 5 === 0) {
                        console.log(`Processed ${audioChunksCountRef.current} audio chunks`);
                    }
                }
            }, chunkInterval);

        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to start recording';
            setError(message);
            console.error('Recording error:', err);
        }
    }, [sampleRate, chunkInterval, format, onAudioData, initializeAudioContext, analyzeAudioLevel]);

    // Stop recording
    const stopRecording = useCallback(() => {
        // Stop interval
        if (chunkIntervalRef.current) {
            clearInterval(chunkIntervalRef.current);
            chunkIntervalRef.current = null;
        }

        // Stop animation frame
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
            animationFrameRef.current = null;
        }

        // Stop MediaRecorder
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            try {
                mediaRecorderRef.current.stop();
            } catch (err) {
                console.error('Error stopping MediaRecorder:', err);
            }
        }

        // Send remaining chunks
        if (chunksRef.current.length > 0 && onAudioData) {
            const mimeType = format === 'webm' ? 'audio/webm;codecs=opus' : `audio/${format}`;
            const blob = new Blob(chunksRef.current, { type: mimeType });
            onAudioData(blob);
            chunksRef.current = [];
        }

        // Stop media stream
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(track => {
                try {
                    track.stop();
                } catch (err) {
                    console.error('Error stopping media track:', err);
                }
            });
            mediaStreamRef.current = null;
        }

        // Close AudioContext
        if (audioContextRef.current) {
            try {
                audioContextRef.current.close();
            } catch (err) {
                console.error('Error closing audio context:', err);
            }
            audioContextRef.current = null;
        }

        setIsRecording(false);
        setIsPaused(false);
        setAudioLevel(0);

        console.log(`Recording stopped. Processed ${audioChunksCountRef.current} audio chunks.`);
    }, [format, onAudioData]);

    // Pause recording
    const pauseRecording = useCallback(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            mediaRecorderRef.current.pause();
            setIsPaused(true);
            console.log('Recording paused');
        }
    }, []);

    // Resume recording
    const resumeRecording = useCallback(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
            mediaRecorderRef.current.resume();
            setIsPaused(false);
            lastAudioTimeRef.current = Date.now();

            // Resume audio level analysis if not using AudioWorklet
            if (!audioWorkletRef.current) {
                analyzeAudioLevel();
            }

            console.log('Recording resumed');
        }
    }, [analyzeAudioLevel]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopRecording();
        };
    }, [stopRecording]);

    return {
        isRecording,
        isPaused,
        audioLevel,
        error,
        startRecording,
        stopRecording,
        pauseRecording,
        resumeRecording,
    };
}