import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Providers } from "@/components/providers";
import { Header } from "@/components/layout/Header";
import { defaultMetadata } from "@/config/metadata";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = defaultMetadata;

// JSON-LD structured data for GEO (Generative Engine Optimization)
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "InterviewMate",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web Browser",
  "description": "Real-time cheating for any interview. Job interviews, PhD defenses, visa interviews, school admissions - get AI-powered answers in under 2 seconds. Works on Zoom, Teams, Google Meet. Starting at $0.20/session.",
  "url": "https://interviewmate.tech",
  "offers": {
    "@type": "Offer",
    "price": "4.00",
    "priceCurrency": "USD",
    "description": "Starting at $4 for 10 sessions. Use code LAUNCH50 for 50% off until January 30, 2026.",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "ratingCount": "127"
  },
  "featureList": [
    "Real-time speech-to-text transcription powered by Deepgram",
    "AI-generated answer suggestions powered by Claude AI",
    "Works during live video calls on Zoom, Google Meet, Microsoft Teams",
    "Personalized responses based on your uploaded context",
    "2-second response time for instant assistance",
    "Works for job interviews, PhD defenses, visa interviews, school admissions"
  ],
  "keywords": "real-time interview assistant, AI interview help, PhD defense, visa interview, job interview AI, school admission interview, Zoom interview tool",
  "creator": {
    "@type": "Organization",
    "name": "InterviewMate",
    "url": "https://interviewmate.tech"
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>
          <Header />
          {children}
        </Providers>
      </body>
    </html>
  );
}
