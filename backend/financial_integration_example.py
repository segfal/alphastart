#!/usr/bin/env python3
"""
Example of how to integrate Polygon financial data with the main application
This shows how to use the PolygonFinancials class in an API route
"""
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from get_pe_and_cash_flow import PolygonFinancials, get_financial_data_for_ticker

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Financial data routes
@app.route('/api/financials/<ticker>', methods=['GET'])
def get_financials(ticker):
    """
    Get comprehensive financial data for a ticker symbol
    Returns balance sheet, cash flow, PE ratio and dividend data
    """
    data = get_financial_data_for_ticker(ticker.upper())
    return jsonify(data)

@app.route('/api/stock-price/<ticker>', methods=['GET'])
def get_stock_price(ticker):
    """Get the current stock price for a ticker"""
    try:
        financials = PolygonFinancials(ticker.upper())
        price = financials.get_current_price()
        return jsonify({
            'ticker': ticker.upper(),
            'price': price
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f"Error retrieving stock price for {ticker}"
        }), 500

@app.route('/api/pe-ratio/<ticker>', methods=['GET'])
def get_pe_ratio(ticker):
    """Get the P/E ratio for a ticker"""
    try:
        financials = PolygonFinancials(ticker.upper())
        pe_ratio = financials.get_pe_ratio()
        return jsonify({
            'ticker': ticker.upper(),
            'pe_ratio': pe_ratio
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f"Error retrieving P/E ratio for {ticker}"
        }), 500

@app.route('/api/balance-sheet/<ticker>', methods=['GET'])
def get_balance_sheet(ticker):
    """Get the balance sheet for a ticker"""
    try:
        financials = PolygonFinancials(ticker.upper())
        balance_sheet = financials.format_balance_sheet(output_format='dict')
        return jsonify({
            'ticker': ticker.upper(),
            'balance_sheet': balance_sheet
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f"Error retrieving balance sheet for {ticker}"
        }), 500

@app.route('/api/cash-flow/<ticker>', methods=['GET'])
def get_cash_flow(ticker):
    """Get the cash flow statement for a ticker"""
    try:
        financials = PolygonFinancials(ticker.upper())
        cash_flow = financials.format_cash_flow(output_format='dict')
        return jsonify({
            'ticker': ticker.upper(),
            'cash_flow': cash_flow
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f"Error retrieving cash flow for {ticker}"
        }), 500

@app.route('/api/dividend-history/<ticker>', methods=['GET'])
def get_dividend_history(ticker):
    """Get the dividend history for a ticker"""
    try:
        financials = PolygonFinancials(ticker.upper())
        dividend_history = financials.get_dividend_history()
        return jsonify({
            'ticker': ticker.upper(),
            'dividend_history': dividend_history
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f"Error retrieving dividend history for {ticker}"
        }), 500

# Example of how to integrate with your agent system
class FinancialAgent:
    def __init__(self):
        pass
        
    def analyze_financials(self, ticker):
        """Analyze the financial health of a company based on Polygon data"""
        financial_data = get_financial_data_for_ticker(ticker.upper())
        
        # Extract key metrics
        pe_ratio = financial_data.get('pe_ratio')
        debt_to_equity = financial_data.get('balance_sheet', {}).get('debt_to_equity')
        dividend_growth = financial_data.get('dividend_data', {}).get('dividend_growth')
        operating_cash_flow = financial_data.get('cash_flow', {}).get('operating_cash_flow')
        total_assets = financial_data.get('balance_sheet', {}).get('total_assets')
        total_liabilities = financial_data.get('balance_sheet', {}).get('total_liabilities')
        
        # Perform analysis
        analysis = {
            'ticker': ticker,
            'pe_ratio': pe_ratio,
            'debt_to_equity': debt_to_equity,
            'dividend_growth': dividend_growth,
            'operating_cash_flow': operating_cash_flow,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'analysis': 'This would be the analysis from your AI model'
        }
        
        return analysis

# Example of how to add this to your main.py
"""
# In main.py, add:
from get_pe_and_cash_flow import get_financial_data_for_ticker

# Add this method to your Prompts class
def get_financial_data(self, ticker: str):
    '''Get comprehensive financial data for a ticker using the Polygon API'''
    return get_financial_data_for_ticker(ticker)

# Add this route to your Flask app
@app.route('/api/financials/<ticker>', methods=['GET'])
def get_financials(ticker):
    '''Get comprehensive financial data for a ticker'''
    data = get_financial_data_for_ticker(ticker.upper())
    return jsonify(data)
"""

# For testing in standalone mode
if __name__ == "__main__":
    # Test the FinancialAgent
    agent = FinancialAgent()
    analysis = agent.analyze_financials("AAPL")
    print("Financial Analysis for AAPL:")
    for key, value in analysis.items():
        if key != 'analysis':
            print(f"{key}: {value}")
    
    # Run Flask app if you want to test the API
    # app.run(debug=True, port=5001) 