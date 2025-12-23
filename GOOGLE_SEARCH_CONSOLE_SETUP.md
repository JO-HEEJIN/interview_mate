# Google Search Console Setup Guide

This guide walks through setting up Google Search Console for interviewmate.tech to enable SEO indexing and monitoring.

## Prerequisites

- Access to interviewmate.tech DNS settings
- Google account

## Steps

### 1. Add Property to Google Search Console

1. Go to https://search.google.com/search-console
2. Click "Add Property"
3. Select "URL prefix" and enter: `https://interviewmate.tech`
4. Click "Continue"

### 2. Verify Ownership

Choose one of the following verification methods:

#### Option A: DNS Verification (Recommended)
1. Google will provide a TXT record
2. Add the TXT record to your domain's DNS settings
3. Wait for DNS propagation (can take up to 48 hours)
4. Click "Verify" in Google Search Console

#### Option B: HTML File Upload
1. Download the verification HTML file from Google Search Console
2. Upload it to `frontend/public/` directory
3. Deploy to production so it's accessible at `https://interviewmate.tech/[filename].html`
4. Click "Verify" in Google Search Console

#### Option C: HTML Tag
1. Copy the meta tag provided by Google
2. Add it to `frontend/src/app/layout.tsx` in the `<head>` section
3. Deploy to production
4. Click "Verify" in Google Search Console

### 3. Submit Sitemap

Once verified:
1. Go to "Sitemaps" in the left sidebar
2. Enter sitemap URL: `https://interviewmate.tech/sitemap.xml`
3. Click "Submit"

### 4. Request Indexing for Key Pages

Manually request indexing for important pages:
1. Go to "URL Inspection" in the left sidebar
2. Enter each URL:
   - `https://interviewmate.tech/`
   - `https://interviewmate.tech/faq`
   - `https://interviewmate.tech/comparison`
   - `https://interviewmate.tech/pricing`
3. Click "Request Indexing" for each page

### 5. Monitor Performance

After 1-2 weeks, check:
- **Performance**: Search queries, clicks, impressions
- **Coverage**: Indexed pages vs errors
- **Enhancements**: Mobile usability, Core Web Vitals

## Expected Timeline

- **Verification**: Immediate (after DNS propagation)
- **First crawl**: 1-3 days
- **Full indexing**: 1-2 weeks
- **Search visibility**: 2-4 weeks

## Key Metrics to Monitor

1. **Indexed Pages**: Should be 20+ (home, pricing, FAQ pages, comparison)
2. **Search Queries**: Track queries like "real-time interview assistant", "live interview AI"
3. **Click-Through Rate (CTR)**: Target >5% for branded queries
4. **Average Position**: Target top 10 for target keywords

## Troubleshooting

### Verification Failed
- Ensure DNS record is correctly added
- Wait full 48 hours for DNS propagation
- Check that HTML file is accessible (no 404 error)

### Pages Not Indexed
- Check robots.txt allows crawling
- Verify sitemap is accessible
- Ensure pages return 200 status code
- Check for duplicate content issues

### Low Search Visibility
- Add more content (blog posts, use cases)
- Build backlinks (Product Hunt, directories)
- Optimize meta descriptions and titles
- Ensure mobile-friendly design

## Next Steps After Setup

1. Set up Google Analytics for traffic monitoring
2. Create Google My Business profile (if applicable)
3. Submit to Bing Webmaster Tools
4. Start building backlinks through:
   - Product Hunt launch
   - Reddit posts
   - Tech blog articles
   - Product directories
