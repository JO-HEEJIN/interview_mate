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
  title: 'InterviewMate - Real-Time AI Interview Assistant for Live Video Calls | Powered by Claude AI & Deepgram',
  description: 'InterviewMate is the most affordable real-time AI interview assistant on the market. Starting at just $0.20 per session with LAUNCH50 discount. Works DURING actual live video interviews on Zoom, Teams, and Google Meet. Powered by Claude AI for accurate answer generation and Deepgram for ultra-fast speech recognition. Get personalized answer suggestions in 2 seconds. Use code LAUNCH50 for 50% off until January 30, 2026.',
  keywords: 'real-time interview assistant, live video interview AI, AI interview coach, Zoom interview tool, Google Meet interview assistant, Claude AI interview, Deepgram transcription, behavioral interview help, STAR method answers, interview copilot, live interview support, job interview AI assistant, video call interview helper, technical interview assistant, HR interview tool, cheap interview assistant, affordable interview AI, budget interview tool',

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
