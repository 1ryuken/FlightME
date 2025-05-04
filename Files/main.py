import logging
import os
from dotenv import load_dotenv
from app import app
import routes  # noqa: F401

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('flightme.log')
        ]
    )
    
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Run the app
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=True
    )
