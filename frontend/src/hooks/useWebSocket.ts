/**
 * Custom hook for WebSocket connection to transcription service
 */

import { useState, useRef, useCallback, useEffect } from 'react';

interface UseWebSocketOptions {
    url: string;
    onTranscription?: (text: string, accumulated: string) => void;
    onQuestionDetected?: (question: string, type: string) => void;
    onTemporaryAnswer?: (question: string, answer: string) => void;
    onAnswer?: (question: string, answer: string, source?: string) => void;
    onAnswerStreamStart?: (question: string) => void;
    onAnswerStreamChunk?: (chunk: string) => void;
    onAnswerStreamEnd?: (question: string) => void;
    onError?: (message: string) => void;
    onConnectionChange?: (connected: boolean) => void;
    onCreditConsumed?: (remainingCredits: number) => void;
    onNoCredits?: () => void;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    connect: () => void;
    disconnect: () => void;
    sendAudio: (data: Blob) => void;
    sendContext: (context: { user_id?: string; resume_text: string; star_stories: any[]; talking_points: any[]; qa_pairs?: any[] }) => void;
    requestAnswer: (question: string, question_type?: string) => void;
    clearSession: () => void;
    finalizeAudio: () => void;
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
    const {
        url,
        onTranscription,
        onQuestionDetected,
        onTemporaryAnswer,
        onAnswer,
        onAnswerStreamStart,
        onAnswerStreamChunk,
        onAnswerStreamEnd,
        onError,
        onConnectionChange,
    } = options;

    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);

    const handleMessage = useCallback((event: MessageEvent) => {
        try {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'transcription':
                    onTranscription?.(data.text, data.accumulated_text);
                    break;
                case 'question_detected':
                    onQuestionDetected?.(data.question, data.question_type);
                    break;
                case 'answer_temporary':
                    onTemporaryAnswer?.(data.question, data.answer);
                    break;
                case 'answer':
                    onAnswer?.(data.question, data.answer, data.source);
                    break;
                case 'answer_stream_start':
                    onAnswerStreamStart?.(data.question);
                    break;
                case 'answer_stream_chunk':
                    onAnswerStreamChunk?.(data.chunk);
                    break;
                case 'answer_stream_end':
                    onAnswerStreamEnd?.(data.question);
                    break;
                case 'error':
                    onError?.(data.message);
                    break;
            }
        } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
        }
    }, [onTranscription, onQuestionDetected, onTemporaryAnswer, onAnswer, onAnswerStreamStart, onAnswerStreamChunk, onAnswerStreamEnd, onError]);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            console.log('WebSocket already connected');
            return;
        }

        try {
            console.log('Connecting to WebSocket:', url);
            const ws = new WebSocket(url);

            ws.onopen = () => {
                console.log('WebSocket connected successfully');
                setIsConnected(true);
                onConnectionChange?.(true);
            };

            ws.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                setIsConnected(false);
                onConnectionChange?.(false);

                // Auto-reconnect after 3 seconds in development
                if (event.code !== 1000) { // 1000 = normal closure
                    console.log('Attempting to reconnect in 3 seconds...');
                    setTimeout(() => {
                        if (wsRef.current?.readyState !== WebSocket.OPEN) {
                            connect();
                        }
                    }, 3000);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error details:', {
                    error,
                    readyState: ws.readyState,
                    url: url,
                    timestamp: new Date().toISOString()
                });
                onError?.('WebSocket connection failed. Please check if backend is running on port 8000');
            };

            ws.onmessage = handleMessage;

            wsRef.current = ws;
        } catch (err) {
            console.error('Failed to create WebSocket:', err);
            onError?.(`Failed to connect to server: ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
    }, [url, handleMessage, onConnectionChange, onError]);

    const disconnect = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsConnected(false);
    }, []);

    const sendAudio = useCallback(async (data: Blob) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            const arrayBuffer = await data.arrayBuffer();
            wsRef.current.send(arrayBuffer);
        }
    }, []);

    const sendContext = useCallback((context: { resume_text: string; star_stories: any[]; talking_points: any[]; qa_pairs?: any[] }) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'context',
                ...context,
            }));
        }
    }, []);

    const requestAnswer = useCallback((question: string, question_type: string = 'general') => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'generate_answer',
                question,
                question_type,
            }));
        }
    }, []);

    const clearSession = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'clear',
            }));
        }
    }, []);

    const finalizeAudio = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'finalize',
            }));
        }
    }, []);

    useEffect(() => {
        connect();
        return () => {
            disconnect();
        };
    }, []);

    return {
        isConnected,
        connect,
        disconnect,
        sendAudio,
        sendContext,
        requestAnswer,
        clearSession,
        finalizeAudio,
    };
}