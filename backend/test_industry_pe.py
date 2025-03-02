#!/usr/bin/env python3
"""
Test script to verify the industry P/E ratio functionality.
"""
from get_pe_and_cash_flow import PolygonFinancials

def test_industry_pe(ticker):
    """Test the industry P/E ratio functionality for a given ticker."""
    print(f"Testing industry P/E ratio for {ticker}...")
    
    # Create financial data instance
    financials = PolygonFinancials(ticker)
    
    # Get company details
    company_details = financials.get_ticker_details()
    company_name = company_details.get('name', ticker)
    print(f"Company: {company_name} ({ticker})")
    
    # Get SIC code and industry peers
    sic_code = company_details.get('sic_code')
    print(f"SIC Code: {sic_code}")
    
    # Get industry peers
    peers = financials.get_industry_peers()
    print(f"Found {len(peers)} industry peers: {', '.join(peers[:5])}{'...' if len(peers) > 5 else ''}")
    
    # Get P/E ratio
    pe_ratio = financials.get_pe_ratio()
    print(f"P/E Ratio: {pe_ratio:.2f}" if pe_ratio else "P/E Ratio: Not available")
    
    # Get industry P/E ratio
    industry_pe = financials.get_industry_pe_ratio(max_peers=5)  # Limit to 5 peers for faster testing
    print(f"Industry P/E Ratio: {industry_pe:.2f}" if industry_pe else "Industry P/E Ratio: Not available")
    
    # Calculate comparison
    if pe_ratio and industry_pe:
        pe_comparison = (pe_ratio / industry_pe - 1) * 100
        if pe_comparison > 0:
            print(f"P/E Comparison: {pe_ratio:.2f} is {pe_comparison:.1f}% higher than industry average of {industry_pe:.2f}")
        else:
            print(f"P/E Comparison: {pe_ratio:.2f} is {abs(pe_comparison):.1f}% lower than industry average of {industry_pe:.2f}")
    
    return {
        'ticker': ticker,
        'company_name': company_name,
        'pe_ratio': pe_ratio,
        'industry_pe_ratio': industry_pe,
        'peers': peers[:5] if peers else []
    }

if __name__ == "__main__":
    # Test with a few different tickers
    tickers = ["AAPL", "MSFT", "GOOGL"]
    
    for ticker in tickers:
        result = test_industry_pe(ticker)
        print("\n" + "-" * 50 + "\n") 