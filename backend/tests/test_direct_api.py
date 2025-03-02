#!/usr/bin/env python3
"""
Test script for the Polygon direct API implementation.
This demonstrates how to get P/E ratio and cash flow information using direct API calls.
"""
from Polygon.polygon_api import FinancialData

def main():
    # Create a financial data instance for a stock
    ticker = "AAPL"  # Change to any ticker you want to analyze
    financial_data = FinancialData(ticker)
    
    # Test the P/E ratio calculation
    print(f"\n===== P/E RATIO FOR {ticker} =====")
    pe_ratio = financial_data.get_pe_ratio()
    if pe_ratio:
        print(f"P/E Ratio: {pe_ratio:.2f}")
    else:
        print("Could not calculate P/E ratio")
    
    # Test the cash flow formatting
    print(f"\n===== CASH FLOW FOR {ticker} =====")
    financial_data.format_cash_flow()
    
    # Test the balance sheet formatting
    print(f"\n===== BALANCE SHEET FOR {ticker} =====")
    financial_data.format_balance_sheet()
    
    # Get the comprehensive financial summary
    print(f"\n===== COMPREHENSIVE FINANCIAL SUMMARY =====")
    financial_data.get_financial_summary()

if __name__ == "__main__":
    main() 