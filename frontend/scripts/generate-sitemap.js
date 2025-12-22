#!/usr/bin/env node
/**
 * Generate sitemap.xml and robots.txt using environment variables
 * Run: node scripts/generate-sitemap.js
 */

const fs = require('fs');
const path = require('path');

// Try to load .env.local manually (without dotenv dependency)
const envPath = path.join(__dirname, '../.env.local');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  envContent.split('\n').forEach(line => {
    const match = line.match(/^([^#=]+)=(.*)$/);
    if (match) {
      const key = match[1].trim();
      const value = match[2].trim();
      if (!process.env[key]) {
        process.env[key] = value;
      }
    }
  });
}

const domain = process.env.NEXT_PUBLIC_SITE_DOMAIN || 'interviewmate.tech';
const siteUrl = `https://${domain}`;

// Define site pages
const pages = [
  { path: '/', priority: '1.0', changefreq: 'daily' },
  { path: '/interview', priority: '0.9', changefreq: 'weekly' },
  { path: '/profile/qa-pairs', priority: '0.8', changefreq: 'weekly' },
  { path: '/profile/context-upload', priority: '0.7', changefreq: 'monthly' },
  { path: '/profile/interview-settings', priority: '0.7', changefreq: 'monthly' },
  { path: '/profile/stories', priority: '0.7', changefreq: 'monthly' },
  { path: '/pricing', priority: '0.9', changefreq: 'weekly' },
];

// Generate sitemap.xml
const generateSitemap = () => {
  const currentDate = new Date().toISOString().split('T')[0];

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(page => `  <url>
    <loc>${siteUrl}${page.path}</loc>
    <lastmod>${currentDate}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

  const publicDir = path.join(__dirname, '../public');
  fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), sitemap);
  console.log('✅ Generated sitemap.xml');
};

// Generate robots.txt
const generateRobots = () => {
  const robots = `# https://www.robotstxt.org/robotstxt.html
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /auth/

Sitemap: ${siteUrl}/sitemap.xml`;

  const publicDir = path.join(__dirname, '../public');
  fs.writeFileSync(path.join(publicDir, 'robots.txt'), robots);
  console.log('✅ Generated robots.txt');
};

// Run generators
console.log(`🌐 Generating SEO files for: ${siteUrl}`);
generateSitemap();
generateRobots();
console.log('✨ Done!');
