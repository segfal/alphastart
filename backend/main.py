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

from stock_news import get_news_from_motley_fool
from get_pe_and_cash_flow import get_financial_data_for_ticker

# Load environment variables and initialize clients
load_dotenv()
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

polygon_client = RESTClient(api_key=POLYGON_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "OPTIONS"])

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
    """
    def __init__(self, ai_client: anthropic.Anthropic):
        self.ai_client = ai_client
        self.rate_limiter = RateLimiter(max_calls=4, time_period=60)  # 4 calls per minute to be safe
        self.cache = {}  # Simple cache to store responses
    
    def _cache_key(self, method: str, params: tuple) -> str:
        """Generate a cache key from method name and parameters."""
        return f"{method}:{':'.join(str(p) for p in params)}"
    
    def _cached_api_call(self, method_name: str, prompt: str, cache_ttl: int = 3600) -> str:
        """Make an API call with caching and rate limiting.
        
        Args:
            method_name: Name of the method making the call (for cache key)
            prompt: The prompt to send to the AI
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
            
        Returns:
            The AI's response text
        """
        cache_key = self._cache_key(method_name, (prompt,))
        
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

    def _get_ai_response(self, prompt: str) -> str:
        """
        Get a response from the AI model with rate limiting.
        
        Args:
            prompt: The prompt to send to the AI
            
        Returns:
            The AI's response text
        """
        # Use the calling method's name for the cache key
        import inspect
        caller_frame = inspect.currentframe().f_back
        caller_method = caller_frame.f_code.co_name
        
        return self._cached_api_call(caller_method, prompt)

    def get_ticker_symbol(self, company: str) -> str:
        """Get the ticker symbol for a company name."""
        prompt = f"What is the ticker symbol of {company} and only return the ticker symbol"
        return self._cached_api_call("get_ticker_symbol", prompt)

    def get_company_name(self, ticker: str) -> str:
        """Get the company name for a ticker symbol."""
        prompt = f"What is the name of {ticker} and only return the company name"
        return self._cached_api_call("get_company_name", prompt)

    def get_company_description(self, ticker: str) -> str:
        """Get a description of the company."""
        prompt = f"What is the description of {ticker} and only return the company description"
        return self._cached_api_call("get_company_description", prompt)

    def get_company_industry(self, ticker: str) -> str:
        """Get the industry classification for a company."""
        prompt = f"What is the industry of {ticker} and only return the company industry"
        return self._cached_api_call("get_company_industry", prompt)

    def get_morning_star_rating(self, ticker: str) -> str:
        """Get the Morningstar rating (1-5) for a company."""
        prompt = f"What is the Morningstar rating for {ticker}? Please only return the numerical rating (1-5) with no additional text or explanation."
        return self._cached_api_call("get_morning_star_rating", prompt)

    def get_moody_rating(self, ticker: str) -> str:
        """Get the Moody's credit rating for a company."""
        prompt = f"What is the Moody's credit rating for {ticker}? Please only return the numerical value or letter grade (e.g. Aaa, Aa1, A2, etc) with no additional text or explanation."
        return self._cached_api_call("get_moody_rating", prompt)

    def analyze_risk(self, ticker: str) -> str:
        """
        Analyze the risk level of a stock based on ratings.
        Returns risk assessment and investment recommendation.
        """
        # Combine multiple queries into a single API call to reduce rate limit usage
        combined_prompt = f"""Please provide the following information about {ticker} in a structured format:
        
        1. Moody's credit rating (e.g., Aaa, Aa1, A2, etc.)
        2. Morningstar rating (numerical value 1-5)
        3. Based on these ratings, assess the risk level (high, medium, or low)
        4. If the risk is not high or medium, would you recommend investing in {ticker}? (yes/no with brief explanation)
        
        Format your response as:
        Moody Rating: [rating]
        Morningstar Rating: [rating]
        Risk Level: [high/medium/low]
        Investment Recommendation: [yes/no with brief explanation]
        """
        
        response = self._cached_api_call("analyze_risk", combined_prompt)
        
        # Parse the response to extract just the investment recommendation
        lines = response.strip().split('\n')
        for line in lines:
            if line.startswith("Investment Recommendation:"):
                return line.replace("Investment Recommendation:", "").strip()
        
        # If we couldn't parse the response, return the whole thing
        return response

    def analyze_financials(self, ticker: str) -> str:
        """
        Perform comprehensive financial analysis of a stock.
        Returns investment recommendation based on financial metrics.
        """
        financial_data = get_financial_data_for_ticker(ticker, self)
        
        # Extract and format financial metrics
        metrics = self._format_financial_metrics(financial_data)
        
        analysis_prompt = self._create_financial_analysis_prompt(ticker, metrics)
        return self._cached_api_call("analyze_financials", analysis_prompt)

    def _format_financial_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, str]:
        """Format financial metrics for analysis."""
        # Initialize with None values to handle missing data
        metrics = {
            'pe_ratio': None,
            'industry_pe_ratio': None,
            'pe_relative_to_industry': None,
            'debt_to_equity': None,
            'dividend_growth': None,
            'operating_cash_flow': None,
            'total_assets': None,
            'total_liabilities': None
        }
        
        # Safely extract values from financial_data
        if financial_data:
            metrics['pe_ratio'] = financial_data.get('pe_ratio')
            metrics['industry_pe_ratio'] = financial_data.get('industry_pe_ratio')
            metrics['pe_relative_to_industry'] = financial_data.get('pe_relative_to_industry')
            
            # Handle nested dictionaries safely
            balance_sheet = financial_data.get('balance_sheet') or {}
            if isinstance(balance_sheet, dict):
                metrics['debt_to_equity'] = balance_sheet.get('debt_to_equity')
                metrics['total_assets'] = balance_sheet.get('total_assets')
                metrics['total_liabilities'] = balance_sheet.get('total_liabilities')
            
            # Handle dividend data safely
            dividend_data = financial_data.get('dividend_data') or {}
            if isinstance(dividend_data, dict):
                metrics['dividend_growth'] = dividend_data.get('dividend_growth')
            
            # Handle cash flow data safely
            cash_flow = financial_data.get('cash_flow') or {}
            if isinstance(cash_flow, dict):
                metrics['operating_cash_flow'] = cash_flow.get('operating_cash_flow')

        # Format currency values
        for key in ['operating_cash_flow', 'total_assets', 'total_liabilities']:
            if metrics[key]:
                metrics[f"{key}_display"] = f"${metrics[key]:,.2f}"
            else:
                metrics[f"{key}_display"] = "Not available"
                
        # Format P/E comparison
        if metrics['pe_ratio'] and metrics['industry_pe_ratio'] and metrics['pe_relative_to_industry']:
            pe_diff_percent = (metrics['pe_relative_to_industry'] - 1) * 100
            if pe_diff_percent > 0:
                metrics['pe_comparison'] = f"{pe_diff_percent:.1f}% higher than industry average"
            else:
                metrics['pe_comparison'] = f"{abs(pe_diff_percent):.1f}% lower than industry average"
        else:
            metrics['pe_comparison'] = "Not available"

        return metrics

    def _create_financial_analysis_prompt(self, ticker: str, metrics: Dict[str, Any]) -> str:
        """Create the prompt for financial analysis."""
        return f"""Analyze the financial health of {ticker} based on these financial metrics:
        - P/E Ratio: {metrics['pe_ratio']}
        - Industry Average P/E Ratio: {metrics['industry_pe_ratio']}
        - P/E Ratio Comparison: {metrics['pe_comparison']}
        - Debt-to-Equity Ratio: {metrics['debt_to_equity']}
        - Dividend Growth Over 5 Years: {'Increasing' if metrics['dividend_growth'] else 'Not consistently increasing'}
        - Operating Cash Flow: {metrics['operating_cash_flow_display']}
        - Total Assets: {metrics['total_assets_display']}
        - Total Liabilities: {metrics['total_liabilities_display']}
        
        Based on these numbers, assess the financial health of {ticker}. Is this a financially healthy company? Why or why not?
        What are the strengths and weaknesses shown in these financial metrics?
        Would you recommend this stock as an investment from a financial stability perspective? My Risk tolerance is low, so I only want to invest in companies that are financially stable.
        I am a long term investor, so I am looking for companies that are financially stable and have a history of paying dividends.
        
        In your analysis, please specifically address how the P/E ratio compares to the industry average and what that indicates about the stock's valuation.
        
        Please only return yes or no and explain why you think so.
        """

    def get_similar_companies(self, ticker: str, count: int = 5) -> List[str]:
        """
        Get a list of similar companies in the same industry as the given ticker.
        Uses Claude to identify peer companies rather than hardcoding them.
        
        Args:
            ticker: The ticker symbol to find peers for
            count: The number of peer companies to return
            
        Returns:
            List of ticker symbols for similar companies
        """
        # Use cached company name and industry to reduce API calls
        company_name = self.get_company_name(ticker)
        industry = self.get_company_industry(ticker)
        
        prompt = f"""I need to find {count} similar publicly traded companies that are competitors or peers to {company_name} ({ticker}) in the {industry} industry.
        
        Please provide only the ticker symbols of these companies in a comma-separated list.
        Do not include {ticker} itself in the list.
        Only include major publicly traded companies with valid ticker symbols.
        Do not include any explanation or additional text, just the comma-separated list of tickers.
        """
        
        response = self._cached_api_call("get_similar_companies", prompt)
        
        # Clean and parse the response
        peers = []
        if response:
            # Remove any explanatory text and just keep the tickers
            cleaned_response = response.strip()
            
            # Split by commas and clean each ticker
            raw_tickers = cleaned_response.split(',')
            for raw_ticker in raw_tickers:
                ticker_clean = raw_ticker.strip().upper()
                # Basic validation - tickers are typically 1-5 characters
                if 1 <= len(ticker_clean) <= 5 and ticker_clean != ticker:
                    peers.append(ticker_clean)
                    
                # Stop once we have enough peers
                if len(peers) >= count:
                    break
        
        return peers[:count]  # Ensure we don't return more than requested

# API Routes
analyzer = StockAnalyzer(anthropic_client)

@app.route('/api/ticker/<ticker>', methods=['GET'])
def get_ticker_data(ticker: str):
    """Get basic information about a stock."""
    try:
        data = {
            'ticker': ticker,
            'company_name': analyzer.get_company_name(ticker),
            'description': analyzer.get_company_description(ticker),
            'industry': analyzer.get_company_industry(ticker)
        }
        
        # Only include risk analysis if explicitly requested to save API calls
        if request.args.get('include_risk') == 'true':
            data['risk'] = analyzer.analyze_risk(ticker)
            
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving ticker data'}), 500

@app.route('/api/financials/<ticker>', methods=['GET'])
def get_financials(ticker: str):
    """Get comprehensive financial data for a stock."""
    try:
        data = get_financial_data_for_ticker(ticker.upper(), analyzer)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving financial data'}), 500

@app.route('/api/news/<ticker>', methods=['GET'])
def get_news(ticker: str):
    """Get recent news articles about a stock."""
    try:
        news = get_news_from_motley_fool(ticker)
        return jsonify(news)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving news data'}), 500

@app.route('/api/financial-analysis/<ticker>', methods=['GET'])
def get_financial_analysis(ticker: str):
    """Get AI-powered financial analysis of a stock."""
    try:
        analysis = analyzer.analyze_financials(ticker.upper())
        return jsonify({'ticker': ticker, 'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Error performing financial analysis'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint that doesn't use Anthropic API."""
    return jsonify({'status': 'ok', 'message': 'Service is running'})

if __name__ == "__main__":
    # Skip the initial test to avoid unnecessary API calls
    # Run Flask app
    app.run(debug=True, port=5001)