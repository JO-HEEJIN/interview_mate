'use client';

/**
 * Recording control buttons
 * Enhanced with better visual feedback and connection status
 */

// Inline SVG Icons
const MicIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
    </svg>
);

const MicOffIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.636 5.636L18.364 18.364" />
    </svg>
);

const PauseIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const PlayIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const SquareIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        <rect x="9" y="9" width="6" height="6" />
    </svg>
);

const RotateCcwIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
);

const ScreenShareIcon = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
);

interface RecordingControlsProps {
    isRecording: boolean;
    isPaused: boolean;
    isConnected: boolean;
    disabled?: boolean;
    captureSystemAudio?: boolean;
    isCapturingSystemAudio?: boolean;
    onCaptureSystemAudioChange?: (enabled: boolean) => void;
    onStart: () => void;
    onStop: () => void;
    onPause: () => void;
    onResume: () => void;
    onClear: () => void;
}

export function RecordingControls({
    isRecording,
    isPaused,
    isConnected,
    disabled = false,
    captureSystemAudio = false,
    isCapturingSystemAudio = false,
    onCaptureSystemAudioChange,
    onStart,
    onStop,
    onPause,
    onResume,
    onClear,
}: RecordingControlsProps) {
    return (
        <div className="flex flex-col gap-2 w-full">
            {/* Warning Text */}
            {!isRecording && (
                <div className="flex justify-center w-full">
                    <p className="text-xs text-amber-600 dark:text-amber-500 font-medium animate-pulse">
                        Pressing 'Start Recording' will consume 1 interview credit per session
                    </p>
                </div>
            )}

            {/* System Audio Toggle — only shown when not recording */}
            {!isRecording && onCaptureSystemAudioChange && (
                <div className="flex items-center gap-2 px-1">
                    <button
                        type="button"
                        role="switch"
                        aria-checked={captureSystemAudio}
                        onClick={() => onCaptureSystemAudioChange(!captureSystemAudio)}
                        className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 ${
                            captureSystemAudio ? 'bg-blue-500' : 'bg-zinc-300 dark:bg-zinc-600'
                        }`}
                    >
                        <span
                            className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                                captureSystemAudio ? 'translate-x-4' : 'translate-x-0'
                            }`}
                        />
                    </button>
                    <ScreenShareIcon className="h-4 w-4 text-zinc-500 dark:text-zinc-400" />
                    <span className="text-xs text-zinc-600 dark:text-zinc-400">
                        Capture system audio (Zoom/Meet)
                    </span>
                </div>
            )}

            {/* System Audio Active Indicator — shown during recording when capturing */}
            {isRecording && isCapturingSystemAudio && (
                <div className="flex items-center gap-2 px-1">
                    <span className="relative flex h-2.5 w-2.5">
                        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75" />
                        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-blue-500" />
                    </span>
                    <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
                        Capturing system audio
                    </span>
                </div>
            )}

            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    {!isRecording ? (
                        <button
                            onClick={onStart}
                            disabled={!isConnected || disabled}
                            className={`flex items-center gap-2 rounded-full px-6 py-3 font-medium text-white transition-all transform hover:scale-105 ${
                                isConnected && !disabled
                                    ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/30'
                                    : 'bg-gray-400 cursor-not-allowed'
                            }`}
                            title={
                                !isConnected ? 'Connecting...' :
                                disabled ? 'Loading...' :
                                'Start recording'
                            }
                        >
                            <MicIcon className="h-5 w-5" />
                            {disabled ? 'Loading...' : 'Start Recording'}
                        </button>
                    ) : (
                        <>
                            {isPaused ? (
                                <button
                                    onClick={onResume}
                                    className="flex items-center gap-2 rounded-full bg-green-500 px-6 py-3 font-medium text-white transition-all transform hover:scale-105 hover:bg-green-600 shadow-lg shadow-green-500/30"
                                    title="Resume recording"
                                >
                                    <PlayIcon className="h-5 w-5" />
                                    Resume
                                </button>
                            ) : (
                                <button
                                    onClick={onPause}
                                    className="flex items-center gap-2 rounded-full bg-yellow-500 px-6 py-3 font-medium text-white transition-all transform hover:scale-105 hover:bg-yellow-600 shadow-lg shadow-yellow-500/30"
                                    title="Pause recording"
                                >
                                    <PauseIcon className="h-5 w-5" />
                                    Pause
                                </button>
                            )}

                            <button
                                onClick={onStop}
                                className="flex items-center gap-2 rounded-full bg-zinc-700 px-6 py-3 font-medium text-white transition-all transform hover:scale-105 hover:bg-zinc-800 shadow-lg shadow-zinc-700/30"
                                title="Stop recording"
                            >
                                <SquareIcon className="h-5 w-5" />
                                Stop
                            </button>
                        </>
                    )}

                    <button
                        onClick={onClear}
                        className="rounded-full border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 transition-all hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                        title="Clear session"
                    >
                        Clear
                    </button>
                </div>

                {/* Connection status indicator */}
                <div className="flex items-center gap-2">
                    <div
                        className={`h-3 w-3 rounded-full transition-all ${isConnected
                            ? 'bg-green-500 shadow-lg shadow-green-500/50'
                            : 'bg-red-500 shadow-lg shadow-red-500/50 animate-pulse'
                            }`}
                    />
                    <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                        {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                </div>
            </div>
        </div>
    );
}
