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
  title: 'InterviewMate - Real-Time AI for Interview Preparation',
  description: 'Prepare context, practice responses, and get structured AI assistance for high-pressure communication with low-latency speech and retrieval.',
  keywords: 'interview preparation, AI interview practice, interview communication, structured interview responses, speech pipeline, semantic retrieval, interview engineering',

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
