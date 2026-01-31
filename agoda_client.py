"""
Agoda Affiliate API Client
Handles authentication, requests, and error handling for Agoda's Long Tail Search API v2.0
"""

import os
import time
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv


class AgodaAPIError(Exception):
    """Custom exception for Agoda API errors"""
    def __init__(self, error_id: int, message: str, status_code: Optional[int] = None):
        self.error_id = error_id
        self.message = message
        self.status_code = status_code
        super().__init__(f"Agoda API Error {error_id}: {message}")


class AgodaAPIClient:
    """
    Client for interacting with Agoda Affiliate Long Tail Search API v2.0
    
    Handles authentication, request construction, error handling, and retries.
    """
    
    BASE_URL = "http://affiliateapi7643.agoda.com/affiliateservice/lt_v1"
    
    # HTTP status code descriptions
    STATUS_MESSAGES = {
        400: "Bad Request - Malformed syntax",
        401: "Unauthorized - Invalid API key or Site ID",
        403: "Forbidden - Quota exceeded or terms violation",
        404: "Not Found - Service or file not found",
        410: "Gone - Request object is too old or no longer valid",
        500: "Internal Server Error - Unrecoverable problem",
        503: "Service Unavailable - Temporary maintenance",
        506: "Partial Confirm - Contact customer service"
    }
    
    def __init__(self, site_id: Optional[str] = None, api_key: Optional[str] = None, 
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the Agoda API client
        
        Args:
            site_id: Agoda site ID (loads from AGODA_SITE_ID env var if not provided)
            api_key: Agoda API key (loads from AGODA_API_KEY env var if not provided)
            logger: Optional logger instance
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Get credentials from parameters or environment variables
        self.site_id = site_id or os.getenv('AGODA_SITE_ID')
        self.api_key = api_key or os.getenv('AGODA_API_KEY')
        
        # Validate credentials are present
        if not self.site_id or not self.api_key:
            raise ValueError(
                "API credentials not found. Please set AGODA_SITE_ID and AGODA_API_KEY "
                "environment variables or pass them as parameters."
            )
        
        # Setup logging
        self.logger = logger or logging.getLogger(__name__)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Accept-Encoding': 'gzip,deflate',
            'Content-Type': 'application/json',
            'Authorization': f'{self.site_id}:{self.api_key}'
        })
    
    def _make_request(self, payload: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Make a request to the Agoda API with retry logic
        
        Args:
            payload: Request payload dictionary
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response data dictionary
            
        Raises:
            AgodaAPIError: If API returns an error
            requests.RequestException: If network error occurs after retries
        """
        retry_delays = [1, 2, 4]  # Exponential backoff delays in seconds
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"API Request (attempt {attempt + 1}/{max_retries}): {payload}")
                
                response = self.session.post(
                    self.BASE_URL,
                    json=payload,
                    timeout=30
                )
                
                self.logger.debug(f"API Response Status: {response.status_code}")
                
                # Check for HTTP errors
                if response.status_code != 200:
                    error_msg = self.STATUS_MESSAGES.get(
                        response.status_code,
                        f"HTTP {response.status_code} error"
                    )
                    self.logger.error(f"{error_msg}")
                    
                    # Retry on server errors (5xx) or service unavailable
                    if response.status_code >= 500 and attempt < max_retries - 1:
                        delay = retry_delays[attempt]
                        self.logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    
                    raise AgodaAPIError(
                        error_id=response.status_code,
                        message=error_msg,
                        status_code=response.status_code
                    )
                
                # Parse JSON response
                try:
                    data = response.json()
                except ValueError as e:
                    self.logger.error(f"Failed to parse JSON response: {e}")
                    raise AgodaAPIError(
                        error_id=0,
                        message="Invalid JSON response from API"
                    )
                
                # Check for API-level errors
                if 'error' in data:
                    error = data['error']
                    error_id = error.get('id', 0)
                    error_message = error.get('message', 'Unknown error')
                    self.logger.error(f"API Error {error_id}: {error_message}")
                    raise AgodaAPIError(error_id=error_id, message=error_message)
                
                self.logger.info("API request successful")
                return data
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
                    
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
                    
            except AgodaAPIError:
                # Don't retry on API-level errors (auth, validation, etc.)
                raise
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error: {e}")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
        
        # Should not reach here, but just in case
        raise requests.exceptions.RetryError("Max retries exceeded")
    
    def city_search(
        self,
        city_id: int,
        check_in: str,
        check_out: str,
        currency: str = "USD",
        language: str = "en-us",
        adults: int = 2,
        children: int = 0,
        children_ages: Optional[List[int]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_star_rating: Optional[float] = None,
        min_review_score: Optional[float] = None,
        discount_only: bool = False,
        sort_by: str = "Recommended",
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for hotels in a specific city
        
        Args:
            city_id: Agoda city ID
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            currency: Currency code (default: USD)
            language: Language code (default: en-us)
            adults: Number of adults (default: 2)
            children: Number of children (default: 0)
            children_ages: List of children ages (optional)
            min_price: Minimum daily rate (optional)
            max_price: Maximum daily rate (optional)
            min_star_rating: Minimum star rating 0-5 (optional)
            min_review_score: Minimum review score 0-10 (optional)
            discount_only: Show only discounted hotels (default: False)
            sort_by: Sort order (default: Recommended)
            max_results: Maximum number of results 1-30 (default: 10)
            
        Returns:
            Dictionary containing search results
        """
        # Validate max_results
        if not 1 <= max_results <= 30:
            raise ValueError("max_results must be between 1 and 30")
        
        # Build occupancy
        occupancy = {
            "numberOfAdult": adults,
            "numberOfChildren": children
        }
        if children_ages:
            if len(children_ages) != children:
                raise ValueError("Number of children ages must match number of children")
            occupancy["childrenAges"] = children_ages
        
        # Build additional criteria
        additional = {
            "currency": currency,
            "language": language,
            "occupancy": occupancy,
            "discountOnly": discount_only,
            "sortBy": sort_by,
            "maxResult": max_results
        }
        
        # Add optional filters
        if min_star_rating is not None:
            additional["minimumStarRating"] = min_star_rating
        if min_review_score is not None:
            additional["minimumReviewScore"] = min_review_score
        if min_price is not None or max_price is not None:
            # API requires both minimum and maximum when using dailyRate filter
            # Default: minimum=1, maximum=100000 (per API documentation)
            additional["dailyRate"] = {
                "minimum": int(min_price) if min_price is not None else 1,
                "maximum": int(max_price) if max_price is not None else 100000
            }
        
        # Build request payload
        payload = {
            "criteria": {
                "cityId": city_id,
                "checkInDate": check_in,
                "checkOutDate": check_out,
                "additional": additional
            }
        }
        
        return self._make_request(payload)
    
    def hotel_search(
        self,
        hotel_ids: List[int],
        check_in: str,
        check_out: str,
        currency: str = "USD",
        language: str = "en-us",
        adults: int = 2,
        children: int = 0,
        children_ages: Optional[List[int]] = None,
        discount_only: bool = False
    ) -> Dict[str, Any]:
        """
        Search for specific hotels by their IDs
        
        Args:
            hotel_ids: List of Agoda hotel IDs
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            currency: Currency code (default: USD)
            language: Language code (default: en-us)
            adults: Number of adults (default: 2)
            children: Number of children (default: 0)
            children_ages: List of children ages (optional)
            discount_only: Show only discounted hotels (default: False)
            
        Returns:
            Dictionary containing search results
        """
        if not hotel_ids:
            raise ValueError("At least one hotel ID is required")
        
        # Build occupancy
        occupancy = {
            "numberOfAdult": adults,
            "numberOfChildren": children
        }
        if children_ages:
            if len(children_ages) != children:
                raise ValueError("Number of children ages must match number of children")
            occupancy["childrenAges"] = children_ages
        
        # Build request payload
        payload = {
            "criteria": {
                "hotelId": hotel_ids,
                "checkInDate": check_in,
                "checkOutDate": check_out,
                "additional": {
                    "currency": currency,
                    "language": language,
                    "occupancy": occupancy,
                    "discountOnly": discount_only
                }
            }
        }
        
        return self._make_request(payload)
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
