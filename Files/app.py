import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('flightme.log')
    ]
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize the database
db = SQLAlchemy(model_class=Base)

def create_app():
    """Create and configure the Flask application"""
    # Create the Flask app
    app = Flask(__name__)
    
    # Validate required environment variables
    required_env_vars = ['SESSION_SECRET', 'GROQ_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
        if 'SESSION_SECRET' in missing_vars:
            logger.warning("Using development secret key - DO NOT USE IN PRODUCTION")
    
    app.secret_key = os.environ.get("SESSION_SECRET", "flightme-dev-secret")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Configure the database connection
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///flightme.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the app with the extension
    db.init_app(app)

    # Create database tables
    with app.app_context():
        try:
            # Import models here to avoid circular imports
            import models  # noqa: F401
            
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            # Don't raise the exception, but log it and continue
            # This allows the app to start even if there are database issues
            # The actual database operations will fail gracefully later

    return app

# Create the app instance
app = create_app()
