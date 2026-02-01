# Hotel Links Monitoring System - Setup Instructions

This document provides step-by-step instructions to set up the automated hotel links monitoring system with email notifications and GitHub Pages dashboard.

## Table of Contents
1. [GitHub Repository Setup](#github-repository-setup)
2. [Gmail App Password Setup](#gmail-app-password-setup)
3. [GitHub Secrets Configuration](#github-secrets-configuration)
4. [GitHub Pages Configuration](#github-pages-configuration)
5. [Testing the Workflow](#testing-the-workflow)
6. [Troubleshooting](#troubleshooting)

---

## GitHub Repository Setup

### Repository Structure
Your repository should have the following structure:
```
blog_hotel_links_verifier/
├── .github/
│   └── workflows/
│       └── monitor-hotel-links.yml
├── agoda/
│   ├── verify_blog_links.py
│   ├── generate_dashboard.py
│   ├── agoda_client.py
│   ├── requirements.txt
│   ├── .env (local only, not committed)
│   └── docs/
│       └── .gitkeep
└── README.md
```

### Important Files
- `verify_blog_links.py`: Scrapes blog posts and verifies hotel availability
- `generate_dashboard.py`: Generates HTML dashboard from verification results
- `monitor-hotel-links.yml`: GitHub Actions workflow configuration
- `docs/`: Directory where the HTML dashboard will be generated

---

## Gmail App Password Setup

To send email notifications, you need to create a Gmail App Password (NOT your regular Gmail password).

### Prerequisites
- Gmail account (sakrecubes@gmail.com)
- 2-Factor Authentication (2FA) must be enabled on your Google account

### Step-by-Step Instructions

#### Step 1: Enable 2-Factor Authentication (if not already enabled)
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click on "2-Step Verification"
3. Follow the prompts to enable 2FA
4. You can use:
   - Text message verification
   - Google Authenticator app
   - Security key

#### Step 2: Generate App Password
1. Once 2FA is enabled, go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. You may need to sign in again
3. Under "Select app", choose "Mail"
4. Under "Select device", choose "Other (Custom name)"
5. Enter a descriptive name: "GitHub Actions - Hotel Links Monitor"
6. Click "Generate"
7. **Important**: Google will display a 16-character password like: `abcd efgh ijkl mnop`
   - Copy this password immediately
   - Remove the spaces: `abcdefghijklmnop`
   - Store it securely (you won't be able to see it again)

#### Step 3: Save the App Password
Store this password securely. You'll need to add it to GitHub Secrets in the next section.

### Security Notes
- ✅ App passwords are safer than your regular password
- ✅ You can revoke app passwords anytime without changing your main password
- ✅ Each app should have its own unique app password
- ❌ Never commit app passwords to your repository
- ❌ Never share app passwords with others

### Alternative: If You Can't Use App Passwords
If you cannot use Gmail app passwords (e.g., workspace account restrictions), consider:
- Using SendGrid API (free tier: 100 emails/day)
- Using Mailgun API (free tier: 1,000 emails/month)
- Using GitHub Actions marketplace email actions with different providers

---

## GitHub Secrets Configuration

GitHub Secrets are encrypted environment variables that keep your sensitive information secure.

### Required Secrets

You need to add **4 secrets** to your GitHub repository:

1. **AGODA_API_KEY**: Your Agoda affiliate API key ✓ (already configured)
2. **AGODA_SITE_ID**: Your Agoda site ID ✓ (already configured)
3. **EMAIL_USERNAME**: Your Gmail address (new)
4. **EMAIL_PASSWORD**: Your Gmail App Password (new)

### Adding Secrets to GitHub

#### Step 1: Navigate to Repository Settings
1. Go to your GitHub repository: https://github.com/sagarsakre/blog_hotel_links_verifier
2. Click on "Settings" (top menu bar)
3. In the left sidebar, click "Secrets and variables" → "Actions"

#### Step 2: Add EMAIL_USERNAME
1. Click "New repository secret"
2. Name: `EMAIL_USERNAME`
3. Secret: `sakrecubes@gmail.com`
4. Click "Add secret"

#### Step 3: Add EMAIL_PASSWORD
1. Click "New repository secret"
2. Name: `EMAIL_PASSWORD`
3. Secret: Paste your Gmail App Password (the 16-character code from earlier, without spaces)
   - Example: `abcdefghijklmnop`
4. Click "Add secret"

### Verify Your Secrets
After adding, you should see 4 secrets:
- ✅ AGODA_API_KEY
- ✅ AGODA_SITE_ID
- ✅ EMAIL_USERNAME
- ✅ EMAIL_PASSWORD

---

## GitHub Pages Configuration

Enable GitHub Pages to host your monitoring dashboard publicly.

### Step 1: Push Your Code
Ensure all files are committed and pushed to your repository:
```bash
cd /Users/ssakre/blog/python_scripts
git add .
git commit -m "Add hotel links monitoring system with dashboard"
git push origin main
```

### Step 2: Run the Workflow Manually (First Time)
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select "Monitor Hotel Links Daily" workflow
4. Click "Run workflow" → "Run workflow"
5. Wait for the workflow to complete (5-10 minutes)

### Step 3: Enable GitHub Pages
1. Go to Repository "Settings"
2. In the left sidebar, click "Pages"
3. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: Select `gh-pages` and `/` (root)
   - Click "Save"

### Step 4: Make GitHub Pages Public (Optional)
If your repository is private but you want the dashboard to be public:
1. Still in Settings → Pages
2. Look for "GitHub Pages visibility" section
3. Select "Public" (this option appears for private repos with GitHub Pro/Team/Enterprise)
4. If you don't see this option:
   - The dashboard will only be accessible to repository collaborators
   - Alternative: Create a separate public repository just for the `gh-pages` branch

### Step 5: Access Your Dashboard
After a few minutes, your dashboard will be available at:
**https://sagarsakre.github.io/blog_hotel_links_verifier/**

---

## Testing the Workflow

### Manual Test Run
1. Go to Actions tab in your repository
2. Select "Monitor Hotel Links Daily"
3. Click "Run workflow"
4. Select branch (usually `main` or `master`)
5. Click "Run workflow"

### What to Expect
The workflow will:
1. ✅ Check out your code
2. ✅ Set up Python environment
3. ✅ Install dependencies
4. ✅ Run verification scripts for all 8 destinations
5. ✅ Generate CSV reports
6. ✅ Generate JSON summaries
7. ✅ Upload artifacts (CSV and JSON files)
8. ⚠️ Send email (only if unavailable hotels found)
9. ✅ Generate HTML dashboard
10. ✅ Deploy dashboard to GitHub Pages

### Check the Results
1. **GitHub Actions**: View the workflow run details in the Actions tab
2. **Artifacts**: Download CSV reports from the workflow run
3. **Dashboard**: Visit https://sagarsakre.github.io/blog_hotel_links_verifier/
4. **Email**: Check sakrecubes@gmail.com inbox (only if issues were found)

---

## Troubleshooting

### Email Not Sending

**Problem**: Email notifications are not received

**Possible Solutions**:

1. **Check Gmail App Password**:
   - Verify the app password is correct (16 characters, no spaces)
   - Try generating a new app password
   - Ensure 2FA is enabled on your Google account

2. **Check GitHub Secrets**:
   - Go to Settings → Secrets → Actions
   - Verify `EMAIL_USERNAME` and `EMAIL_PASSWORD` exist
   - Re-add the secrets if needed

3. **Check Spam Folder**:
   - Emails from GitHub Actions might go to spam
   - Add noreply@github.com to your contacts

4. **Check Workflow Logs**:
   - Go to Actions → Select the failed run
   - Click on "Send email notification" step
   - Look for error messages

**Common Error Messages**:
- `Authentication failed`: Wrong app password or username
- `Must issue STARTTLS`: Server settings incorrect (should be handled by action)
- `Recipient address rejected`: Email address incorrect

### Dashboard Not Updating

**Problem**: Dashboard shows old data or doesn't update

**Possible Solutions**:

1. **Check Workflow Status**:
   - Go to Actions tab
   - Verify the latest workflow completed successfully
   - Look for errors in the "Generate HTML dashboard" step

2. **Clear Browser Cache**:
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or open dashboard in incognito/private mode

3. **Check GitHub Pages**:
   - Go to Settings → Pages
   - Verify source is set to `gh-pages` branch
   - Check if the page is published

4. **Check gh-pages Branch**:
   - Switch to `gh-pages` branch in GitHub
   - Verify `index.html` exists and was recently updated

### Workflow Fails

**Problem**: GitHub Actions workflow fails

**Common Issues**:

1. **API Key Issues**:
   - Verify `AGODA_API_KEY` and `AGODA_SITE_ID` secrets are correct
   - Check if Agoda API is reachable
   - Look for rate limiting errors

2. **Dependency Issues**:
   - Check if `requirements.txt` is correct
   - Verify Python version compatibility (3.11)

3. **Permission Issues**:
   - Verify workflow has `contents: write` permission
   - Check if `gh-pages` branch exists and is not protected

### Hotels Showing as Unavailable When They Exist

**Problem**: False positives - hotels showing unavailable when they're actually available

**Explanation**: The script tries 3 different months to determine availability. If a hotel is sold out during peak season, it might still show as unavailable.

**Solutions**:
1. Check the actual Agoda link in your blog post
2. Verify the property ID is correct
3. The hotel might genuinely be discontinued
4. Consider adjusting the verification logic in `verify_blog_links.py`

---

## Schedule Details

The workflow runs automatically:
- **Time**: 3:30 AM UTC daily (9:00 AM IST)
- **Frequency**: Once per day
- **Manual**: Can be triggered anytime via "Run workflow" button

To change the schedule, edit `.github/workflows/monitor-hotel-links.yml`:
```yaml
schedule:
  - cron: '30 3 * * *'  # Minute Hour Day Month DayOfWeek
```

Examples:
- `'0 0 * * *'` - Midnight UTC
- `'0 12 * * *'` - Noon UTC
- `'0 0 * * 1'` - Midnight UTC every Monday
- `'0 */6 * * *'` - Every 6 hours

---

## Support

For issues or questions:
1. Check the workflow logs in GitHub Actions
2. Review this documentation
3. Check the email configuration
4. Verify all secrets are correctly configured

---

## Summary Checklist

Before going live, ensure:
- [ ] Gmail App Password created
- [ ] 2FA enabled on Google account
- [ ] All 4 GitHub Secrets configured
- [ ] Workflow file pushed to repository
- [ ] Test run completed successfully
- [ ] GitHub Pages enabled and published
- [ ] Dashboard accessible at https://sagarsakre.github.io/blog_hotel_links_verifier/
- [ ] Email received when issues detected (test by manually breaking a link)

---

**Last Updated**: February 1, 2026  
**Repository**: https://github.com/sagarsakre/blog_hotel_links_verifier  
**Dashboard**: https://sagarsakre.github.io/blog_hotel_links_verifier/
