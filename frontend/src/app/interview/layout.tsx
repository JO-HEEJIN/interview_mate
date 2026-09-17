import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Practice Session | InterviewMate',
  description:
    'Run a timed mock interview session with real-time transcription and personalized response suggestions.',
  alternates: { canonical: '/interview' },
};

export default function PracticeSessionLayout({ children }: { children: React.ReactNode }) {
  return children;
}
