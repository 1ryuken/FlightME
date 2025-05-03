import os
import json
import logging
from datetime import datetime, timedelta
from openai import OpenAI

logger = logging.getLogger(__name__)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

class FlightAnalyzer:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)
    
    def analyze_flight_prices(self, flight_data):
        """
        Analyze flight pricing data using OpenAI GPT-4o
        
        Args:
            flight_data: Dictionary containing current and historical flight prices
            
        Returns:
            Dictionary with price analysis and recommendations
        """
        try:
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
                    "avg_price": sum(prices) / len(prices)
                })
            
            # Create a message for the LLM
            prompt = self._create_analysis_prompt(
                current_prices, 
                historical_prices, 
                current_min_price, 
                current_max_price, 
                current_avg_price,
                airline_summary
            )
            
            # Send to OpenAI for analysis
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a flight price analysis expert. Analyze flight pricing data and provide insights and recommendations. Respond in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )
            
            analysis_result = json.loads(response.choices[0].message.content)
            logger.info("Successfully generated flight price analysis")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in flight price analysis: {e}")
            return {
                "error": f"Failed to analyze flight prices: {str(e)}"
            }
    
    def _create_analysis_prompt(self, current_prices, historical_prices, min_price, max_price, avg_price, airline_summary):
        """Create a prompt for the LLM with the flight data"""
        
        prompt = f"""
Please analyze the following flight pricing data and provide insights and recommendations.

CURRENT PRICES SUMMARY:
- Minimum Price: ${min_price:.2f}
- Maximum Price: ${max_price:.2f}
- Average Price: ${avg_price:.2f}
- Number of flights found: {len(current_prices)}

AIRLINE BREAKDOWN:
{json.dumps(airline_summary, indent=2)}

SAMPLE OF CURRENT FLIGHT OPTIONS:
{json.dumps(current_prices[:5], indent=2)}

HISTORICAL PRICE TRENDS:
{json.dumps(historical_prices[-10:], indent=2)}

Based on this data, please provide:
1. A brief analysis of the current pricing situation
2. A prediction of whether prices are likely to rise, fall, or remain stable
3. Recommendation on the best time to book
4. Any specific airlines that offer the best value
5. Other relevant insights that would help a traveler make a decision

Please format your response as a JSON object with these fields:
- analysis (string): Overall analysis of the price data
- recommendation (string): Specific recommendation for booking
- price_trend (string): One of "rising", "falling", or "stable"
- best_time_to_book (string): When the user should book
- best_value_airlines (array of strings): Airlines offering the best value
- price_volatility (string): Assessment of how much prices are fluctuating
- confidence_level (number between 0 and 1): How confident you are in this analysis
"""
        return prompt
