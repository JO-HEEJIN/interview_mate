'use client';

/**
 * Visual indicator for audio input level
 * Enhanced with better visual feedback and color gradients
 */

interface AudioLevelIndicatorProps {
    level: number; // 0-100
    isRecording: boolean;
    isPaused?: boolean;
}

export function AudioLevelIndicator({ level, isRecording, isPaused = false }: AudioLevelIndicatorProps) {
    const bars = 20;
    const activeBarCount = Math.round((level / 100) * bars);

    const getBarColor = (index: number, isActive: boolean) => {
        if (!isRecording || isPaused) {
            return 'bg-zinc-300 dark:bg-zinc-700';
        }

        if (!isActive) {
            return 'bg-zinc-300 dark:bg-zinc-700';
        }

        const intensity = index / bars;

        if (intensity < 0.5) {
            return 'bg-green-500';
        } else if (intensity < 0.7) {
            return 'bg-yellow-500';
        } else if (intensity < 0.85) {
            return 'bg-orange-500';
        } else {
            return 'bg-red-500';
        }
    };

    const getBarHeight = (index: number) => {
        // Create a gradient effect with increasing height
        const minHeight = 4;
        const maxHeight = 32;
        const increment = (maxHeight - minHeight) / bars;
        return minHeight + (index * increment);
    };

    return (
        <div className="flex items-center justify-center gap-1 h-10">
            {Array.from({ length: bars }).map((_, i) => {
                const isActive = i < activeBarCount;
                const colorClass = getBarColor(i, isActive);
                const height = getBarHeight(i);

                return (
                    <div
                        key={i}
                        className={`w-1.5 rounded-full transition-all duration-100 ${colorClass}`}
                        style={{
                            height: `${height}px`,
                            opacity: isActive ? 1 : 0.4,
                            boxShadow: isActive && isRecording && !isPaused
                                ? `0 0 ${4 + (i / bars) * 4}px ${colorClass.replace('bg-', '').replace('-500', '').replace('-400', '')}`
                                : 'none',
                        }}
                    />
                );
            })}
        </div>
    );
}