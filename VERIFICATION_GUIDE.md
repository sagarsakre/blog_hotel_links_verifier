# Agoda Affiliate Link Verification Tool

## Overview

The `verify_blog_links.py` script automatically scrapes your blog posts to extract Agoda affiliate links, verifies property availability using the Agoda API, and generates a detailed CSV report comparing hyperlink names with actual property names.

## Features

✅ **Automatic Scraping**: Extracts all Agoda links from any blog post URL
✅ **Smart Property ID Extraction**: Handles multiple Agoda URL formats (`hid`, `selectedproperty`, `hotelId`)
✅ **Availability Verification**: Tests 3 random dates in next month to check property availability
✅ **Name Comparison**: Shows hyperlink text vs actual hotel name for semantic matching
✅ **CSV Export**: Easy-to-analyze spreadsheet format for bulk verification

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install beautifulsoup4 lxml requests python-dotenv
```

## Usage

### Basic Usage

Verify all Agoda links in a blog post:

```bash
python3 verify_blog_links.py \
  --blog-url "https://sakrecubes.com/2022/10/bali-complete-travel-guide.html" \
  --output bali_hotels_verification.csv \
  --currency INR
```

**Note**: Currency defaults to INR. Use `--currency USD` or other codes if needed.

### Advanced Options

```bash
python3 verify_blog_links.py \
  --blog-url "https://your-blog.com/travel-guide" \
  --output verification_report.csv \
  --currency INR \
  --adults 2 \
  --verbose
```

### Command-Line Arguments

**Required:**
- `--blog-url`: URL of the blog post to scrape

**Optional:**
- `--output`: Output CSV file path (default: `agoda_verification_report.csv`)
- `--currency`: Currency code for prices (default: `INR`)
- `--adults`: Number of adults for booking (default: `2`)
- `--verbose`: Enable detailed logging

## CSV Report Columns

The generated CSV contains the following columns (in this order):

| Column | Description |
|--------|-------------|
| `property_id` | Extracted Agoda property ID |
| `hyperlink_text` | Hotel name as shown in your blog link |
| `actual_hotel_name` | Official hotel name from Agoda API |
| `availability_status` | `Available`, `Unavailable`, or `Error` |
| `agoda_url` | Full Agoda affiliate URL |
| `successful_dates` | Check-in/check-out dates that worked |
| `dates_tried` | All date combinations attempted (separated by `;`) |
| `currency` | Currency code (defaults to INR) |
| `daily_rate` | Price per night in specified currency |
| `error_message` | Error details (only if all 3 attempts failed) |
| `blog_url` | The blog post URL that was scraped |

**Note**: `error_message` is empty for available properties and only populated when all 3 verification attempts fail.

## Example Test Results

**Test Blog:** Bali Complete Travel Guide
**Total Links:** 127 Agoda hotel links
**Results:**
- ✅ Available: 118 hotels
- ❌ Unavailable: 9 hotels

### Unavailable Properties Found

1. Ananda Resort Seminyak (ID: 201700)
2. Bali Dream Resort (ID: 666316)
3. Alam kawi (ID: 18907297)
4. Sarwi homestay (ID: 10616792)
5. Umae Villa (ID: 545266)
6. Pondok Bamboo Villa (ID: 10592138)
7. Episode Kuta (ID: 411115)
8. Villa White Karma (ID: 37864749)
9. Bubble Hotel (ID: 25056937)

## Post-Verification Workflow

1. **Open the CSV** in Excel, Google Sheets, or any spreadsheet application

2. **Compare Names**: Review the `hyperlink_text` vs `actual_hotel_name` columns
   - Some names may differ slightly (e.g., "Harris Seminyak" vs "HARRIS Hotel Seminyak")
   - Use ChatGPT for semantic matching if needed

3. **Handle Unavailable Properties**:
   - Update blog links to alternative hotels
   - Remove outdated recommendations
   - Add notes about seasonal availability

4. **Verify Pricing**: Check `daily_rate` to ensure recommendations match your budget categories

## How It Works

1. **Web Scraping**: Fetches blog HTML and finds all links containing "agoda.com"
2. **Property ID Extraction**: Parses URLs to extract hotel IDs from various parameter formats
3. **Date Generation**: Creates 3 random check-in dates in next month (2-night stays)
4. **API Verification**: Queries Agoda API for each property with random dates
5. **Retry Logic**: If first date fails, tries 2 more random dates before marking unavailable
6. **Report Generation**: Compiles all results into a comprehensive CSV file

## Supported URL Formats

The tool automatically detects property IDs from multiple Agoda URL formats:

```
✅ https://www.agoda.com/partners/partnersearch.aspx?hid=123456
✅ https://www.agoda.com/search?selectedproperty=123456
✅ https://www.agoda.com/hotel/123456
✅ URLs with hotelId parameter
```

## Troubleshooting

### "No module named 'bs4'" Error

Install BeautifulSoup4:
```bash
pip install beautifulsoup4 lxml
```

### "Could not extract property ID" Warning

The URL format might be unsupported. Check the `agoda_url` column in the CSV and report the format for future support.

### API Authentication Errors

Ensure your `.env` file contains valid Agoda API credentials:
```
AGODA_SITE_ID=your_site_id
AGODA_API_KEY=your_api_key
```

### All Properties Showing "Unavailable"

- Verify your Agoda API credentials are valid
- Check if you've exceeded API rate limits
- Ensure the properties are actually listed on Agoda

## Tips for Best Results

✨ **Run During Off-Peak Hours**: API calls can take time for many properties
✨ **Review Regularly**: Hotel availability changes seasonally
✨ **Compare Names Carefully**: Some hotels rebrand or have multiple names
✨ **Check Prices**: Daily rates help verify your budget recommendations
✨ **Update Blog Links**: Remove or replace unavailable properties promptly

## Future Enhancements

Potential features for future versions:
- Batch processing multiple blog URLs from a file
- HTML report generation with visual indicators
- Historical tracking of availability changes
- Email notifications for newly unavailable properties
- Integration with Google Sheets API

## Support

For issues or questions:
1. Check the verbose logs: `--verbose` flag
2. Review the CSV `error_message` column
3. Verify your Agoda API credentials
4. Check the README.md for API documentation

---

**Created:** February 1, 2026
**Version:** 1.0.0
**License:** MIT
