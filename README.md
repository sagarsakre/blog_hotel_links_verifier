# Hotel Links Monitoring System

Automated monitoring system for Agoda affiliate links across travel blog posts, with email notifications and a live dashboard.

## 🎯 Overview

This system automatically:
- ✅ Scrapes travel blog posts for Agoda hotel links
- ✅ Verifies hotel availability via Agoda API
- ✅ Sends email alerts when properties become unavailable
- ✅ Generates a live dashboard showing health status
- ✅ Runs daily via GitHub Actions

## 📊 Live Dashboard

**View the dashboard**: [https://sagarsakre.github.io/blog_hotel_links_verifier/](https://sagarsakre.github.io/blog_hotel_links_verifier/)

The dashboard shows:
- Overall health status of all destinations
- Availability statistics for each destination
- List of unavailable properties (if any)
- Last check timestamp

## 🏨 Monitored Destinations

The system currently monitors hotel links for:
1. **Bali** - Complete Travel Guide
2. **Varkala** - Complete Guide
3. **Munnar** - Complete Travel Guide
4. **Goa** - Complete Travel Guide
5. **Singapore** - Complete Guide
6. **Mysore** - Best Places to Stay
7. **Chikmagaluru** - Travel Guide
8. **Udupi** - Complete Guide

## 🔧 Components

### 1. `verify_blog_links.py`
Main script that:
- Scrapes blog posts for Agoda links
- Extracts property IDs
- Checks availability across 3 consecutive months
- Generates CSV reports and JSON summaries
- Returns exit codes for workflow automation

### 2. `generate_dashboard.py`
Dashboard generator that:
- Reads JSON summaries from verification runs
- Creates a beautiful, responsive HTML dashboard
- Shows real-time status with color-coded indicators
- Deployed to GitHub Pages automatically

### 3. GitHub Actions Workflow
Automated workflow that:
- Runs daily at 9:00 AM IST (3:30 UTC)
- Verifies all destination links
- Sends email on failures
- Updates the dashboard
- Stores reports as artifacts

## 📧 Email Notifications

Email alerts are sent to `sakrecubes@gmail.com` when:
- ❌ Hotels become unavailable
- ⚠️ Property IDs cannot be extracted
- 🔴 API errors occur

Emails include:
- Summary of issues
- Attached CSV reports
- Link to live dashboard
- Link to workflow run details

## 🚀 Setup

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed setup guide.

### Quick Start

1. **Configure GitHub Secrets**:
   - `AGODA_API_KEY`
   - `AGODA_SITE_ID`
   - `EMAIL_USERNAME`
   - `EMAIL_PASSWORD` (Gmail App Password)

2. **Enable GitHub Pages**:
   - Settings → Pages
   - Source: `gh-pages` branch
   - Make it public (optional, for private repos)

3. **Run the workflow**:
   - Actions → Monitor Hotel Links Daily
   - Click "Run workflow"

## 📁 File Structure

```
agoda/
├── verify_blog_links.py      # Main verification script
├── generate_dashboard.py     # Dashboard generator
├── agoda_client.py            # Agoda API client
├── requirements.txt           # Python dependencies
├── docs/                      # GitHub Pages output
│   └── index.html            # Generated dashboard
├── SETUP_INSTRUCTIONS.md     # Detailed setup guide
└── README.md                 # This file
```

## 🔄 Workflow Schedule

- **Automated**: Daily at 3:30 UTC (9:00 AM IST)
- **Manual**: Can be triggered anytime via GitHub Actions UI
- **Artifacts**: CSV reports retained for 90 days

## 📈 Usage

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Test single destination
python verify_blog_links.py \
  --blog-url "https://sakrecubes.com/2022/10/bali-complete-travel-guide.html" \
  --output bali_hotels.csv \
  --json-output bali_summary.json

# Generate dashboard locally
python generate_dashboard.py \
  --input-dir . \
  --output docs/index.html
```

### Adding New Destinations

To monitor a new destination, edit `.github/workflows/monitor-hotel-links.yml` and add:

```yaml
python verify_blog_links.py \
  --blog-url "https://sakrecubes.com/YOUR-POST-URL.html" \
  --output DESTINATION_hotels.csv \
  --json-output DESTINATION_summary.json || FAILED=1
```

## 🛠️ Troubleshooting

See [SETUP_INSTRUCTIONS.md - Troubleshooting](SETUP_INSTRUCTIONS.md#troubleshooting) for common issues and solutions.

Quick checks:
- ✅ All GitHub Secrets configured
- ✅ Gmail 2FA enabled
- ✅ App Password generated
- ✅ GitHub Pages enabled
- ✅ Workflow has write permissions

## 📊 Dashboard Features

- **Responsive Design**: Works on mobile, tablet, and desktop
- **Real-time Status**: Color-coded health indicators
- **Detailed Reports**: Expandable rows for unavailable properties
- **Auto-refresh**: Updated daily via GitHub Actions
- **Public Access**: Can be shared with anyone

## 🔐 Security

- ✅ Private repository protects code and secrets
- ✅ API keys stored in GitHub Secrets (encrypted)
- ✅ Gmail App Password (revocable, not main password)
- ✅ Dashboard shows only public information
- ❌ No sensitive data exposed in dashboard

## 📝 License

Private repository - All rights reserved.

## 👤 Author

**Sagar Sakre**
- Blog: [SakreCubes.com](https://sakrecubes.com)
- Email: sakrecubes@gmail.com

## 🙏 Acknowledgments

- Agoda API for hotel availability data
- GitHub Actions for automation
- GitHub Pages for dashboard hosting

---

**Last Updated**: February 1, 2026  
**Dashboard**: https://sagarsakre.github.io/blog_hotel_links_verifier/  
**Repository**: https://github.com/sagarsakre/blog_hotel_links_verifier
