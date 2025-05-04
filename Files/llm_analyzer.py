import os
import json
import logging
from datetime import datetime, timedelta
from groq import Groq
from typing import Dict, List, Optional, Union
import hashlib
import time

logger = logging.getLogger(__name__)

MODEL = "llama-3.3-70b-versatile"
CACHE_DURATION = timedelta(hours=24)  # Cache results for 24 hours

class FlightAnalyzer:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.error("GROQ_API_KEY not found in environment variables. Please set it before using the analyzer.")
        self.client = None  # Will be initialized when needed
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
    
    def _initialize_client(self) -> bool:
        """Initialize the Groq client if API key is available"""
        if not self.api_key:
            return False
        try:
            self.client = Groq(api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            return False
    
    def _get_cache_key(self, flight_data: Dict) -> str:
        """Generate a unique cache key for the flight data"""
        data_str = json.dumps(flight_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if it exists and is not expired"""
        if cache_key in self._cache:
            timestamp = self._cache_timestamps[cache_key]
            if datetime.now() - timestamp < CACHE_DURATION:
                logger.info("Using cached analysis result")
                return self._cache[cache_key]
            else:
                # Remove expired cache
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Cache the analysis result"""
        self._cache[cache_key] = result
        self._cache_timestamps[cache_key] = datetime.now()
    
    def analyze_flight_prices(self, flight_data: Dict) -> Dict:
        """
        Analyze flight pricing data using Groq's LLM
        
        Args:
            flight_data: Dictionary containing current and historical flight prices
            
        Returns:
            Dictionary with price analysis and recommendations
        """
        try:
            # Check if API key is available and client is initialized
            if not self.api_key:
                return {
                    "error": "GROQ_API_KEY not found. Please set the GROQ_API_KEY environment variable.",
                    "help": "You can get your API key from https://console.groq.com/keys"
                }
            
            if not self.client and not self._initialize_client():
                return {
                    "error": "Failed to initialize Groq client. Please check your API key and try again."
                }
            
            # Validate input data
            if not isinstance(flight_data, dict):
                return {"error": "Invalid flight data format"}
            
            # Check cache first
            cache_key = self._get_cache_key(flight_data)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Extract data from the flight_data
            current_prices = flight_data.get('current_prices', [])
            historical_prices = flight_data.get('historical_prices', [])
            
            if not current_prices:
                return {
                    "error": "No current flight price data available for analysis"
                }
            
            # Prepare the data for LLM analysis
            current_min_price = min([flight['price'] for flight in current_prices], default=0)
            current_max_price = max([flight['price'] for flight in current_prices], default=0)
            current_avg_price = sum([flight['price'] for flight in current_prices]) / len(current_prices) if current_prices else 0
            
            # Calculate price statistics
            price_stats = self._calculate_price_statistics(current_prices, historical_prices)
            
            # Get airline distribution
            airlines = {}
            for flight in current_prices:
                airline = flight.get('airline', 'Unknown')
                if airline in airlines:
                    airlines[airline].append(flight['price'])
                else:
                    airlines[airline] = [flight['price']]
            
            airline_summary = []
            for airline, prices in airlines.items():
                airline_summary.append({
                    "airline": airline,
                    "min_price": min(prices),
                    "avg_price": sum(prices) / len(prices),
                    "max_price": max(prices),
                    "num_flights": len(prices)
                })
            
            # Create a message for the LLM
            prompt = self._create_analysis_prompt(
                current_prices, 
                historical_prices, 
                current_min_price, 
                current_max_price, 
                current_avg_price,
                airline_summary,
                price_stats
            )
            
            # Send to Groq for analysis
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a flight price analysis expert. Analyze flight pricing data and provide insights and recommendations. Respond in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            analysis_result = json.loads(response.choices[0].message.content)
            
            # Add metadata to the result
            analysis_result.update({
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "num_flights_analyzed": len(current_prices),
                    "price_range": {
                        "min": current_min_price,
                        "max": current_max_price,
                        "average": current_avg_price
                    },
                    "airlines_analyzed": len(airlines)
                }
            })
            
            # Cache the result
            self._cache_result(cache_key, analysis_result)
            
            logger.info("Successfully generated flight price analysis")
            return analysis_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {"error": "Failed to parse analysis results"}
        except Exception as e:
            logger.error(f"Error in flight price analysis: {e}")
            return {
                "error": f"Failed to analyze flight prices: {str(e)}"
            }
    
    def _calculate_price_statistics(self, current_prices: List[Dict], historical_prices: List[Dict]) -> Dict:
        """Calculate various price statistics for analysis"""
        stats = {
            "current": {
                "min": min([p['price'] for p in current_prices], default=0),
                "max": max([p['price'] for p in current_prices], default=0),
                "avg": sum([p['price'] for p in current_prices]) / len(current_prices) if current_prices else 0,
                "median": sorted([p['price'] for p in current_prices])[len(current_prices)//2] if current_prices else 0
            },
            "historical": {
                "min": min([p['price'] for p in historical_prices], default=0),
                "max": max([p['price'] for p in historical_prices], default=0),
                "avg": sum([p['price'] for p in historical_prices]) / len(historical_prices) if historical_prices else 0,
                "trend": "stable"  # Will be calculated below
            }
        }
        
        # Calculate price trend
        if len(historical_prices) >= 2:
            recent_prices = [p['price'] for p in historical_prices[-7:]]  # Last week
            if len(recent_prices) >= 2:
                price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
                if price_change > 5:
                    stats["historical"]["trend"] = "rising"
                elif price_change < -5:
                    stats["historical"]["trend"] = "falling"
        
        return stats
    
    def _create_analysis_prompt(self, current_prices: List[Dict], historical_prices: List[Dict], 
                              min_price: float, max_price: float, avg_price: float,
                              airline_summary: List[Dict], price_stats: Dict) -> str:
        """Create a prompt for the LLM with the flight data"""
        
        prompt = f"""
Please analyze the following flight pricing data and provide insights and recommendations.

CURRENT PRICES SUMMARY:
- Minimum Price: ${min_price:.2f}
- Maximum Price: ${max_price:.2f}
- Average Price: ${avg_price:.2f}
- Number of flights found: {len(current_prices)}

PRICE STATISTICS:
{json.dumps(price_stats, indent=2)}

AIRLINE BREAKDOWN:
{json.dumps(airline_summary, indent=2)}

SAMPLE OF CURRENT FLIGHT OPTIONS:
{json.dumps(current_prices[:5], indent=2)}

HISTORICAL PRICE TRENDS:
{json.dumps(historical_prices[-10:], indent=2)}

Based on this data, please provide:
1. A detailed analysis of the current pricing situation
2. A prediction of whether prices are likely to rise, fall, or remain stable
3. Recommendation on the best time to book
4. Any specific airlines that offer the best value
5. Price volatility assessment
6. Confidence level in the analysis
7. Additional insights that would help a traveler make a decision

Please format your response as a JSON object with these fields:
- analysis (string): Overall analysis of the price data
- recommendation (string): Specific recommendation for booking
- price_trend (string): One of "rising", "falling", or "stable"
- best_time_to_book (string): When the user should book
- best_value_airlines (array of strings): Airlines offering the best value
- price_volatility (string): Assessment of how much prices are fluctuating
- confidence_level (number between 0 and 1): How confident you are in this analysis
- additional_insights (array of strings): Other relevant insights
- risk_assessment (string): Assessment of booking risk
"""
        return prompt
