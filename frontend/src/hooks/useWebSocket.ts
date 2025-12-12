/**
 * Custom hook for WebSocket connection to transcription service
 */

import { useState, useRef, useCallback, useEffect } from 'react';

interface UseWebSocketOptions {
    url: string;
    onTranscription?: (text: string, accumulated: string) => void;
    onQuestionDetected?: (question: string, type: string) => void;
    onAnswer?: (question: string, answer: string) => void;
    onError?: (message: string) => void;
    onConnectionChange?: (connected: boolean) => void;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    connect: () => void;
    disconnect: () => void;
    sendAudio: (data: Blob) => void;
    sendContext: (context: { resume_text: string; star_stories: any[]; talking_points: any[] }) => void;
    requestAnswer: (question: string) => void;
    clearSession: () => void;
    finalizeAudio: () => void;
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
    const {
        url,
        onTranscription,
        onQuestionDetected,
        onAnswer,
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
                case 'answer':
                    onAnswer?.(data.question, data.answer);
                    break;
                case 'error':
                    onError?.(data.message);
                    break;
            }
        } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
        }
    }, [onTranscription, onQuestionDetected, onAnswer, onError]);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            const ws = new WebSocket(url);

            ws.onopen = () => {
                setIsConnected(true);
                onConnectionChange?.(true);
            };

            ws.onclose = () => {
                setIsConnected(false);
                onConnectionChange?.(false);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                onError?.('WebSocket connection error');
            };

            ws.onmessage = handleMessage;

            wsRef.current = ws;
        } catch (err) {
            console.error('Failed to connect WebSocket:', err);
            onError?.('Failed to connect to server');
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

    const sendContext = useCallback((context: { resume_text: string; star_stories: any[]; talking_points: any[] }) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'context',
                ...context,
            }));
        }
    }, []);

    const requestAnswer = useCallback((question: string) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'generate_answer',
                question,
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