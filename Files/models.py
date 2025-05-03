from datetime import datetime
from app import db

class Airline(db.Model):
    """Model for airline information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<Airline {self.name}>"

class Airport(db.Model):
    """Model for airport information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False, unique=True)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<Airport {self.code} - {self.city}>"

class Flight(db.Model):
    """Model for flight information"""
    id = db.Column(db.Integer, primary_key=True)
    airline_id = db.Column(db.Integer, db.ForeignKey('airline.id'), nullable=False)
    origin_id = db.Column(db.Integer, db.ForeignKey('airport.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('airport.id'), nullable=False)
    flight_number = db.Column(db.String(20), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    airline = db.relationship('Airline', backref='flights')
    origin = db.relationship('Airport', foreign_keys=[origin_id], backref='departures')
    destination = db.relationship('Airport', foreign_keys=[destination_id], backref='arrivals')
    
    def __repr__(self):
        return f"<Flight {self.flight_number} {self.origin.code} to {self.destination.code}>"

class FlightPrice(db.Model):
    """Model for flight price data"""
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="USD")
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    available_seats = db.Column(db.Integer)
    
    # Relationship
    flight = db.relationship('Flight', backref='prices')
    
    def __repr__(self):
        return f"<FlightPrice ${self.price} for {self.flight.flight_number}>"

class PriceAnalysis(db.Model):
    """Model for LLM-generated price analysis"""
    id = db.Column(db.Integer, primary_key=True)
    origin_code = db.Column(db.String(10), nullable=False)
    destination_code = db.Column(db.String(10), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    analysis = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    price_trend = db.Column(db.String(20), nullable=False)  # rising, falling, stable
    best_time_to_book = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PriceAnalysis {self.origin_code} to {self.destination_code} on {self.travel_date}>"

class SearchHistory(db.Model):
    """Model for storing user search history"""
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(10), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    search_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    
    def __repr__(self):
        return f"<SearchHistory {self.origin} to {self.destination} on {self.travel_date}>"
