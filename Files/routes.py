import logging
from datetime import datetime, timedelta
import json
from flask import render_template, request, jsonify, redirect, url_for, session, flash
from app import app, db
from models import SearchHistory, PriceAnalysis
from scraper import scrape_flights
from llm_analyzer import FlightAnalyzer
from utils import is_valid_search, parse_date, get_popular_routes, format_price, get_emoji_for_trend

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Home page with flight search form"""
    popular_routes = get_popular_routes()
    return render_template('index.html', popular_routes=popular_routes)

@app.route('/about')
def about():
    """About page with information about the application"""
    return render_template('about.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle flight search form submission"""
    origin = request.form.get('origin', '').strip().upper()
    destination = request.form.get('destination', '').strip().upper()
    date_str = request.form.get('date', '')
    
    # Parse and validate date
    travel_date = parse_date(date_str)
    
    # Validate search parameters
    valid, error_message = is_valid_search(origin, destination, travel_date)
    if not valid:
        flash(error_message, 'danger')
        return redirect(url_for('index'))
    
    # Save search to history
    try:
        search_history = SearchHistory(
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            ip_address=request.remote_addr
        )
        db.session.add(search_history)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error saving search history: {e}")
        db.session.rollback()
    
    # Check if we have a recent analysis for this route and date
    existing_analysis = PriceAnalysis.query.filter_by(
        origin_code=origin, 
        destination_code=destination,
        travel_date=travel_date
    ).order_by(PriceAnalysis.created_at.desc()).first()
    
    # If we have a recent analysis (less than 24 hours old), use it
    if existing_analysis and (datetime.utcnow() - existing_analysis.created_at) < timedelta(hours=24):
        logger.info(f"Using existing analysis for {origin} to {destination} on {travel_date}")
        return redirect(url_for('search_results', origin=origin, destination=destination, date=date_str))
    
    # Otherwise, redirect to the results page which will perform the analysis
    return redirect(url_for('search_results', origin=origin, destination=destination, date=date_str))

@app.route('/search_results')
def search_results():
    """Display flight search results and analysis"""
    origin = request.args.get('origin', '').strip().upper()
    destination = request.args.get('destination', '').strip().upper()
    date_str = request.args.get('date', '')
    
    # Parse and validate date
    travel_date = parse_date(date_str)
    
    # Validate search parameters
    valid, error_message = is_valid_search(origin, destination, travel_date)
    if not valid:
        flash(error_message, 'danger')
        return redirect(url_for('index'))
    
    # Check if we have a recent analysis
    existing_analysis = PriceAnalysis.query.filter_by(
        origin_code=origin, 
        destination_code=destination,
        travel_date=travel_date
    ).order_by(PriceAnalysis.created_at.desc()).first()
    
    # If we have a recent analysis (less than 24 hours old), use it
    if existing_analysis and (datetime.utcnow() - existing_analysis.created_at) < timedelta(hours=24):
        analysis_data = {
            'analysis': existing_analysis.analysis,
            'recommendation': existing_analysis.recommendation,
            'price_trend': existing_analysis.price_trend,
            'best_time_to_book': existing_analysis.best_time_to_book,
            'price_trend_emoji': get_emoji_for_trend(existing_analysis.price_trend),
            'created_at': existing_analysis.created_at
        }
        return render_template(
            'search_results.html',
            origin=origin,
            destination=destination,
            date=travel_date.strftime('%Y-%m-%d'),
            analysis=analysis_data,
            is_loading=False
        )
    
    # If no analysis exists, render the template with loading state
    return render_template(
        'search_results.html',
        origin=origin,
        destination=destination,
        date=travel_date.strftime('%Y-%m-%d'),
        is_loading=True
    )

@app.route('/api/analyze', methods=['GET'])
def analyze_flights():
    """API endpoint to analyze flight prices"""
    origin = request.args.get('origin', '').strip().upper()
    destination = request.args.get('destination', '').strip().upper()
    date_str = request.args.get('date', '')
    
    # Parse and validate date
    travel_date = parse_date(date_str)
    
    # Validate search parameters
    valid, error_message = is_valid_search(origin, destination, travel_date)
    if not valid:
        return jsonify({'error': error_message}), 400
    
    try:
        # Check if we have a recent analysis
        existing_analysis = PriceAnalysis.query.filter_by(
            origin_code=origin, 
            destination_code=destination,
            travel_date=travel_date
        ).order_by(PriceAnalysis.created_at.desc()).first()
        
        # If we have a recent analysis (less than 24 hours old), use it
        if existing_analysis and (datetime.utcnow() - existing_analysis.created_at) < timedelta(hours=24):
            logger.info(f"Using cached analysis for {origin} to {destination} on {travel_date}")
            return jsonify({
                'analysis': existing_analysis.analysis,
                'recommendation': existing_analysis.recommendation,
                'price_trend': existing_analysis.price_trend,
                'best_time_to_book': existing_analysis.best_time_to_book,
                'price_trend_emoji': get_emoji_for_trend(existing_analysis.price_trend),
                'created_at': existing_analysis.created_at.isoformat()
            })
        
        # Scrape flight data
        logger.info(f"Scraping flight data for {origin} to {destination} on {travel_date}")
        flight_data = scrape_flights(origin, destination, travel_date)
        
        # Analyze the flight data using LLM
        analyzer = FlightAnalyzer()
        analysis_result = analyzer.analyze_flight_prices(flight_data)
        
        if 'error' in analysis_result:
            return jsonify({'error': analysis_result['error']}), 500
        
        # Save the analysis to the database
        try:
            price_analysis = PriceAnalysis(
                origin_code=origin,
                destination_code=destination,
                travel_date=travel_date,
                analysis=analysis_result.get('analysis', ''),
                recommendation=analysis_result.get('recommendation', ''),
                price_trend=analysis_result.get('price_trend', 'stable'),
                best_time_to_book=analysis_result.get('best_time_to_book', '')
            )
            db.session.add(price_analysis)
            db.session.commit()
            logger.info(f"Saved price analysis for {origin} to {destination} on {travel_date}")
        except Exception as e:
            logger.error(f"Error saving price analysis: {e}")
            db.session.rollback()
        
        # Add the emoji for the trend
        analysis_result['price_trend_emoji'] = get_emoji_for_trend(analysis_result.get('price_trend', ''))
        analysis_result['created_at'] = datetime.utcnow().isoformat()
        
        return jsonify(analysis_result)
    
    except Exception as e:
        logger.error(f"Error analyzing flights: {e}")
        return jsonify({'error': f"Failed to analyze flights: {str(e)}"}), 500

@app.route('/api/historical', methods=['GET'])
def get_historical_data():
    """API endpoint to get historical price data for charts"""
    origin = request.args.get('origin', '').strip().upper()
    destination = request.args.get('destination', '').strip().upper()
    date_str = request.args.get('date', '')
    
    # Parse and validate date
    travel_date = parse_date(date_str)
    
    # Validate search parameters
    valid, error_message = is_valid_search(origin, destination, travel_date)
    if not valid:
        return jsonify({'error': error_message}), 400
    
    try:
        # For now, just get the simulated historical data from the scraper
        flight_data = scrape_flights(origin, destination, travel_date)
        historical_prices = flight_data.get('historical_prices', [])
        
        return jsonify({
            'dates': [item['date'] for item in historical_prices],
            'prices': [item['price'] for item in historical_prices]
        })
    
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        return jsonify({'error': f"Failed to get historical data: {str(e)}"}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500
