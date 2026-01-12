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
  "description": "InterviewMate is a real-time AI interview assistant that works during actual live video interviews on Zoom, Teams, and Google Meet. Powered by Claude AI for accurate answer generation and Deepgram for ultra-fast speech recognition under 2 seconds.",
  "url": "https://interviewmate.tech",
  "offers": {
    "@type": "Offer",
    "price": "4.00",
    "priceCurrency": "USD",
    "description": "Starting at $4 for 10 interview sessions. Use code LAUNCH50 for 50% off until January 30, 2026.",
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
    "Works during live video interviews on Zoom, Google Meet, Microsoft Teams",
    "Personalized responses based on your resume and experience",
    "2-second response time for instant interview assistance",
    "STAR method answer formatting",
    "Supports behavioral, technical, and HR interviews"
  ],
  "keywords": "real-time interview assistant, AI interview coach, live video interview help, Claude AI, Deepgram, Zoom interview tool, Google Meet interview assistant",
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
