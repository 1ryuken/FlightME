import logging
import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import traceback

logger = logging.getLogger(__name__)

class FlightScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        """Configure and initialize the Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def close_driver(self):
        """Close the WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def get_kayak_prices(self, origin, destination, date):
        """Scrape flight prices from Kayak"""
        try:
            # Format the date for Kayak URL (YYYY-MM-DD)
            formatted_date = date.strftime("%Y-%m-%d")
            url = f"https://www.kayak.com/flights/{origin}-{destination}/{formatted_date}"
            
            logger.info(f"Scraping Kayak: {url}")
            self.driver.get(url)
            
            # Wait for the price elements to load
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='price-text']")))
            
            # Add a short random delay to avoid detection
            time.sleep(random.uniform(2.0, 4.0))
            
            # Extract flight data
            flight_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='inner-grid']")
            results = []
            
            for element in flight_elements[:10]:  # Limit to first 10 results
                try:
                    airline = element.find_element(By.CSS_SELECTOR, "div[class*='carrier-name']").text
                    price_elem = element.find_element(By.CSS_SELECTOR, "div[class*='price-text']")
                    price_text = price_elem.text.replace('$', '').replace(',', '')
                    price = float(price_text)
                    departure_time = element.find_element(By.CSS_SELECTOR, "div[class*='depart-time']").text
                    flight_duration = element.find_element(By.CSS_SELECTOR, "div[class*='duration']").text
                    
                    results.append({
                        'airline': airline,
                        'price': price,
                        'departure_time': departure_time,
                        'duration': flight_duration,
                        'source': 'Kayak'
                    })
                except (NoSuchElementException, ValueError) as e:
                    logger.warning(f"Error extracting flight data: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(results)} flights from Kayak")
            return results
        
        except TimeoutException:
            logger.error(f"Timeout while scraping Kayak for {origin} to {destination}")
            return []
        except Exception as e:
            logger.error(f"Error scraping Kayak: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def get_expedia_prices(self, origin, destination, date):
        """Scrape flight prices from Expedia"""
        try:
            # Format the date for Expedia URL (YYYY-MM-DD)
            formatted_date = date.strftime("%Y-%m-%d")
            url = f"https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{origin},to:{destination},departure:{formatted_date}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search"
            
            logger.info(f"Scraping Expedia: {url}")
            self.driver.get(url)
            
            # Wait for the price elements to load
            wait = WebDriverWait(self.driver, 30)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test-id='price-column']")))
            
            # Add a short random delay to avoid detection
            time.sleep(random.uniform(3.0, 5.0))
            
            # Extract flight data
            flight_elements = self.driver.find_elements(By.CSS_SELECTOR, "li[data-test-id='offer-listing']")
            results = []
            
            for element in flight_elements[:10]:  # Limit to first 10 results
                try:
                    airline = element.find_element(By.CSS_SELECTOR, "span[data-test-id='airline-name']").text
                    price_elem = element.find_element(By.CSS_SELECTOR, "div[data-test-id='price-column'] span.uitk-text-emphasis")
                    price_text = price_elem.text.replace('$', '').replace(',', '')
                    price = float(price_text)
                    departure_time = element.find_element(By.CSS_SELECTOR, "span[data-test-id='departure-time']").text
                    duration = element.find_element(By.CSS_SELECTOR, "div[data-test-id='journey-duration']").text
                    
                    results.append({
                        'airline': airline,
                        'price': price,
                        'departure_time': departure_time,
                        'duration': duration,
                        'source': 'Expedia'
                    })
                except (NoSuchElementException, ValueError) as e:
                    logger.warning(f"Error extracting Expedia flight data: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(results)} flights from Expedia")
            return results
        
        except TimeoutException:
            logger.error(f"Timeout while scraping Expedia for {origin} to {destination}")
            return []
        except Exception as e:
            logger.error(f"Error scraping Expedia: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def get_flight_prices(self, origin, destination, date):
        """Get flight prices from multiple sources"""
        all_results = []
        
        # Get prices from different sources
        kayak_results = self.get_kayak_prices(origin, destination, date)
        all_results.extend(kayak_results)
        
        # Add a delay between scraping different websites
        time.sleep(random.uniform(5.0, 8.0))
        
        expedia_results = self.get_expedia_prices(origin, destination, date)
        all_results.extend(expedia_results)
        
        return all_results
    
    def get_historical_prices(self, origin, destination, date_range=30):
        """Simulate historical prices for analysis
        
        In a real implementation, this would use actual historical data,
        but for demonstration we'll generate simulated historical data
        """
        today = datetime.now().date()
        results = []
        
        # Generate simulated price points for the past X days
        for i in range(date_range, 0, -1):
            past_date = today - timedelta(days=i)
            
            # Create price fluctuation pattern
            base_price = 300 + random.randint(-50, 50)
            # Add a weekly pattern (weekends more expensive)
            if past_date.weekday() >= 5:  # Weekend
                base_price += random.randint(20, 40)
            # Add a proximity factor (closer dates more expensive)
            proximity_factor = (date_range - i) / date_range
            price_adjustment = proximity_factor * random.randint(20, 100)
            
            final_price = base_price + price_adjustment
            
            results.append({
                'date': past_date.strftime('%Y-%m-%d'),
                'price': round(final_price, 2)
            })
        
        return results

def scrape_flights(origin, destination, date):
    """Function to perform the scraping for a specific route"""
    scraper = FlightScraper()
    try:
        flight_data = scraper.get_flight_prices(origin, destination, date)
        historical_data = scraper.get_historical_prices(origin, destination)
        
        return {
            'current_prices': flight_data,
            'historical_prices': historical_data
        }
    finally:
        scraper.close_driver()

#PAW3395 i really need this shit fr