/**
 * Site metadata configuration
 * Generates Next.js metadata using environment variables
 */

import { Metadata } from 'next';
import { siteConfig } from './site';

export const defaultMetadata: Metadata = {
  title: siteConfig.title,
  description: siteConfig.description,
  keywords: siteConfig.keywords,
  authors: [{ name: 'InterviewMate Team' }],
  creator: 'InterviewMate',
  publisher: 'InterviewMate',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/best.jpg',
    apple: '/best.jpg',
    shortcut: '/best.jpg',
  },
  manifest: '/manifest.json',
  openGraph: {
    title: siteConfig.title,
    description: siteConfig.description,
    url: siteConfig.productionUrl,
    siteName: siteConfig.name,
    images: [
      {
        url: siteConfig.getOgImageUrl('/best.jpg'),
        width: 1200,
        height: 630,
        alt: siteConfig.name,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: siteConfig.title,
    description: siteConfig.description,
    images: [siteConfig.getOgImageUrl('/best.jpg')],
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#000000' },
  ],
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: siteConfig.name,
  },
  metadataBase: new URL(siteConfig.productionUrl),
};
