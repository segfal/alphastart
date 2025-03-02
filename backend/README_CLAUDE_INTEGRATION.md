# Claude Integration for Financial Data Retrieval

This document outlines the integration of Claude AI into the stock analysis service to dynamically retrieve financial data without relying on hardcoded values.

## Overview

We've enhanced the stock analysis service to use Claude AI for retrieving:

1. Similar companies in the same industry as a given ticker
2. Current stock prices when API data is unavailable
3. Industry P/E ratios when peer company data is insufficient

## Implementation Details

### 1. Similar Companies Retrieval

The `StockAnalyzer` class now includes a `get_similar_companies` method that:
- Uses Claude to identify peer companies based on the company name and industry
- Cleans and validates the response to ensure only valid ticker symbols are returned
- Returns a list of similar companies for further analysis

### 2. Current Price Retrieval

The `get_current_price` method in `PolygonFinancials` now:
- Attempts multiple API approaches to retrieve the current price
- Falls back to Claude when API data is unavailable
- Uses regex to extract numeric values from Claude's response

### 3. Industry P/E Ratio Calculation

The `get_industry_pe_ratio` method now:
- Retrieves similar companies using the Claude-powered method
- Calculates the average P/E ratio of peer companies
- Falls back to Claude for industry average P/E when peer data is insufficient

## Testing

A test script (`test_claude_integration.py`) has been created to verify the functionality of:
- Similar companies retrieval
- Current price retrieval using Claude
- Industry P/E ratio calculation
- P/E ratio calculation
- Financial summary generation

## Usage

To use the Claude integration:

1. Ensure the `ANTHROPIC_API_KEY` environment variable is set
2. Initialize the `StockAnalyzer` with an Anthropic client:
   ```python
   from anthropic import Anthropic
   
   anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
   analyzer = StockAnalyzer(anthropic_client)
   ```

3. Pass the analyzer to the `PolygonFinancials` class:
   ```python
   financials = PolygonFinancials(ticker, POLYGON_API_KEY, analyzer)
   ```

4. Use the enhanced methods:
   ```python
   similar_companies = analyzer.get_similar_companies(ticker)
   current_price = financials.get_current_price()
   industry_pe = financials.get_industry_pe_ratio()
   financial_data = financials.get_financial_data_for_ticker()
   ```

## Benefits

- **Dynamic Data**: No more hardcoded values for peer companies, prices, or P/E ratios
- **Up-to-date Information**: Claude provides current market data when APIs fail
- **Improved Accuracy**: Better industry comparisons with relevant peer companies
- **Fallback Mechanism**: Multiple approaches ensure data availability

## Limitations

- Balance sheet and cash flow data still rely on API availability
- Claude responses may occasionally require parsing to extract numeric values
- API rate limits may apply to both Polygon and Anthropic APIs 