#!/usr/bin/env python3
"""
Test script to verify the Claude integration for financial data retrieval.
This script tests the StockAnalyzer's ability to use Claude to find similar companies,
get current prices, and retrieve industry P/E ratios.
"""

import os
import sys
from dotenv import load_dotenv
import importlib.util
import anthropic

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

if not ANTHROPIC_API_KEY:
    print("Error: ANTHROPIC_API_KEY environment variable not set")
    sys.exit(1)

if not POLYGON_API_KEY:
    print("Error: POLYGON_API_KEY environment variable not set")
    sys.exit(1)

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Import StockAnalyzer from main.py
try:
    spec = importlib.util.spec_from_file_location("main", "main.py")
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    StockAnalyzer = main_module.StockAnalyzer
except Exception as e:
    print(f"Error importing StockAnalyzer from main.py: {e}")
    sys.exit(1)

# Import PolygonFinancials
from get_pe_and_cash_flow import PolygonFinancials

def test_claude_integration(ticker):
    """Test the Claude integration for a given ticker."""
    print(f"\n{'='*50}")
    print(f"Testing Claude integration for {ticker}")
    print(f"{'='*50}")
    
    # Initialize StockAnalyzer with the Anthropic client
    analyzer = StockAnalyzer(anthropic_client)
    
    # Test getting similar companies
    print("\n1. Testing get_similar_companies:")
    similar_companies = analyzer.get_similar_companies(ticker)
    print(f"Similar companies for {ticker}: {similar_companies}")
    
    # Test getting current price using Claude
    print("\n2. Testing current price retrieval:")
    financials = PolygonFinancials(ticker, POLYGON_API_KEY, analyzer)
    current_price = financials.get_current_price()
    print(f"Current price for {ticker}: {current_price}")
    
    # Test getting industry P/E ratio using Claude
    print("\n3. Testing industry P/E ratio retrieval:")
    industry_pe = financials.get_industry_pe_ratio()
    print(f"Industry P/E ratio for {ticker}: {industry_pe}")
    
    # Test getting P/E ratio
    print("\n4. Testing P/E ratio calculation:")
    pe_ratio = financials.get_pe_ratio()
    print(f"P/E ratio for {ticker}: {pe_ratio}")
    
    # Test getting financial summary
    print("\n5. Testing financial summary:")
    financial_data = financials.get_financial_data_for_ticker()
    print(f"Financial summary for {ticker}:")
    for key, value in financial_data.items():
        print(f"  {key}: {value}")
    
    return financial_data

if __name__ == "__main__":
    # Test with a few different tickers
    tickers = ["AAPL", "MSFT", "GOOGL"]
    results = {}
    
    for ticker in tickers:
        try:
            results[ticker] = test_claude_integration(ticker)
        except Exception as e:
            print(f"Error testing {ticker}: {e}")
    
    print("\n\nSummary of results:")
    for ticker, data in results.items():
        print(f"\n{ticker}:")
        if data:
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print("  No data available") 