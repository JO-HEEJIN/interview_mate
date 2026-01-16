/**
 * Site-wide configuration
 * Uses environment variables to avoid hardcoding domains
 */

export const siteConfig = {
  // Site URLs
  url: process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000',
  domain: process.env.NEXT_PUBLIC_SITE_DOMAIN || 'interviewmate.tech',

  // Site metadata
  name: process.env.NEXT_PUBLIC_SITE_NAME || 'InterviewMate',
  title: 'InterviewMate - Real-Time AI for Any Interview | Job, PhD, Visa, Admissions',
  description: 'Real-time cheating for any interview. Job interviews, PhD defenses, visa interviews, school admissions - get AI-powered answers in under 2 seconds. Starting at $0.20/session. Works on Zoom, Teams, Google Meet. Use code LAUNCH50 for 50% off.',
  keywords: 'real-time interview assistant, AI interview help, PhD defense assistant, visa interview prep, job interview AI, school admission interview, academic interview help, Zoom interview tool, Google Meet interview, Claude AI, Deepgram transcription, interview copilot, live interview support, video call interview helper, cheap interview assistant, affordable interview AI',

  // API
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',

  // Social/SEO
  twitter: '@interviewmate',

  // Production URLs (computed)
  get productionUrl() {
    return `https://${this.domain}`;
  },

  get apiProductionUrl() {
    return `https://api.${this.domain}`;
  },

  // Helper to get canonical URL
  getCanonicalUrl(path: string = '') {
    const baseUrl = process.env.NODE_ENV === 'production'
      ? this.productionUrl
      : this.url;

    return path ? `${baseUrl}${path.startsWith('/') ? path : `/${path}`}` : baseUrl;
  },

  // Helper for OG images
  getOgImageUrl(image: string = '/og-image.png') {
    return this.getCanonicalUrl(image);
  }
} as const;

export type SiteConfig = typeof siteConfig;
