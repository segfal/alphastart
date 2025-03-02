import os
import time
from main import StockAnalyzer, anthropic_client
from get_pe_and_cash_flow import PolygonFinancials, get_financial_data_for_ticker

def test_rate_limiting_and_caching():
    """Test the rate limiting and caching functionality."""
    print("Starting rate limiting and caching test...")
    
    # Initialize the StockAnalyzer
    analyzer = StockAnalyzer(anthropic_client)
    
    # Test 1: Multiple calls to the same method should use cache
    print("\nTest 1: Testing caching for repeated calls")
    start_time = time.time()
    result1 = analyzer.get_similar_companies("AAPL")
    time1 = time.time() - start_time
    print(f"First call took {time1:.2f} seconds")
    
    start_time = time.time()
    result2 = analyzer.get_similar_companies("AAPL")
    time2 = time.time() - start_time
    print(f"Second call took {time2:.2f} seconds")
    
    print(f"Cache hit ratio: {time2/time1:.2f}x faster")
    print(f"Similar companies for AAPL: {result2}")
    
    # Test 2: Test rate limiting by making multiple different calls
    print("\nTest 2: Testing rate limiting for multiple different calls")
    tickers = ["MSFT", "GOOGL", "AMZN", "META", "TSLA"]
    
    print("Making multiple API calls in sequence...")
    start_time = time.time()
    for ticker in tickers:
        print(f"Getting similar companies for {ticker}...")
        companies = analyzer.get_similar_companies(ticker)
        print(f"Found {len(companies)} similar companies")
    
    total_time = time.time() - start_time
    print(f"Total time for {len(tickers)} different API calls: {total_time:.2f} seconds")
    print(f"Average time per call: {total_time/len(tickers):.2f} seconds")
    
    # Test 3: Test integration with PolygonFinancials
    print("\nTest 3: Testing integration with PolygonFinancials")
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("POLYGON_API_KEY not found in environment variables")
        return
    
    # Test with a ticker that should have data
    ticker = "AAPL"
    print(f"Testing financial data retrieval for {ticker}")
    
    # Create a PolygonFinancials instance with the analyzer
    financials = PolygonFinancials(ticker, api_key, analyzer)
    
    # Test getting industry peers
    print("Getting industry peers...")
    start_time = time.time()
    peers = financials.get_industry_peers()
    time1 = time.time() - start_time
    print(f"Found {len(peers)} peers in {time1:.2f} seconds")
    
    # Test getting industry peers again (should use cache)
    print("Getting industry peers again (should use cache)...")
    start_time = time.time()
    peers = financials.get_industry_peers()
    time2 = time.time() - start_time
    print(f"Found {len(peers)} peers in {time2:.2f} seconds")
    print(f"Cache hit ratio: {time2/time1:.2f}x faster")
    
    # Test getting current price
    print("Getting current price...")
    start_time = time.time()
    price = financials.get_current_price()
    time1 = time.time() - start_time
    print(f"Current price: {price} (retrieved in {time1:.2f} seconds)")
    
    # Test getting current price again (should use cache)
    print("Getting current price again (should use cache)...")
    start_time = time.time()
    price = financials.get_current_price()
    time2 = time.time() - start_time
    print(f"Current price: {price} (retrieved in {time2:.2f} seconds)")
    print(f"Cache hit ratio: {time2/time1:.2f}x faster")
    
    # Test getting industry P/E ratio
    print("Getting industry P/E ratio...")
    start_time = time.time()
    industry_pe = financials.get_industry_pe_ratio()
    time1 = time.time() - start_time
    print(f"Industry P/E ratio: {industry_pe} (retrieved in {time1:.2f} seconds)")
    
    # Test getting industry P/E ratio again (should use cache)
    print("Getting industry P/E ratio again (should use cache)...")
    start_time = time.time()
    industry_pe = financials.get_industry_pe_ratio()
    time2 = time.time() - start_time
    print(f"Industry P/E ratio: {industry_pe} (retrieved in {time2:.2f} seconds)")
    print(f"Cache hit ratio: {time2/time1:.2f}x faster")
    
    # Test 4: Test the full financial data retrieval
    print("\nTest 4: Testing full financial data retrieval")
    start_time = time.time()
    financial_data = get_financial_data_for_ticker(ticker, api_key=api_key, analyzer=analyzer)
    total_time = time.time() - start_time
    print(f"Retrieved financial data in {total_time:.2f} seconds")
    print(f"Financial data keys: {list(financial_data.keys() if financial_data else [])}")
    
    # Print cache statistics
    print("\nCache statistics:")
    if hasattr(analyzer, 'cache'):
        print(f"Total cache entries: {len(analyzer.cache)}")
        print("Cache keys:")
        for key in analyzer.cache:
            print(f"  - {key}")
    else:
        print("Cache not available")
    
    # Print rate limiter statistics
    print("\nRate limiter statistics:")
    if hasattr(analyzer, 'rate_limiter'):
        print(f"Calls tracked: {len(analyzer.rate_limiter.calls)}")
        print(f"Max calls allowed: {analyzer.rate_limiter.max_calls}")
        print(f"Time period: {analyzer.rate_limiter.time_period} seconds")
    else:
        print("Rate limiter not available")

if __name__ == "__main__":
    test_rate_limiting_and_caching() 