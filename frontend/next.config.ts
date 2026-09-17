import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Retired pages that described live-interview use. Permanent redirects
  // replace them in search indexes and keep old inbound links working.
  async redirects() {
    return [
      { source: "/comparison", destination: "/faq", permanent: true },
      {
        source: "/faq/:lang(ar|es|hi|id|ja|ko|pt|ru|th|tl|vi|zh)",
        destination: "/faq",
        permanent: true,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(self), geolocation=()",
          },
          {
            key: "Access-Control-Allow-Origin",
            value: "https://interviewmate.tech",
          },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "img-src 'self' data: https:",
              "font-src 'self' data: https://fonts.gstatic.com",
              "connect-src 'self' https://*.supabase.co wss://*.supabase.co https://api.deepgram.com https://api.stripe.com https://api.lemonsqueezy.com https://*.railway.app wss://*.railway.app",
              "frame-ancestors 'none'",
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
