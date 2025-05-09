from fastapi import FastAPI, Query, HTTPException
from visa.passportindex_scraper import PassportIndexVisaScraper
from hotels.booking_scraper import BookingScraper
import uvicorn

app = FastAPI(
    title="FlightME Scraper API",
    description="API for fetching visa requirements and hotel information",
    version="1.0.0"
)

scraper = PassportIndexVisaScraper()

@app.get("/visa-requirements/")
async def get_visa_requirements(
    nationality: str = Query(..., description="Full country name (e.g., 'United States', 'India')"),
    destination: str = Query(..., description="Full country name (e.g., 'United Kingdom', 'Japan')"),
    code_type: str = Query("full", description="'full' for full country names, 'iso2' for ISO codes")
):
    """
    Get visa requirements between two countries.
    
    Parameters:
    - nationality: Full country name (e.g., 'United States', 'India')
    - destination: Full country name (e.g., 'United Kingdom', 'Japan')
    - code_type: 'full' for full country names, 'iso2' for ISO codes (default: 'full')
    
    Returns:
    - JSON object containing nationality, destination, and visa requirement
    """
    try:
        result = scraper.fetch(nationality=nationality, destination=destination, code_type=code_type)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/hotels/")
async def get_hotels(
    location: str = Query(..., description="City or location to search for hotels (e.g., 'Paris', 'New York')")
):
    """
    Get hotel information for a specific location.
    
    Parameters:
    - location: City or location to search for hotels
    
    Returns:
    - JSON array containing hotel information including name, price, rating, and booking link
    """
    try:
        hotel_scraper = BookingScraper(location)
        hotels = hotel_scraper.fetch_hotels()
        return hotels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching hotels: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
