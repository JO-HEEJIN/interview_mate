import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Providers } from "@/components/providers";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { defaultMetadata } from "@/config/metadata";
import { siteConfig } from "@/config/site";
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
  "applicationCategory": "EducationalApplication",
  "operatingSystem": "Web Browser",
  "description": siteConfig.description,
  "url": "https://interviewmate.tech",
  "offers": {
    "@type": "Offer",
    "price": "10.00",
    "priceCurrency": "USD",
    "description": "30 free practice sessions to start. Popular pack: 60 sessions for $10. AI Q&A Generator and Q&A Management free on first profile.",
    "availability": "https://schema.org/InStock"
  },
  "featureList": [
    "Personalized practice questions generated from your resume and target-role context",
    "Timed mock interview sessions with real-time Deepgram transcription",
    "Personalized response suggestions grounded in your prepared context",
    "Practice Q&A library with semantic retrieval",
    "Session history export for review"
  ],
  "keywords": siteConfig.keywords,
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
