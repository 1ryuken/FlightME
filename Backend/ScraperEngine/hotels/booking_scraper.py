import requests
from bs4 import BeautifulSoup
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookingScraper:
    def __init__(self, location):
        self.base_url = "https://www.booking.com/searchresults.html"
        self.location = location
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }

    def fetch_hotels(self):
        try:
            params = {
                'ss': self.location,
                'rows': 10,
                'checkin': '2024-03-01',
                'checkout': '2024-03-02',
                'group_adults': 1,
                'no_rooms': 1,
                'selected_currency': 'USD'
            }
            
            logger.info(f"Fetching hotels for location: {self.location}")
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            hotels = []

            # Updated selectors for the current Booking.com structure
            hotel_blocks = soup.find_all('div', {'data-testid': 'property-card'})
            
            if not hotel_blocks:
                logger.warning("No hotel blocks found. The page structure might have changed.")
                return []

            for hotel in hotel_blocks:
                try:
                    # Get hotel name
                    name_element = hotel.find('div', {'data-testid': 'title'})
                    name = name_element.text.strip() if name_element else 'N/A'
                    
                    # Get price - trying multiple possible selectors
                    price = 'N/A'
                    price_selectors = [
                        'span[data-testid="price-and-discounted-price"]',
                        'span[data-testid="price-and-discounted-price"] span',
                        'div[data-testid="price-for-x-nights"]',
                        'span[data-testid="price-and-discounted-price"] div'
                    ]
                    
                    for selector in price_selectors:
                        price_element = hotel.select_one(selector)
                        if price_element:
                            price = price_element.text.strip()
                            # Clean up the price text
                            price = price.replace('$', '').replace(',', '').strip()
                            break
                    
                    # Get rating
                    rating_element = hotel.find('div', {'data-testid': 'review-score'})
                    rating = rating_element.text.strip() if rating_element else 'N/A'
                    
                    # Get link
                    link_element = hotel.find('a', {'data-testid': 'title-link'})
                    link = link_element['href'] if link_element else None
                    
                    if name and link:  # Only add if we have at least a name and link
                        hotels.append({
                            'name': name,
                            'price': price,
                            'rating': rating,
                            'link': f"https://www.booking.com{link}" if link else 'N/A'
                        })
                        logger.info(f"Found hotel: {name} - Price: {price}")
                except Exception as e:
                    logger.error(f"Error processing hotel block: {str(e)}")
                    continue

            if hotels:
                logger.info(f"Successfully found {len(hotels)} hotels")
                self._save_to_json(hotels)
                return hotels
            else:
                logger.warning("No hotels found in the search results")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Booking.com: {str(e)}")
            raise Exception(f"Failed to fetch hotel data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def _save_to_json(self, data, filename="hotels_data.json"):
        try:
            # Create db directory if it doesn't exist
            db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")
            os.makedirs(db_dir, exist_ok=True)
            
            file_path = os.path.join(db_dir, filename)
            
            # Read existing data if file exists
            existing_data = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    logger.warning(f"Could not read existing JSON file {filename}, starting fresh")
                    existing_data = []
            
            # Combine existing and new data
            combined_data = existing_data + data
            
            # Write the combined data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2)
            
            logger.info(f"Successfully saved {len(data)} hotels to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to JSON: {str(e)}")
            # Don't raise the exception, just log it
            # This way, even if saving fails, the API will still return the hotel data 