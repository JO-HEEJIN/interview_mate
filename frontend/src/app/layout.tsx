import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Providers } from "@/components/providers";
import { Header } from "@/components/layout/Header";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "InterviewMate.ai - AI Interview Assistant",
  description: "Real-time AI-powered interview assistant that helps you prepare for technical and behavioral interviews",
  icons: {
    icon: '/best.jpg',
    apple: '/best.jpg',
    shortcut: '/best.jpg',
  },
  manifest: '/manifest.json',
  openGraph: {
    title: "InterviewMate.ai - AI Interview Assistant",
    description: "Real-time AI-powered interview assistant that helps you prepare for technical and behavioral interviews",
    url: 'https://interviewmate.ai',
    siteName: 'InterviewMate.ai',
    images: [
      {
        url: '/best.jpg',
        width: 1200,
        height: 630,
        alt: 'InterviewMate.ai',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'InterviewMate.ai - AI Interview Assistant',
    description: 'Real-time AI-powered interview assistant that helps you prepare for technical and behavioral interviews',
    images: ['/best.jpg'],
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
    title: 'InterviewMate',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
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
