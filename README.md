# Agoda Affiliate API Scripts

Python scripts to interact with the Agoda Affiliate Long Tail Search API v2.0 for fetching hotel availability, pricing, and details.

## Features

- **City Search**: Search for hotels in a specific city with filtering options
- **Hotel Search**: Get details for specific hotels by their IDs
- **Link Verifier**: Automatically verify Agoda affiliate links from blog posts
- **Flexible Output**: Console display and file export (JSON/CSV)
- **Robust Error Handling**: Comprehensive error handling with retry logic
- **CLI Interface**: Easy-to-use command-line arguments
- **Secure Configuration**: Environment-based API credential management

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Credentials

Copy the example environment file and add your Agoda API credentials:

```bash
cp .env.example .env
```

Edit `.env` and replace with your actual credentials:

```
AGODA_SITE_ID=your_site_id_here
AGODA_API_KEY=your_api_key_here
```

**Important**: Never commit the `.env` file with actual credentials to version control.

## Usage

### Blog Link Verification (NEW!)

Verify all Agoda affiliate links in a blog post:

```bash
python verify_blog_links.py \
  --blog-url "https://sakrecubes.com/2022/10/bali-complete-travel-guide.html" \
  --output bali_hotels_verification.csv
```

Currency defaults to INR. Override with `--currency USD` if needed.

This will:
1. Scrape the blog post for all Agoda links
2. Extract property IDs from affiliate URLs
3. Verify availability for random dates next month (3 attempts per property)
4. Generate a CSV report with availability status and name comparison

**See [VERIFICATION_GUIDE.md](VERIFICATION_GUIDE.md) for detailed documentation.**

### City Search

Search for hotels in a specific city:

```bash
python city_search.py --city-id 9395 --check-in 2026-03-01 --check-out 2026-03-03
```

With additional filters:

```bash
python city_search.py \
  --city-id 9395 \
  --check-in 2026-03-01 \
  --check-out 2026-03-03 \
  --currency USD \
  --adults 2 \
  --children 1 \
  --min-price 50 \
  --max-price 200 \
  --min-star-rating 4.5 \
  --max-results 20 \
  --sort-by PriceAsc \
  --output results.json
```

### Hotel Search

Search for specific hotels by their IDs:

```bash
python hotel_search.py \
  --hotel-ids 407854,463019,1144213 \
  --check-in 2026-03-01 \
  --check-out 2026-03-03 \
  --currency USD \
  --output hotel_results.csv
```

## Command-Line Arguments

### City Search (`city_search.py`)

**Required:**
- `--city-id`: Agoda city ID
- `--check-in`: Check-in date (YYYY-MM-DD)
- `--check-out`: Check-out date (YYYY-MM-DD)

**Optional:**
- `--currency`: Currency code (default: USD)
- `--language`: Language code (default: en-us)
- `--adults`: Number of adults (default: 2)
- `--children`: Number of children (default: 0)
- `--min-price`: Minimum daily rate
- `--max-price`: Maximum daily rate
- `--min-star-rating`: Minimum star rating (0-5)
- `--min-review-score`: Minimum review score (0-10)
- `--max-results`: Maximum number of results (1-30, default: 10)
- `--sort-by`: Sort order (Recommended, PriceAsc, PriceDesc, StarRatingDesc, etc.)
- `--discount-only`: Show only hotels with discounts
- `--output`: Output file path (.json or .csv)
- `--verbose`: Enable verbose logging
- `--log-file`: Save logs to file

### Hotel Search (`hotel_search.py`)

**Required:**
- `--hotel-ids`: Comma-separated list of hotel IDs
- `--check-in`: Check-in date (YYYY-MM-DD)
- `--check-out`: Check-out date (YYYY-MM-DD)

**Optional:**
- `--currency`: Currency code (default: USD)
- `--language`: Language code (default: en-us)
- `--adults`: Number of adults (default: 2)
- `--children`: Number of children (default: 0)
- `--output`: Output file path (.json or .csv)
- `--verbose`: Enable verbose logging
- `--log-file`: Save logs to file

## Supported Values

### Currency Codes

EUR, GBP, HKD, MYR, SGD, THB, USD, NZD, AUD, JPY, ZAR, CAD, AED, CNY, PHP, CHF, DKK, SEK, CZK, PLN, IDR, KRW, INR, TWD, NOK, and more (see API documentation)

### Language Codes

en-us, fr-fr, de-de, it-it, es-es, ja-jp, zh-hk, zh-cn, ko-kr, ru-ru, pt-pt, th-th, and more (see API documentation)

### Sort Options (City Search)

- Recommended (default)
- PriceAsc / PriceDesc
- StarRatingAsc / StarRatingDesc
- AllGuestsReviewScore
- BusinessTravellerReviewScore
- CouplesReviewScore
- SoloTravellersReviewScore
- FamiliesWithYoungReviewScore
- FamiliesWithTeenReviewScore
- GroupsReviewScore

## Output Format

### JSON Output

Structured JSON with metadata and results:

```json
{
  "search_params": {
    "city_id": 9395,
    "check_in": "2026-03-01",
    "check_out": "2026-03-03"
  },
  "timestamp": "2026-01-31T10:30:00",
  "total_results": 10,
  "hotels": [
    {
      "hotel_id": 463019,
      "hotel_name": "Sample Hotel",
      "star_rating": 4.0,
      "review_score": 8.1,
      "daily_rate": 85.50,
      "currency": "USD",
      "discount_percentage": 15,
      "free_wifi": true,
      "breakfast_included": false,
      "image_url": "https://...",
      "landing_url": "https://..."
    }
  ]
}
```

### CSV Output

Flattened format suitable for spreadsheet analysis with columns: hotel_id, hotel_name, star_rating, review_score, daily_rate, crossed_out_rate, currency, discount_percentage, free_wifi, breakfast_included, image_url, landing_url

## Error Handling

The scripts include comprehensive error handling for:

- API authentication errors (401)
- Invalid parameters (400)
- No search results (911)
- Network timeouts and connection errors
- Rate limiting (403)
- Server errors (500, 503)

Failed requests are automatically retried with exponential backoff (3 attempts).

## Logging

Enable verbose logging to see detailed API interactions:

```bash
python city_search.py --city-id 9395 --check-in 2026-03-01 --check-out 2026-03-03 --verbose
```

Save logs to a file:

```bash
python city_search.py --city-id 9395 --check-in 2026-03-01 --check-out 2026-03-03 --log-file api.log
```

## API Reference

This implementation uses the Agoda Affiliate Long Tail Search API v2.0.

**Endpoint**: `http://affiliateapi7643.agoda.com/affiliateservice/lt_v1`

For more information about the API, refer to the official Agoda Affiliate API documentation.

## Security Notes

- API credentials are stored in `.env` file which is excluded from version control
- Never hardcode API keys in source code
- The `.env` file should never be committed to Git
- Use `.env.example` as a template for sharing configuration structure

## License

This project is provided as-is for use with the Agoda Affiliate API.
