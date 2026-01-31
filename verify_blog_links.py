#!/usr/bin/env python3
"""
Agoda Affiliate Link Verifier
Scrapes blog posts to extract Agoda affiliate links and verifies property availability
"""

import sys
import csv
import logging
import argparse
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

from agoda_client import AgodaAPIClient, AgodaAPIError


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        verbose: Enable debug logging
        
    Returns:
        Configured logger
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler()]
    )
    
    logger = logging.getLogger('verify_blog_links')
    return logger


def scrape_agoda_links(blog_url: str, logger: logging.Logger) -> List[Dict[str, str]]:
    """
    Scrape blog post for Agoda affiliate links
    
    Args:
        blog_url: URL of the blog post to scrape
        logger: Logger instance
        
    Returns:
        List of dictionaries containing link info (hyperlink_text, agoda_url)
        
    Raises:
        requests.RequestException: If fetching blog fails
    """
    logger.info(f"Fetching blog content from: {blog_url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(blog_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find all links containing "agoda.com"
        agoda_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'agoda.com' in href.lower():
                hyperlink_text = link.get_text(strip=True)
                agoda_links.append({
                    'hyperlink_text': hyperlink_text if hyperlink_text else 'N/A',
                    'agoda_url': href
                })
        
        logger.info(f"Found {len(agoda_links)} Agoda link(s) in the blog post")
        return agoda_links
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch blog content: {e}")
        raise


def extract_property_id(agoda_url: str, logger: logging.Logger) -> Optional[int]:
    """
    Extract property ID from Agoda affiliate URL
    
    Args:
        agoda_url: Agoda affiliate URL
        logger: Logger instance
        
    Returns:
        Property ID as integer, or None if not found
    """
    try:
        # Parse URL and query parameters
        parsed = urlparse(agoda_url)
        params = parse_qs(parsed.query)
        
        # Try "selectedproperty" parameter (primary method)
        if 'selectedproperty' in params:
            property_id = int(params['selectedproperty'][0])
            logger.debug(f"Extracted property ID {property_id} from 'selectedproperty' parameter")
            return property_id
        
        # Try "hid" parameter (Agoda affiliate partner search format)
        if 'hid' in params:
            property_id = int(params['hid'][0])
            logger.debug(f"Extracted property ID {property_id} from 'hid' parameter")
            return property_id
        
        # Try "hotelId" parameter (fallback)
        if 'hotelId' in params:
            property_id = int(params['hotelId'][0])
            logger.debug(f"Extracted property ID {property_id} from 'hotelId' parameter")
            return property_id
        
        # Try to extract from path (e.g., /hotel-name.html?hotelid=12345)
        if 'hotelid' in agoda_url.lower():
            match = re.search(r'hotelid[=:](\d+)', agoda_url, re.IGNORECASE)
            if match:
                property_id = int(match.group(1))
                logger.debug(f"Extracted property ID {property_id} from URL pattern")
                return property_id
        
        logger.warning(f"Could not extract property ID from URL: {agoda_url}")
        return None
        
    except (ValueError, IndexError) as e:
        logger.warning(f"Error extracting property ID from {agoda_url}: {e}")
        return None


def generate_random_dates(year: int, month: int, logger: logging.Logger) -> Tuple[str, str]:
    """
    Generate random check-in and check-out dates for a given month
    
    Args:
        year: Year (e.g., 2026)
        month: Month (1-12)
        logger: Logger instance
        
    Returns:
        Tuple of (check_in_date, check_out_date) in YYYY-MM-DD format
    """
    # Get the last day of the month
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    
    last_day = (next_month - timedelta(days=1)).day
    
    # Generate random check-in date (not too close to end of month)
    # Leave at least 2 days for checkout
    max_check_in_day = last_day - 2
    check_in_day = random.randint(1, max_check_in_day)
    
    check_in_date = datetime(year, month, check_in_day)
    check_out_date = check_in_date + timedelta(days=2)  # 2-night stay
    
    check_in_str = check_in_date.strftime('%Y-%m-%d')
    check_out_str = check_out_date.strftime('%Y-%m-%d')
    
    logger.debug(f"Generated dates: {check_in_str} to {check_out_str}")
    
    return check_in_str, check_out_str


def verify_property_availability(
    property_id: int,
    client: AgodaAPIClient,
    currency: str,
    adults: int,
    logger: logging.Logger
) -> Dict[str, Any]:
    """
    Verify property availability by trying 3 random dates across 3 consecutive months
    
    If a hotel is unavailable in one month (e.g., due to high tourist season),
    we check the next month to determine if it's genuinely discontinued or just sold out.
    
    Args:
        property_id: Agoda property ID
        client: Agoda API client instance
        currency: Currency code
        adults: Number of adults
        logger: Logger instance
        
    Returns:
        Dictionary with verification results
    """
    # Calculate starting month (next month from current date)
    current_date = datetime.now()
    start_year = current_date.year
    start_month = current_date.month + 1
    
    if start_month > 12:
        start_month = 1
        start_year += 1
    
    logger.info(f"Verifying property {property_id} starting from {start_year}-{start_month:02d}")
    
    result = {
        'property_id': property_id,
        'availability_status': 'Unavailable',
        'actual_hotel_name': None,
        'successful_dates': None,
        'dates_tried': [],
        'daily_rate': None,
        'currency': currency,
        'error_message': None
    }
    
    last_error = None  # Track last error, only set if all attempts fail
    
    # Try 3 different months (consecutive months to avoid seasonal issues)
    for attempt in range(1, 4):
        # Calculate year and month for this attempt
        target_year = start_year
        target_month = start_month + (attempt - 1)
        
        # Handle year rollover
        while target_month > 12:
            target_month -= 12
            target_year += 1
        
        logger.info(f"Attempt {attempt}/3 for property {property_id} - checking {target_year}-{target_month:02d}")
        
        try:
            # Generate random dates in the target month
            check_in, check_out = generate_random_dates(
                target_year, 
                target_month, 
                logger
            )
            result['dates_tried'].append(f"{check_in} to {check_out}")
            
            # Query Agoda API
            logger.debug(f"Querying API for property {property_id} ({check_in} to {check_out})")
            response = client.hotel_search(
                hotel_ids=[property_id],
                check_in=check_in,
                check_out=check_out,
                currency=currency,
                adults=adults
            )
            
            # Check if results returned
            results = response.get('results', [])
            if results and len(results) > 0:
                hotel = results[0]
                result['availability_status'] = 'Available'
                result['actual_hotel_name'] = hotel.get('hotelName', 'N/A')
                result['successful_dates'] = f"{check_in} to {check_out}"
                result['daily_rate'] = hotel.get('dailyRate')
                # Keep the requested currency, don't override with API response
                # result['currency'] is already set to the requested currency
                result['error_message'] = None  # Clear any errors since we succeeded
                
                logger.info(f"✓ Property {property_id} is AVAILABLE ({result['actual_hotel_name']})")
                return result
            else:
                logger.debug(f"No results for property {property_id} in {target_year}-{target_month:02d}")
                
        except AgodaAPIError as e:
            logger.warning(f"API error on attempt {attempt} for property {property_id}: {e}")
            last_error = str(e)
            
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt} for property {property_id}: {e}")
            last_error = str(e)
    
    # All attempts failed - set error message only now
    result['error_message'] = last_error
    logger.info(f"✗ Property {property_id} is UNAVAILABLE (all 3 attempts across 3 months failed)")
    return result


def save_to_csv(
    blog_url: str,
    verification_results: List[Dict[str, Any]],
    output_file: str,
    logger: logging.Logger
) -> None:
    """
    Save verification results to CSV file
    
    Args:
        blog_url: The blog URL that was scraped
        verification_results: List of verification result dictionaries
        output_file: Output CSV file path
        logger: Logger instance
    """
    if not verification_results:
        logger.warning("No results to save to CSV")
        return
    
    # Column order as requested
    fieldnames = [
        'property_id',
        'hyperlink_text',
        'actual_hotel_name',
        'availability_status',
        'agoda_url',
        'successful_dates',
        'dates_tried',
        'currency',
        'daily_rate',
        'error_message',
        'blog_url'
    ]
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in verification_results:
                # Convert dates_tried list to string
                if isinstance(result.get('dates_tried'), list):
                    result['dates_tried'] = '; '.join(result['dates_tried'])
                
                # Add blog_url to each row
                result['blog_url'] = blog_url
                
                writer.writerow(result)
        
        logger.info(f"✓ Results saved to {output_file}")
        
    except IOError as e:
        logger.error(f"Failed to save CSV file: {e}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Verify Agoda affiliate links from blog posts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify all Agoda links in a blog post
  python verify_blog_links.py \\
    --blog-url "https://sakrecubes.com/2022/10/bali-complete-travel-guide.html" \\
    --output bali_hotels_verification.csv
  
  # With custom currency and verbose logging
  python verify_blog_links.py \\
    --blog-url "https://example.com/travel-guide" \\
    --currency INR \\
    --adults 2 \\
    --verbose
        """
    )
    
    # Required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument('--blog-url', type=str, required=True,
                         help='Blog post URL to scrape for Agoda links')
    
    # Optional arguments
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--output', type=str, default='agoda_verification_report.csv',
                         help='Output CSV file path (default: agoda_verification_report.csv)')
    optional.add_argument('--currency', type=str, default='INR',
                         help='Currency code for price checks (default: INR)')
    optional.add_argument('--adults', type=int, default=2,
                         help='Number of adults (default: 2)')
    optional.add_argument('--verbose', action='store_true',
                         help='Enable verbose logging')
    
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    logger.info("=" * 80)
    logger.info("Agoda Affiliate Link Verifier")
    logger.info("=" * 80)
    
    try:
        # Step 1: Scrape blog for Agoda links
        agoda_links = scrape_agoda_links(args.blog_url, logger)
        
        if not agoda_links:
            logger.warning("No Agoda links found in the blog post")
            return 0
        
        # Step 2: Extract property IDs and verify availability
        verification_results = []
        
        logger.info(f"\nProcessing {len(agoda_links)} Agoda link(s)...")
        logger.info("=" * 80)
        
        # Initialize API client
        with AgodaAPIClient(logger=logger) as client:
            for i, link_info in enumerate(agoda_links, 1):
                logger.info(f"\n[{i}/{len(agoda_links)}] Processing: {link_info['hyperlink_text']}")
                logger.info(f"URL: {link_info['agoda_url']}")
                
                # Extract property ID
                property_id = extract_property_id(link_info['agoda_url'], logger)
                
                if property_id is None:
                    logger.warning("Skipping - could not extract property ID")
                    verification_results.append({
                        'hyperlink_text': link_info['hyperlink_text'],
                        'agoda_url': link_info['agoda_url'],
                        'property_id': 'N/A',
                        'availability_status': 'Error',
                        'actual_hotel_name': None,
                        'successful_dates': None,
                        'dates_tried': [],
                        'daily_rate': None,
                        'currency': args.currency,
                        'error_message': 'Could not extract property ID'
                    })
                    continue
                
                # Verify availability
                result = verify_property_availability(
                    property_id,
                    client,
                    args.currency,
                    args.adults,
                    logger
                )
                
                # Add link info to result
                result['hyperlink_text'] = link_info['hyperlink_text']
                result['agoda_url'] = link_info['agoda_url']
                
                verification_results.append(result)
        
        # Step 3: Save results to CSV
        logger.info("\n" + "=" * 80)
        logger.info("Verification Summary")
        logger.info("=" * 80)
        
        available_count = sum(1 for r in verification_results if r['availability_status'] == 'Available')
        unavailable_count = sum(1 for r in verification_results if r['availability_status'] == 'Unavailable')
        error_count = sum(1 for r in verification_results if r['availability_status'] == 'Error')
        
        logger.info(f"Total links processed: {len(verification_results)}")
        logger.info(f"Available: {available_count}")
        logger.info(f"Unavailable: {unavailable_count}")
        logger.info(f"Errors: {error_count}")
        
        save_to_csv(args.blog_url, verification_results, args.output, logger)
        
        logger.info("\n✓ Verification completed successfully!")
        logger.info(f"Report saved to: {args.output}")
        
        return 0
        
    except requests.RequestException as e:
        logger.error(f"Network error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
