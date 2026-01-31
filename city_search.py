#!/usr/bin/env python3
"""
City Search Script for Agoda Affiliate API
Searches for hotels in a specific city with various filtering options
"""

import sys
import json
import csv
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from agoda_client import AgodaAPIClient, AgodaAPIError


def setup_logging(verbose: bool = False, log_file: str = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        verbose: Enable debug logging
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler()]
    )
    
    logger = logging.getLogger('city_search')
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    return logger


def validate_date(date_str: str) -> str:
    """
    Validate date string in YYYY-MM-DD format
    
    Args:
        date_str: Date string to validate
        
    Returns:
        Validated date string
        
    Raises:
        ValueError: If date format is invalid
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")


def validate_dates(check_in: str, check_out: str) -> None:
    """
    Validate check-in and check-out dates
    
    Args:
        check_in: Check-in date string
        check_out: Check-out date string
        
    Raises:
        ValueError: If dates are invalid or check-out is not after check-in
    """
    check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
    
    if check_out_date <= check_in_date:
        raise ValueError("Check-out date must be after check-in date")
    
    # Warn if dates are in the past
    today = datetime.now().date()
    if check_in_date.date() < today:
        logging.warning(f"Check-in date {check_in} is in the past")


def format_hotel_data(hotel: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format hotel data for display
    
    Args:
        hotel: Raw hotel data from API
        
    Returns:
        Formatted hotel data
    """
    return {
        'hotel_id': hotel.get('hotelId'),
        'hotel_name': hotel.get('hotelName'),
        'star_rating': hotel.get('starRating'),
        'review_score': hotel.get('reviewScore'),
        'review_count': hotel.get('reviewCount', 0),
        'daily_rate': hotel.get('dailyRate'),
        'crossed_out_rate': hotel.get('crossedOutRate'),
        'currency': hotel.get('currency'),
        'discount_percentage': hotel.get('discountPercentage'),
        'free_wifi': hotel.get('freeWifi'),
        'breakfast_included': hotel.get('includeBreakfast'),
        'image_url': hotel.get('imageURL'),
        'landing_url': hotel.get('landingURL')
    }


def display_results(results: List[Dict[str, Any]], logger: logging.Logger) -> None:
    """
    Display search results in console
    
    Args:
        results: List of formatted hotel data
        logger: Logger instance
    """
    if not results:
        logger.info("No hotels found matching the criteria")
        return
    
    logger.info(f"\nFound {len(results)} hotel(s):\n")
    
    for i, hotel in enumerate(results, 1):
        print(f"\n{'='*80}")
        print(f"Hotel {i}: {hotel['hotel_name']}")
        print(f"{'='*80}")
        print(f"Hotel ID: {hotel['hotel_id']}")
        print(f"Star Rating: {hotel['star_rating']} stars")
        print(f"Review Score: {hotel['review_score']}/10 ({hotel['review_count']} reviews)")
        print(f"Price: {hotel['currency']} {hotel['daily_rate']:.2f}/night", end='')
        
        if hotel['discount_percentage'] > 0:
            print(f" (was {hotel['crossed_out_rate']:.2f}, {hotel['discount_percentage']}% off)")
        else:
            print()
        
        amenities = []
        if hotel['free_wifi']:
            amenities.append("Free WiFi")
        if hotel['breakfast_included']:
            amenities.append("Breakfast Included")
        
        if amenities:
            print(f"Amenities: {', '.join(amenities)}")
        
        print(f"Booking URL: {hotel['landing_url']}")


def save_to_json(results: List[Dict[str, Any]], output_file: str, 
                 search_params: Dict[str, Any], logger: logging.Logger) -> None:
    """
    Save results to JSON file
    
    Args:
        results: List of formatted hotel data
        output_file: Output file path
        search_params: Search parameters used
        logger: Logger instance
    """
    output_data = {
        'search_params': search_params,
        'timestamp': datetime.now().isoformat(),
        'total_results': len(results),
        'hotels': results
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {output_file}")
    except IOError as e:
        logger.error(f"Failed to save JSON file: {e}")


def save_to_csv(results: List[Dict[str, Any]], output_file: str, 
                logger: logging.Logger) -> None:
    """
    Save results to CSV file
    
    Args:
        results: List of formatted hotel data
        output_file: Output file path
        logger: Logger instance
    """
    if not results:
        logger.warning("No results to save to CSV")
        return
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            # Use keys from first result as fieldnames
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(results)
        
        logger.info(f"Results saved to {output_file}")
    except IOError as e:
        logger.error(f"Failed to save CSV file: {e}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Search for hotels in a specific city using Agoda API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic search for Bangkok
  python city_search.py --city-id 9395 --check-in 2026-03-01 --check-out 2026-03-03
  
  # Search with filters and save to JSON
  python city_search.py --city-id 9395 --check-in 2026-03-01 --check-out 2026-03-03 \\
    --currency USD --adults 2 --children 1 --min-price 50 --max-price 200 \\
    --min-star-rating 4.5 --sort-by PriceAsc --output results.json
  
  # Search and save to CSV
  python city_search.py --city-id 9395 --check-in 2026-03-01 --check-out 2026-03-03 \\
    --output results.csv
        """
    )
    
    # Required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument('--city-id', type=int, required=True,
                         help='Agoda city ID')
    required.add_argument('--check-in', type=str, required=True,
                         help='Check-in date (YYYY-MM-DD)')
    required.add_argument('--check-out', type=str, required=True,
                         help='Check-out date (YYYY-MM-DD)')
    
    # Optional search parameters
    search = parser.add_argument_group('search parameters')
    search.add_argument('--currency', type=str, default='USD',
                       help='Currency code (default: USD)')
    search.add_argument('--language', type=str, default='en-us',
                       help='Language code (default: en-us)')
    search.add_argument('--adults', type=int, default=2,
                       help='Number of adults (default: 2)')
    search.add_argument('--children', type=int, default=0,
                       help='Number of children (default: 0)')
    search.add_argument('--children-ages', type=str,
                       help='Comma-separated list of children ages (e.g., 10,12)')
    
    # Filter parameters
    filters = parser.add_argument_group('filter parameters')
    filters.add_argument('--min-price', type=float,
                        help='Minimum daily rate')
    filters.add_argument('--max-price', type=float,
                        help='Maximum daily rate')
    filters.add_argument('--min-star-rating', type=float,
                        help='Minimum star rating (0-5)')
    filters.add_argument('--min-review-score', type=float,
                        help='Minimum review score (0-10)')
    filters.add_argument('--discount-only', action='store_true',
                        help='Show only hotels with discounts')
    
    # Sort and limit
    display = parser.add_argument_group('display parameters')
    display.add_argument('--sort-by', type=str, default='Recommended',
                        choices=[
                            'Recommended', 'PriceAsc', 'PriceDesc',
                            'StarRatingAsc', 'StarRatingDesc',
                            'AllGuestsReviewScore', 'BusinessTravellerReviewScore',
                            'CouplesReviewScore', 'SoloTravellersReviewScore',
                            'FamiliesWithYoungReviewScore', 'FamiliesWithTeenReviewScore',
                            'GroupsReviewScore'
                        ],
                        help='Sort order (default: Recommended)')
    display.add_argument('--max-results', type=int, default=10,
                        help='Maximum number of results (1-30, default: 10)')
    
    # Output options
    output = parser.add_argument_group('output options')
    output.add_argument('--output', type=str,
                       help='Output file path (.json or .csv)')
    output.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    output.add_argument('--log-file', type=str,
                       help='Log file path')
    
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.verbose, args.log_file)
    
    try:
        # Validate dates
        check_in = validate_date(args.check_in)
        check_out = validate_date(args.check_out)
        validate_dates(check_in, check_out)
        
        # Parse children ages if provided
        children_ages = None
        if args.children_ages:
            try:
                children_ages = [int(age.strip()) for age in args.children_ages.split(',')]
                if len(children_ages) != args.children:
                    logger.error("Number of children ages must match number of children")
                    return 1
            except ValueError:
                logger.error("Invalid children ages format. Expected comma-separated integers")
                return 1
        
        # Initialize API client
        logger.info("Initializing Agoda API client...")
        with AgodaAPIClient(logger=logger) as client:
            # Perform search
            logger.info(f"Searching for hotels in city {args.city_id}...")
            logger.info(f"Dates: {check_in} to {check_out}")
            
            response = client.city_search(
                city_id=args.city_id,
                check_in=check_in,
                check_out=check_out,
                currency=args.currency,
                language=args.language,
                adults=args.adults,
                children=args.children,
                children_ages=children_ages,
                min_price=args.min_price,
                max_price=args.max_price,
                min_star_rating=args.min_star_rating,
                min_review_score=args.min_review_score,
                discount_only=args.discount_only,
                sort_by=args.sort_by,
                max_results=args.max_results
            )
            
            # Process results
            raw_results = response.get('results', [])
            results = [format_hotel_data(hotel) for hotel in raw_results]
            
            # Display results
            display_results(results, logger)
            
            # Save to file if output specified
            if args.output:
                search_params = {
                    'city_id': args.city_id,
                    'check_in': check_in,
                    'check_out': check_out,
                    'currency': args.currency,
                    'language': args.language,
                    'adults': args.adults,
                    'children': args.children,
                    'sort_by': args.sort_by,
                    'max_results': args.max_results
                }
                
                output_path = Path(args.output)
                if output_path.suffix.lower() == '.json':
                    save_to_json(results, args.output, search_params, logger)
                elif output_path.suffix.lower() == '.csv':
                    save_to_csv(results, args.output, logger)
                else:
                    logger.error("Output file must have .json or .csv extension")
                    return 1
            
            logger.info("\nSearch completed successfully!")
            return 0
            
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except AgodaAPIError as e:
        logger.error(f"API error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
