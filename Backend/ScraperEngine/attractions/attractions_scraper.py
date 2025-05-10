import requests
from bs4 import BeautifulSoup # type: ignore
import json
import logging
import os
from typing import Dict, List, Optional, Tuple
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttractionsScraper:
    def __init__(self):
        self.base_urls = [
            "https://en.wikipedia.org/wiki/List_of_tourist_attractions_in_{}",
            "https://en.wikipedia.org/wiki/Tourist_attractions_in_{}",
            "https://en.wikipedia.org/wiki/List_of_landmarks_in_{}",
            "https://en.wikipedia.org/wiki/List_of_attractions_in_{}",
            "https://en.wikipedia.org/wiki/List_of_places_of_interest_in_{}",
            "https://en.wikipedia.org/wiki/List_of_visitor_attractions_in_{}",
            "https://en.wikipedia.org/wiki/List_of_points_of_interest_in_{}",
            "https://en.wikipedia.org/wiki/List_of_tourist_attractions_in_the_{}_area",
            "https://en.wikipedia.org/wiki/List_of_tourist_attractions_in_{}_metropolitan_area",
            "https://en.wikipedia.org/wiki/List_of_tourist_attractions_in_{}_region"
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")
        os.makedirs(self.db_dir, exist_ok=True)
        
        # Special cases for city names
        self.city_mappings = {
            "san_francisco": "San_Francisco_Bay_Area",
            "new_york": "New_York_City",
            "los_angeles": "Los_Angeles_metropolitan_area",
            "chicago": "Chicago_metropolitan_area",
            "miami": "Miami_metropolitan_area",
            "houston": "Houston_metropolitan_area",
            "philadelphia": "Philadelphia_metropolitan_area",
            "phoenix": "Phoenix_metropolitan_area",
            "seattle": "Seattle_metropolitan_area",
            "denver": "Denver_metropolitan_area",
            "boston": "Boston_metropolitan_area",
            "atlanta": "Atlanta_metropolitan_area",
            "dallas": "Dallas-Fort_Worth_metropolitan_area",
            "washington_dc": "Washington,_D.C.",
            "las_vegas": "Las_Vegas_Valley",
            "orlando": "Orlando_metropolitan_area",
            "san_diego": "San_Diego_metropolitan_area",
            "portland": "Portland_metropolitan_area",
            "nashville": "Nashville_metropolitan_area",
            "austin": "Austin_metropolitan_area"
        }
        
    def _format_city_name(self, city: str) -> str:
        """
        Format city name for Wikipedia URL.
        
        Args:
            city: Raw city name
            
        Returns:
            Formatted city name
        """
        # Convert to lowercase and remove special characters
        city = city.lower()
        city = re.sub(r'[^\w\s-]', '', city)
        # Replace spaces with underscores
        city = city.strip().replace(" ", "_")
        
        # Check for special cases
        if city in self.city_mappings:
            return self.city_mappings[city]
            
        return city

    def _try_urls(self, formatted_city: str) -> Tuple[Optional[str], Optional[requests.Response]]:
        """
        Try different URL patterns until finding a valid one.
        
        Args:
            formatted_city: Formatted city name
            
        Returns:
            Tuple of (successful URL, response object)
        """
        for base_url in self.base_urls:
            url = base_url.format(formatted_city)
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    return url, response
            except requests.exceptions.RequestException:
                continue
        return None, None

    def scrape_attractions(self, city: str) -> List[Dict]:
        """
        Scrape tourist attractions for a given city from Wikipedia.
        
        Args:
            city: City name (will be formatted for Wikipedia URL)
            
        Returns:
            List of attractions with details
        """
        try:
            # Format city name for Wikipedia URL
            formatted_city = self._format_city_name(city)
            
            # Try different URL patterns
            url, response = self._try_urls(formatted_city)
            if not url or not response:
                logger.error(f"No valid Wikipedia page found for {city}")
                return []
            
            logger.info(f"Scraping attractions for {city} from {url}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            attractions = []
            
            # Find the main content div
            content = soup.find('div', {'id': 'mw-content-text'})
            if not content:
                logger.warning(f"No content found for {city}")
                return []
            
            # Look for lists of attractions
            lists = content.find_all(['ul', 'ol'])
            
            for list_elem in lists:
                items = list_elem.find_all('li')
                for item in items:
                    # Skip empty items
                    if not item.text.strip():
                        continue
                        
                    # Extract attraction name and description
                    name = item.find('b')
                    if name:
                        name = name.text.strip()
                    else:
                        # Try to get the first part of the text as name
                        name = item.text.split('.')[0].strip()
                    
                    # Get description (rest of the text)
                    description = item.text.replace(name, '').strip()
                    if description.startswith('.'):
                        description = description[1:].strip()
                    
                    # Get Wikipedia link if available
                    link = None
                    link_elem = item.find('a')
                    if link_elem and 'href' in link_elem.attrs:
                        link = f"https://en.wikipedia.org{link_elem['href']}"
                    
                    # Get image URL if available
                    image_url = None
                    img_elem = item.find('img')
                    if img_elem and 'src' in img_elem.attrs:
                        image_url = img_elem['src']
                        if image_url.startswith('//'):
                            image_url = f"https:{image_url}"
                    
                    attraction = {
                        'name': name,
                        'description': description,
                        'link': link,
                        'image_url': image_url,
                        'city': city
                    }
                    
                    attractions.append(attraction)
            
            # Save to JSON file
            self._save_to_json(attractions, city)
            
            logger.info(f"Found {len(attractions)} attractions for {city}")
            return attractions
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Wikipedia: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def _save_to_json(self, attractions: List[Dict], city: str) -> None:
        """
        Save attractions data to JSON file.
        
        Args:
            attractions: List of attraction data
            city: City name for the filename
        """
        try:
            # Format filename
            filename = f"attractions_{city.lower().replace(' ', '_')}.json"
            filepath = os.path.join(self.db_dir, filename)
            
            # Read existing data if file exists
            existing_data = []
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    logger.warning(f"Could not read existing JSON file {filename}, starting fresh")
            
            # Combine existing and new data
            combined_data = existing_data + attractions
            
            # Write the combined data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(attractions)} attractions to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to JSON: {str(e)}")
            raise
    
    def get_attractions(self, city: str) -> List[Dict]:
        """
        Get attractions for a city, either from cache or by scraping.
        
        Args:
            city: City name
            
        Returns:
            List of attractions
        """
        try:
            # Check if we have cached data
            filename = f"attractions_{city.lower().replace(' ', '_')}.json"
            filepath = os.path.join(self.db_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # If no cached data, scrape it
            return self.scrape_attractions(city)
            
        except Exception as e:
            logger.error(f"Error getting attractions: {str(e)}")
            raise 