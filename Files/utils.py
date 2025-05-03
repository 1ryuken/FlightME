import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

def validate_airport_code(code):
    """
    Validate if the provided string is a valid airport code format
    Basic validation: 3 uppercase letters
    """
    if not code:
        return False
    
    if len(code) != 3:
        return False
    
    if not code.isalpha() or not code.isupper():
        return False
    
    return True

def parse_date(date_str):
    """
    Parse a date string to a datetime object
    Expected format: YYYY-MM-DD
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def is_valid_search(origin, destination, date):
    """
    Validate flight search parameters
    """
    # Check airport codes
    if not validate_airport_code(origin) or not validate_airport_code(destination):
        return False, "Invalid airport code. Please use 3-letter IATA codes (e.g., JFK, LAX)"
    
    # Check if origin and destination are different
    if origin == destination:
        return False, "Origin and destination cannot be the same"
    
    # Validate date
    if not date:
        return False, "Invalid date format. Please use YYYY-MM-DD"
    
    # Check if date is in the future
    today = datetime.now().date()
    if date < today:
        return False, "Date must be in the future"
    
    # Check if date is not too far in the future (e.g., 1 year max)
    max_date = today + timedelta(days=365)
    if date > max_date:
        return False, "Date cannot be more than 1 year in the future"
    
    return True, ""

def get_popular_routes():
    """
    Return a list of popular flight routes for suggestions
    """
    routes = [
        {"origin": "JFK", "destination": "LAX", "origin_city": "New York", "destination_city": "Los Angeles"},
        {"origin": "SFO", "destination": "JFK", "origin_city": "San Francisco", "destination_city": "New York"},
        {"origin": "ORD", "destination": "MIA", "origin_city": "Chicago", "destination_city": "Miami"},
        {"origin": "LAX", "destination": "LAS", "origin_city": "Los Angeles", "destination_city": "Las Vegas"},
        {"origin": "SEA", "destination": "SFO", "origin_city": "Seattle", "destination_city": "San Francisco"},
        {"origin": "ATL", "destination": "MCO", "origin_city": "Atlanta", "destination_city": "Orlando"},
        {"origin": "DFW", "destination": "DEN", "origin_city": "Dallas", "destination_city": "Denver"},
        {"origin": "BOS", "destination": "ORD", "origin_city": "Boston", "destination_city": "Chicago"},
        {"origin": "LGA", "destination": "BOS", "origin_city": "New York", "destination_city": "Boston"},
        {"origin": "IAD", "destination": "ATL", "origin_city": "Washington", "destination_city": "Atlanta"}
    ]
    
    # Return a random selection of 5 routes
    return random.sample(routes, 5)

def format_price(price):
    """Format price with dollar sign and two decimal places"""
    return f"${price:.2f}"

def get_emoji_for_trend(trend):
    """Return an appropriate emoji for a price trend"""
    if trend.lower() == "rising":
        return "↗️"
    elif trend.lower() == "falling":
        return "↘️"
    elif trend.lower() == "stable":
        return "➡️"
    else:
        return "❓"
