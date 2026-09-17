import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Pricing | InterviewMate',
  description:
    'Start with 30 free practice sessions. Pay-as-you-go session credits that never expire, with no subscription.',
  alternates: { canonical: '/pricing' },
};

export default function PricingLayout({ children }: { children: React.ReactNode }) {
  return children;
}
