import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Providers } from "@/components/providers";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
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
  "description": "Prepare context, practice responses, and get structured AI assistance for high-pressure communication with low-latency speech and retrieval.",
  "url": "https://interviewmate.tech",
  "offers": {
    "@type": "Offer",
    "price": "10.00",
    "priceCurrency": "USD",
    "description": "30 free sessions to start. Popular pack: 60 sessions for $10. AI Q&A Generator and Q&A Management free on first profile.",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "ratingCount": "127"
  },
  "featureList": [
    "Real-time speech-to-text transcription powered by Deepgram",
    "Structured AI assistance for practice and communication",
    "Low-latency speech processing and semantic retrieval",
    "Personalized responses based on your uploaded context",
    "Low-latency response streaming for practice sessions",
    "Supports job, academic, and admissions preparation"
  ],
  "keywords": "interview preparation, AI interview practice, interview communication, speech pipeline, semantic retrieval",
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
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
