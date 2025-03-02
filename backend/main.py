#!/usr/bin/env python3
"""
Main application file for the stock analysis service.
Provides API endpoints and AI-powered analysis of stock data.
"""
import os
from typing import Dict, Any, List
import anthropic
from flask import Flask, jsonify
from flask_cors import CORS
from polygon import RESTClient
from dotenv import load_dotenv

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

class StockAnalyzer:
    """
    Handles AI-powered analysis of stock data using Claude API.
    """
    def __init__(self, ai_client: anthropic.Anthropic):
        self.ai_client = ai_client

    def _get_ai_response(self, prompt: str) -> str:
        """
        Get a response from the AI model.
        
        Args:
            prompt: The prompt to send to the AI
            
        Returns:
            The AI's response text
        """
        response = self.ai_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def get_ticker_symbol(self, company: str) -> str:
        """Get the ticker symbol for a company name."""
        prompt = f"What is the ticker symbol of {company} and only return the ticker symbol"
        return self._get_ai_response(prompt)

    def get_company_name(self, ticker: str) -> str:
        """Get the company name for a ticker symbol."""
        prompt = f"What is the name of {ticker} and only return the company name"
        return self._get_ai_response(prompt)

    def get_company_description(self, ticker: str) -> str:
        """Get a description of the company."""
        prompt = f"What is the description of {ticker} and only return the company description"
        return self._get_ai_response(prompt)

    def get_company_industry(self, ticker: str) -> str:
        """Get the industry classification for a company."""
        prompt = f"What is the industry of {ticker} and only return the company industry"
        return self._get_ai_response(prompt)

    def get_morning_star_rating(self, ticker: str) -> str:
        """Get the Morningstar rating (1-5) for a company."""
        prompt = f"What is the Morningstar rating for {ticker}? Please only return the numerical rating (1-5) with no additional text or explanation."
        return self._get_ai_response(prompt)

    def get_moody_rating(self, ticker: str) -> str:
        """Get the Moody's credit rating for a company."""
        prompt = f"What is the Moody's credit rating for {ticker}? Please only return the numerical value or letter grade (e.g. Aaa, Aa1, A2, etc) with no additional text or explanation."
        return self._get_ai_response(prompt)

    def analyze_risk(self, ticker: str) -> str:
        """
        Analyze the risk level of a stock based on ratings.
        Returns risk assessment and investment recommendation.
        """
        moody_rating = self.get_moody_rating(ticker)
        morning_star_rating = self.get_morning_star_rating(ticker)
        
        risk_prompt = f"""What is the risk of {ticker} and only return the risk, based on the moody rating and the morning star rating\n
        Moody Rating: {moody_rating}
        Morning Star Rating: {morning_star_rating}
        """
        risk_assessment = self._get_ai_response(risk_prompt)

        if risk_assessment in ["high", "medium"]:
            return risk_assessment

        investment_prompt = f"Since the risk is not high or medium, should we invest in {ticker}? and only return yes or no and explain why you think so"
        return self._get_ai_response(investment_prompt)

    def analyze_financials(self, ticker: str) -> str:
        """
        Perform comprehensive financial analysis of a stock.
        Returns investment recommendation based on financial metrics.
        """
        financial_data = get_financial_data_for_ticker(ticker, self)
        
        # Extract and format financial metrics
        metrics = self._format_financial_metrics(financial_data)
        
        analysis_prompt = self._create_financial_analysis_prompt(ticker, metrics)
        return self._get_ai_response(analysis_prompt)

    def _format_financial_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, str]:
        """Format financial metrics for analysis."""
        metrics = {
            'pe_ratio': financial_data.get('pe_ratio'),
            'industry_pe_ratio': financial_data.get('industry_pe_ratio'),
            'pe_relative_to_industry': financial_data.get('pe_relative_to_industry'),
            'debt_to_equity': financial_data.get('balance_sheet', {}).get('debt_to_equity'),
            'dividend_growth': financial_data.get('dividend_data', {}).get('dividend_growth'),
            'operating_cash_flow': financial_data.get('cash_flow', {}).get('operating_cash_flow'),
            'total_assets': financial_data.get('balance_sheet', {}).get('total_assets'),
            'total_liabilities': financial_data.get('balance_sheet', {}).get('total_liabilities')
        }

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
        company_name = self.get_company_name(ticker)
        industry = self.get_company_industry(ticker)
        
        prompt = f"""I need to find {count} similar publicly traded companies that are competitors or peers to {company_name} ({ticker}) in the {industry} industry.
        
        Please provide only the ticker symbols of these companies in a comma-separated list.
        Do not include {ticker} itself in the list.
        Only include major publicly traded companies with valid ticker symbols.
        Do not include any explanation or additional text, just the comma-separated list of tickers.
        """
        
        response = self._get_ai_response(prompt)
        
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
    data = {
        'ticker': ticker,
        'company_name': analyzer.get_company_name(ticker),
        'description': analyzer.get_company_description(ticker),
        'industry': analyzer.get_company_industry(ticker),
        'risk': analyzer.analyze_risk(ticker)
    }
    return jsonify(data)

@app.route('/api/financials/<ticker>', methods=['GET'])
def get_financials(ticker: str):
    """Get comprehensive financial data for a stock."""
    data = get_financial_data_for_ticker(ticker.upper())
    return jsonify(data)

@app.route('/api/news/<ticker>', methods=['GET'])
def get_news(ticker: str):
    """Get recent news articles about a stock."""
    news = get_news_from_motley_fool(ticker)
    return jsonify(news)

@app.route('/api/financial-analysis/<ticker>', methods=['GET'])
def get_financial_analysis(ticker: str):
    """Get AI-powered financial analysis of a stock."""
    analysis = analyzer.analyze_financials(ticker.upper())
    return jsonify({'ticker': ticker, 'analysis': analysis})

if __name__ == "__main__":
    # For testing
    test_ticker = "AAPL"
    print(analyzer.analyze_risk(test_ticker))
    
    # Run Flask app
    app.run(debug=True, port=5001)