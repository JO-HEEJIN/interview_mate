'use client';

import { ProfileProvider } from '@/contexts/ProfileContext';

interface ProvidersProps {
    children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
    return (
        <ProfileProvider>
            {children}
        </ProfileProvider>
    );
}
