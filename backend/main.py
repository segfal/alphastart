#!/usr/bin/env python3
"""
Main application file for the stock analysis service.
Provides API endpoints and AI-powered analysis of stock data.
"""
import os
import time
from typing import Dict, Any, List
import anthropic
from flask import Flask, jsonify, request
from flask_cors import CORS
from polygon import RESTClient
from dotenv import load_dotenv
import threading
import functools
import re
from fuzzywuzzy import fuzz, process
import sqlite3
from datetime import datetime, timedelta
import json

from stock_news import get_news_from_motley_fool
from get_pe_and_cash_flow import get_financial_data_for_ticker, PolygonFinancials

# Load environment variables and initialize clients
load_dotenv()
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

polygon_client = RESTClient(api_key=POLYGON_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "OPTIONS"])

# SQLite database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'stock_cache.db')

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create stock search cache table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_search_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        results TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create stock info cache table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_info_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        data_type TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, data_type)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Initialize database on startup
init_db()

# Cache for stock search results (in-memory, will be replaced with SQLite)
stock_search_cache = {}
STOCK_SEARCH_CACHE_TTL = 86400  # 24 hours in seconds

class RateLimiter:
    """Simple rate limiter to prevent hitting API limits."""
    def __init__(self, max_calls: int, time_period: int):
        self.max_calls = max_calls  # Maximum number of calls allowed in the time period
        self.time_period = time_period  # Time period in seconds
        self.calls = []  # List to track timestamps of calls
        self.lock = threading.Lock()  # Lock for thread safety
    
    def acquire(self):
        """Wait until a call can be made without exceeding the rate limit."""
        with self.lock:
            now = time.time()
            # Remove timestamps older than the time period
            self.calls = [t for t in self.calls if now - t < self.time_period]
            
            # If we've reached the maximum number of calls, wait
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_period - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Update now after sleeping
                    now = time.time()
                    # Clean up calls list again
                    self.calls = [t for t in self.calls if now - t < self.time_period]
            
            # Add the current timestamp to the calls list
            self.calls.append(now)

class StockAnalyzer:
    """
    Handles AI-powered analysis of stock data using Claude API.
    Optimized to minimize API calls by combining prompts and using longer cache durations.
    """
    def __init__(self, ai_client: anthropic.Anthropic):
        self.ai_client = ai_client
        self.rate_limiter = RateLimiter(max_calls=3, time_period=60)  # More conservative rate limit
        self.cache = {}  # Simple cache to store responses
        self.cache_ttl = 24 * 3600  # Increase cache TTL to 24 hours for most queries
    
    def _cache_key(self, method: str, params: tuple) -> str:
        """Generate a cache key from method name and parameters."""
        return f"{method}:{':'.join(str(p) for p in params)}"
    
    def _cached_api_call(self, method_name: str, prompt: str, cache_ttl: int = None) -> str:
        """Make an API call with caching and rate limiting.
        
        Args:
            method_name: Name of the method making the call (for cache key)
            prompt: The prompt to send to the AI
            cache_ttl: Cache time-to-live in seconds (defaults to self.cache_ttl)
            
        Returns:
            The AI's response text
        """
        cache_key = self._cache_key(method_name, (prompt,))
        cache_ttl = cache_ttl or self.cache_ttl
        
        # Check if we have a cached response
        if cache_key in self.cache:
            cached_time, cached_response = self.cache[cache_key]
            if time.time() - cached_time < cache_ttl:
                return cached_response
        
        # Acquire rate limit permission
        self.rate_limiter.acquire()
        
        # Make the API call
        response = self.ai_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.content[0].text
        
        # Cache the response
        self.cache[cache_key] = (time.time(), result)
        
        return result

    def get_company_info(self, ticker: str) -> dict:
        """Get all basic company information in a single API call."""
        prompt = f"""For the company with ticker {ticker}, provide the following information in a JSON format:
        1. Company name
        2. Brief description (1-2 sentences)
        3. Industry
        
        Format the response as a valid JSON object with keys: name, description, industry.
        Only return the JSON object, no other text."""
        
        try:
            response = self._cached_api_call("get_company_info", prompt)
            return json.loads(response)
        except:
            return {
                "name": f"Company {ticker}",
                "description": "Information not available",
                "industry": "Unknown"
            }

    def analyze_risk_and_financials(self, ticker: str, risk_level: str = 'moderate', financial_data: dict = None) -> dict:
        """Combined analysis of risk and financials in a single API call."""
        metrics = ""
        if financial_data:
            metrics = f"""
            Financial Metrics:
            - P/E Ratio: {financial_data.get('pe_ratio', 'N/A')}
            - Industry Average P/E: {financial_data.get('industry_pe_ratio', 'N/A')}
            - Debt-to-Equity: {financial_data.get('balance_sheet', {}).get('debt_to_equity', 'N/A')}
            - Total Assets: {financial_data.get('balance_sheet', {}).get('total_assets', 'N/A')}
            - Total Liabilities: {financial_data.get('balance_sheet', {}).get('total_liabilities', 'N/A')}"""

        prompt = f"""Analyze {ticker} stock and provide a risk assessment and investment recommendation.
        
        {metrics}
        
        The user has a {risk_level} risk tolerance level.
        
        Provide your response in JSON format with these keys:
        - risk_level: "low", "medium", or "high"
        - risk_factors: List of key risk factors (max 3)
        - recommendation: Clear investment recommendation
        - analysis: Brief analysis explanation
        
        Only return the JSON object, no other text."""
        
        try:
            response = self._cached_api_call("analyze_risk_and_financials", prompt)
            return json.loads(response)
        except:
            return {
                "risk_level": "medium",
                "risk_factors": ["Unable to analyze risks"],
                "recommendation": "Please consult financial advisor",
                "analysis": "Analysis not available"
            }

    def get_similar_companies(self, ticker: str, count: int = 5) -> List[str]:
        """Get similar companies with longer cache duration."""
        prompt = f"""List {count} major publicly traded competitors of {ticker}.
        Return only a comma-separated list of ticker symbols.
        No explanation needed."""
        
        response = self._cached_api_call("get_similar_companies", prompt, cache_ttl=7 * 24 * 3600)  # 7 days cache
        
        # Clean and parse the response
        peers = []
        if response:
            raw_tickers = response.strip().split(',')
            peers = [t.strip().upper() for t in raw_tickers if 1 <= len(t.strip()) <= 5 and t.strip().upper() != ticker]
        
        return peers[:count]

# API Routes
analyzer = StockAnalyzer(anthropic_client)

@app.route('/api/ticker/<ticker>', methods=['GET'])
def get_ticker_data(ticker: str):
    """Get basic information about a stock."""
    try:
        # Get risk_level from query parameters, default to 'moderate'
        risk_level = request.args.get('risk_level', 'moderate')
        
        # Check cache first
        cached_data = get_cached_stock_info(ticker, 'basic_info')
        
        if cached_data:
            # If we have cached data but need to update the risk analysis due to different risk level
            if cached_data.get('risk_level') != risk_level:
                cached_data['risk'] = analyzer.analyze_risk_and_financials(ticker, risk_level)['risk_level']
                cached_data['risk_level'] = risk_level
                # Update cache with new risk analysis
                cache_stock_info(ticker, 'basic_info', cached_data)
                return create_cache_response(cached_data, from_cache=False)
            
            return create_cache_response(cached_data, from_cache=True)
        
        # If not in cache, fetch the data
        data = analyzer.get_company_info(ticker)
        data['risk'] = analyzer.analyze_risk_and_financials(ticker)['risk_level']
        data['risk_level'] = risk_level
        
        # Cache the results
        cache_stock_info(ticker, 'basic_info', data)
            
        return create_cache_response(data, from_cache=False)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving ticker data'}), 500

@app.route('/api/financials/<ticker>', methods=['GET'])
def get_financials(ticker: str):
    """Get comprehensive financial data for a stock."""
    try:
        # Check cache first
 
        # If not in cache, fetch the data
        # get only pe ratio and balance sheet
        pe_ratio = get_pe_ratio(ticker)
        time.sleep(3)
        balance_sheet = get_balance_sheet(ticker)
        data = {
            'pe_ratio': pe_ratio,
            'balance_sheet': balance_sheet
        }
        
        
        # Cache the results
        cache_stock_info(ticker, 'financials', data)
        
        return create_cache_response(data, from_cache=False)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving financial data'}), 500

@app.route('/api/news/<ticker>', methods=['GET'])
def get_news(ticker: str):
    """Get latest news for a stock."""
    try:
        # Check cache first
        cached_data = get_cached_stock_info(ticker, 'news')
        
        if cached_data:
            return create_cache_response(cached_data, from_cache=True)
        
        # If not in cache, fetch the data
        news = analyzer.get_news(ticker.upper())
        result = {'ticker': ticker, 'news': news}
        
        # Cache the results
        cache_stock_info(ticker, 'news', result)
        
        return create_cache_response(result, from_cache=False)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving news'}), 500

@app.route('/api/pe_ratio/<ticker>', methods=['GET'])
def get_pe_ratio(ticker: str):
    """Get only the P/E ratio for a specific stock without industry comparison."""
    try:
        # Check cache first
        cached_data = get_cached_stock_info(ticker, 'pe_ratio')
        
        if cached_data:
            return create_cache_response(cached_data, from_cache=True)
        
        # Import the PolygonFinancials class directly
        from get_pe_and_cash_flow import PolygonFinancials
        
        # Create an instance without passing the analyzer to avoid industry lookups
        financials = PolygonFinancials(ticker.upper())
        
        # Get only the P/E ratio using the direct API call method
        pe_ratio = financials._get_pe_from_ticker_details()
        
        # If that fails, try the snapshot method
        if pe_ratio is None:
            pe_ratio = financials._get_pe_from_snapshot()
        
        # Create a simple response object
        data = {
            'ticker': ticker.upper(),
            'pe_ratio': pe_ratio
        }
        
        # Cache the results
        cache_stock_info(ticker, 'pe_ratio', data)
        
        return create_cache_response(data, from_cache=False)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving P/E ratio'}), 500

@app.route('/api/balance_sheet/<ticker>', methods=['GET'])
def get_balance_sheet(ticker: str):
    """Get only the balance sheet data for a specific stock."""
    try:
        # Check cache first
        cached_data = get_cached_stock_info(ticker, 'balance_sheet')
        
        if cached_data:
            return create_cache_response(cached_data, from_cache=True)
        
        # Import the PolygonFinancials class directly
        from get_pe_and_cash_flow import PolygonFinancials
        
        # Create an instance without passing the analyzer to avoid industry lookups
        financials = PolygonFinancials(ticker.upper())
        
        # Get only the balance sheet data
        balance_sheet = financials.format_balance_sheet(output_format='dict')
        
        if balance_sheet:
            # Create a simple response object
            data = {
                'ticker': ticker.upper(),
                'balance_sheet': balance_sheet
            }
            
            # Cache the results
            cache_stock_info(ticker, 'balance_sheet', data)
            
            return create_cache_response(data, from_cache=False)
        else:
            return jsonify({'error': 'No balance sheet data available', 'message': 'Could not retrieve balance sheet data'}), 404
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving balance sheet data'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint that doesn't use Anthropic API."""
    return jsonify({'status': 'ok', 'message': 'Service is running'})

@app.route('/api/search/<query>', methods=['GET'])
def search_stocks(query):
    """
    Search for stocks by ticker or company name with fuzzy matching.
    Results are cached in SQLite database to minimize API calls.
    
    Args:
        query: The search query string
        
    Returns:
        JSON response with matching stocks
    """
    # Check SQLite cache first
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Look for cached results that are less than 24 hours old
    cache_expiry = datetime.now() - timedelta(seconds=STOCK_SEARCH_CACHE_TTL)
    cursor.execute(
        "SELECT results FROM stock_search_cache WHERE query = ? AND timestamp > ?", 
        (query.lower(), cache_expiry)
    )
    
    cached_result = cursor.fetchone()
    
    if cached_result:
        print(f"Using cached search results for '{query}'")
        conn.close()
        return create_cache_response(json.loads(cached_result['results']), from_cache=True)
    
    try:
        # Call Polygon API to search for stocks
        results = polygon_client.list_tickers(
            search=query,
            market="stocks",
            active=True,
            limit=20,
            sort="ticker"
        )
        
        # Process results and add fuzzy matching scores
        stocks = []
        for ticker in results:
            # Calculate fuzzy match score
            ticker_score = fuzz.partial_ratio(query.lower(), ticker.ticker.lower())
            name_score = fuzz.partial_ratio(query.lower(), ticker.name.lower() if ticker.name else "")
            
            # Use the higher of the two scores
            match_score = max(ticker_score, name_score)
            
            stocks.append({
                "ticker": ticker.ticker,
                "name": ticker.name,
                "type": ticker.type,
                "market": ticker.market,
                "match_score": match_score
            })
        
        # Sort by match score (highest first)
        stocks.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Cache the results in SQLite
        cursor.execute(
            "INSERT INTO stock_search_cache (query, results) VALUES (?, ?)",
            (query.lower(), json.dumps(stocks))
        )
        conn.commit()
        
        conn.close()
        return create_cache_response(stocks, from_cache=False)
    
    except Exception as e:
        conn.close()
        print(f"Error searching stocks: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Helper function to cache stock info
def cache_stock_info(ticker, data_type, data):
    """Store stock information in the SQLite cache"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        import json
        # Use REPLACE to update existing entries or insert new ones
        cursor.execute(
            "REPLACE INTO stock_info_cache (ticker, data_type, data) VALUES (?, ?, ?)",
            (ticker.upper(), data_type, json.dumps(data))
        )
        
        conn.commit()
        conn.close()
        print(f"Cached {data_type} data for {ticker}")
    except Exception as e:
        print(f"Error caching stock info: {str(e)}")

# Helper function to get cached stock info
def get_cached_stock_info(ticker, data_type, max_age_seconds=86400):
    """Retrieve stock information from the SQLite cache if available and not expired"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cache_expiry = datetime.now() - timedelta(seconds=max_age_seconds)
        cursor.execute(
            "SELECT data FROM stock_info_cache WHERE ticker = ? AND data_type = ? AND timestamp > ?", 
            (ticker.upper(), data_type, cache_expiry)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            import json
            print(f"Using cached {data_type} data for {ticker}")
            return json.loads(result['data'])
        
        return None
    except Exception as e:
        print(f"Error retrieving cached stock info: {str(e)}")
        return None

# Helper function to create a response with cache headers
def create_cache_response(data, from_cache=False):
    """Create a Flask response with appropriate cache headers"""
    response = jsonify(data)
    if from_cache:
        response.headers['X-From-Cache'] = 'true'
    return response

if __name__ == "__main__":
    # Skip the initial test to avoid unnecessary API calls
    # Run Flask app
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)