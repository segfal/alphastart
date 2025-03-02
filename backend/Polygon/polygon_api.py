import os
from polygon import RESTClient
from polygon.rest.models import BalanceSheet, IncomeStatement, CashFlowStatement
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import json
import requests
load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

client = RESTClient(api_key=POLYGON_API_KEY)


class FinancialData:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.api_key = POLYGON_API_KEY

    def get_financial_data(self):
        return client.get_aggs(ticker=self.ticker, multiplier=1, timespan="minute", from_="2024-01-01", to="2024-01-02", limit=10)
    
    def get_financial_data_for_date(self, date: str):
        return client.get_aggs(ticker=self.ticker, multiplier=1, timespan="minute", from_=date, to=date, limit=10)
    
    def get_financial_data_for_date_range(self, start_date: str, end_date: str):
        return client.get_aggs(ticker=self.ticker, multiplier=1, timespan="minute", from_=start_date, to=end_date, limit=10)
    
    def get_financial_data_for_date_range_with_limit(self, start_date: str, end_date: str, limit: int):
        return client.get_aggs(ticker=self.ticker, multiplier=1, timespan="minute", from_=start_date, to=end_date, limit=limit)
    
    def get_financial_data_for_date_range_with_limit_and_offset(self, start_date: str, end_date: str, limit: int, offset: int):
        return client.get_aggs(ticker=self.ticker, multiplier=1, timespan="minute", from_=start_date, to=end_date, limit=limit, offset=offset)
    
    def get_stock_financials(self, statement_type="BALANCE_SHEET", limit=1):
        """Get the company's financial statement data from Polygon API.
        
        Args:
            statement_type: Type of financial statement ("BALANCE_SHEET", "INCOME_STATEMENT", "CASH_FLOW_STATEMENT")
            limit: Number of reports to retrieve
            
        Returns:
            Financial statement data or None if an error occurs
        """
        try:
            return client.get_stock_financials(
                ticker=self.ticker,
                limit=limit,
                financial_statement=statement_type
            )
        except Exception as e:
            print(f"Error fetching {statement_type}: {e}")
            return None
    
    def get_vx_financials(self, filing_date=None):
        """Get detailed financial data using the vx API endpoint.
        
        Args:
            filing_date: Optional filing date in YYYY-MM-DD format to filter results
            
        Returns:
            List of financial data objects
        """
        try:
            params = {"ticker": self.ticker}
            if filing_date:
                params["filing_date"] = filing_date
                
            financials = []
            for f in client.vx.list_stock_financials(**params):
                financials.append(f)
            return financials
        except Exception as e:
            print(f"Error fetching vx financials: {e}")
            return []
    
    def get_financials(self, timeframe="annual", limit=1):
        """Get all financial data directly via Polygon API.
        
        This method fetches balance sheet, income statement, and cash flow in one request.
        
        Args:
            timeframe: 'annual' or 'quarterly' or 'ttm'
            limit: Number of results to retrieve
            
        Returns:
            Financial data dictionary or None if an error occurs
        """
        try:
            url = f"https://api.polygon.io/vX/reference/financials?ticker={self.ticker}&apiKey={self.api_key}&timeframe={timeframe}&limit={limit}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' not in data or not data['results']:
                print(f"No financial data found for {self.ticker}")
                return None
                
            return data['results']
        except Exception as e:
            print(f"Error fetching financial data: {e}")
            return None
    
    def get_balance_sheet(self):
        """Get the company's balance sheet data using direct API request."""
        try:
            # First try with TTM (Trailing Twelve Months)
            financials = self.get_financials(timeframe="ttm", limit=1)
            
            # If no TTM data, try annual
            if not financials:
                financials = self.get_financials(timeframe="annual", limit=1)
                
            # If still no data, try quarterly    
            if not financials:
                financials = self.get_financials(timeframe="quarterly", limit=1)
                
            if not financials:
                return None
                
            # Extract balance sheet from the first result
            first_result = financials[0]
            
            if 'financials' in first_result and 'balance_sheet' in first_result['financials']:
                return {
                    'meta': {
                        'ticker': self.ticker,
                        'period_end_date': first_result.get('end_date'),
                        'filing_date': first_result.get('filing_date'),
                        'fiscal_period': first_result.get('fiscal_period'),
                        'fiscal_year': first_result.get('fiscal_year')
                    },
                    'balance_sheet': first_result['financials']['balance_sheet']
                }
            else:
                print(f"No balance sheet data in the response for {self.ticker}")
                return None
        except Exception as e:
            print(f"Error fetching balance sheet: {e}")
            return None
    
    def get_cash_flow(self):
        """Get the company's cash flow data using direct API request."""
        try:
            # First try with TTM (Trailing Twelve Months)
            financials = self.get_financials(timeframe="ttm", limit=1)
            
            # If no TTM data, try annual
            if not financials:
                financials = self.get_financials(timeframe="annual", limit=1)
                
            # If still no data, try quarterly    
            if not financials:
                financials = self.get_financials(timeframe="quarterly", limit=1)
                
            if not financials:
                return None
                
            # Extract cash flow from the first result
            first_result = financials[0]
            
            if 'financials' in first_result and 'cash_flow_statement' in first_result['financials']:
                return {
                    'meta': {
                        'ticker': self.ticker,
                        'period_end_date': first_result.get('end_date'),
                        'filing_date': first_result.get('filing_date'),
                        'fiscal_period': first_result.get('fiscal_period'),
                        'fiscal_year': first_result.get('fiscal_year')
                    },
                    'cash_flow': first_result['financials']['cash_flow_statement']
                }
            else:
                print(f"No cash flow data in the response for {self.ticker}")
                return None
        except Exception as e:
            print(f"Error fetching cash flow: {e}")
            return None
    
    def get_income_statement(self):
        """Get the company's income statement data using direct API request."""
        try:
            # First try with TTM (Trailing Twelve Months)
            financials = self.get_financials(timeframe="ttm", limit=1)
            
            # If no TTM data, try annual
            if not financials:
                financials = self.get_financials(timeframe="annual", limit=1)
                
            # If still no data, try quarterly    
            if not financials:
                financials = self.get_financials(timeframe="quarterly", limit=1)
                
            if not financials:
                return None
                
            # Extract income statement from the first result
            first_result = financials[0]
            
            if 'financials' in first_result and 'income_statement' in first_result['financials']:
                return {
                    'meta': {
                        'ticker': self.ticker,
                        'period_end_date': first_result.get('end_date'),
                        'filing_date': first_result.get('filing_date'),
                        'fiscal_period': first_result.get('fiscal_period'),
                        'fiscal_year': first_result.get('fiscal_year')
                    },
                    'income_statement': first_result['financials']['income_statement']
                }
            else:
                print(f"No income statement data in the response for {self.ticker}")
                return None
        except Exception as e:
            print(f"Error fetching income statement: {e}")
            return None
    
    def get_current_price(self):
        """Get the latest stock price using direct API request."""
        try:
            url = f"https://api.polygon.io/v2/aggs/ticker/{self.ticker}/prev?apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' in data and data['results']:
                return data['results'][0]['c']  # Closing price
            else:
                print(f"No price data found for {self.ticker}")
                return None
        except Exception as e:
            print(f"Error fetching stock price: {e}")
            return None
    
    def get_pe_ratio(self):
        """Calculate the P/E ratio using direct API requests."""
        try:
            # Get latest stock price
            price = self.get_current_price()
            if not price:
                print("Could not get current price")
                return None
            
            # Get income statement for EPS data
            income_data = self.get_income_statement()
            if not income_data or 'income_statement' not in income_data:
                print("Could not get income statement data")
                return None
            
            # Extract diluted EPS from income statement
            income_stmt = income_data['income_statement']
            eps = None
            
            # Try diluted earnings per share first
            if 'diluted_earnings_per_share' in income_stmt:
                eps_data = income_stmt['diluted_earnings_per_share']
                if eps_data and 'value' in eps_data:
                    eps = eps_data['value']
            
            # Fall back to basic EPS if diluted not available
            if eps is None and 'basic_earnings_per_share' in income_stmt:
                eps_data = income_stmt['basic_earnings_per_share']
                if eps_data and 'value' in eps_data:
                    eps = eps_data['value']
            
            # Calculate P/E ratio if we have both price and EPS
            if eps and eps > 0:
                pe_ratio = price / eps
                return pe_ratio
            else:
                print(f"Unable to calculate P/E ratio: Price={price}, EPS={eps}")
                return None
        except Exception as e:
            print(f"Error calculating P/E ratio: {e}")
            return None
    
    def format_balance_sheet(self, output_format='print'):
        """Format the balance sheet data for better readability.
        
        Args:
            output_format: 'print' to display or 'dict' to return as dictionary
            
        Returns:
            Formatted balance sheet data or None if error
        """
        balance_sheet_data = self.get_balance_sheet()
        if not balance_sheet_data:
            return None
        
        # Extract the balance sheet data
        meta = balance_sheet_data['meta']
        bs = balance_sheet_data['balance_sheet']
        
        # Create a formatted dictionary
        formatted = {
            'ticker': meta['ticker'],
            'period_end_date': meta['period_end_date'],
            'filing_date': meta['filing_date'],
            'fiscal_period': meta['fiscal_period'],
            'fiscal_year': meta['fiscal_year'],
            'assets': {},
            'liabilities': {},
            'equity': {}
        }
        
        # Extract asset data
        if 'assets' in bs and 'value' in bs['assets']:
            formatted['assets']['total_assets'] = bs['assets']['value']
        
        if 'current_assets' in bs and 'value' in bs['current_assets']:
            formatted['assets']['current_assets'] = bs['current_assets']['value']
        
        if 'noncurrent_assets' in bs and 'value' in bs['noncurrent_assets']:
            formatted['assets']['noncurrent_assets'] = bs['noncurrent_assets']['value']
        
        if 'cash' in bs and 'value' in bs['cash']:
            formatted['assets']['cash'] = bs['cash']['value']
        
        if 'inventory' in bs and 'value' in bs['inventory']:
            formatted['assets']['inventory'] = bs['inventory']['value']
        
        # Extract liability data
        if 'liabilities' in bs and 'value' in bs['liabilities']:
            formatted['liabilities']['total_liabilities'] = bs['liabilities']['value']
        
        if 'current_liabilities' in bs and 'value' in bs['current_liabilities']:
            formatted['liabilities']['current_liabilities'] = bs['current_liabilities']['value']
        
        if 'noncurrent_liabilities' in bs and 'value' in bs['noncurrent_liabilities']:
            formatted['liabilities']['noncurrent_liabilities'] = bs['noncurrent_liabilities']['value']
        
        if 'long_term_debt' in bs and 'value' in bs['long_term_debt']:
            formatted['liabilities']['long_term_debt'] = bs['long_term_debt']['value']
        
        # Extract equity data
        if 'equity' in bs and 'value' in bs['equity']:
            formatted['equity']['total_equity'] = bs['equity']['value']
        
        if 'equity_attributable_to_parent' in bs and 'value' in bs['equity_attributable_to_parent']:
            formatted['equity']['equity_attributable_to_parent'] = bs['equity_attributable_to_parent']['value']
        
        # Return or print based on output format
        if output_format == 'dict':
            return formatted
        else:
            # Print formatted balance sheet
            print(f"\n===== BALANCE SHEET FOR {formatted['ticker']} =====")
            print(f"Period End Date: {formatted['period_end_date']}")
            print(f"Filing Date: {formatted['filing_date']}")
            print(f"Fiscal Period: {formatted['fiscal_period']} {formatted['fiscal_year']}")
            
            print("\n=== ASSETS ===")
            for key, value in formatted['assets'].items():
                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
            
            print("\n=== LIABILITIES ===")
            for key, value in formatted['liabilities'].items():
                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
            
            print("\n=== EQUITY ===")
            for key, value in formatted['equity'].items():
                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
            
            # Calculate and print some ratios
            if 'total_assets' in formatted['assets'] and 'total_liabilities' in formatted['liabilities']:
                debt_ratio = formatted['liabilities']['total_liabilities'] / formatted['assets']['total_assets']
                print(f"\nDebt Ratio: {debt_ratio:.2f}")
            
            if 'total_liabilities' in formatted['liabilities'] and 'total_equity' in formatted['equity']:
                debt_to_equity = formatted['liabilities']['total_liabilities'] / formatted['equity']['total_equity']
                print(f"Debt-to-Equity Ratio: {debt_to_equity:.2f}")
            
            return None
    
    def format_cash_flow(self, output_format='print'):
        """Format the cash flow data for better readability.
        
        Args:
            output_format: 'print' to display or 'dict' to return as dictionary
            
        Returns:
            Formatted cash flow data or None if error
        """
        cash_flow_data = self.get_cash_flow()
        if not cash_flow_data:
            return None
        
        # Extract the cash flow data
        meta = cash_flow_data['meta']
        cf = cash_flow_data['cash_flow']
        
        # Create a formatted dictionary
        formatted = {
            'ticker': meta['ticker'],
            'period_end_date': meta['period_end_date'],
            'filing_date': meta['filing_date'],
            'fiscal_period': meta['fiscal_period'],
            'fiscal_year': meta['fiscal_year'],
            'operating': {},
            'investing': {},
            'financing': {},
            'total': {}
        }
        
        # Extract operating cash flow data
        if 'net_cash_flow_from_operating_activities' in cf and 'value' in cf['net_cash_flow_from_operating_activities']:
            formatted['operating']['net_cash_flow'] = cf['net_cash_flow_from_operating_activities']['value']
        
        # Extract investing cash flow data
        if 'net_cash_flow_from_investing_activities' in cf and 'value' in cf['net_cash_flow_from_investing_activities']:
            formatted['investing']['net_cash_flow'] = cf['net_cash_flow_from_investing_activities']['value']
        
        # Extract financing cash flow data
        if 'net_cash_flow_from_financing_activities' in cf and 'value' in cf['net_cash_flow_from_financing_activities']:
            formatted['financing']['net_cash_flow'] = cf['net_cash_flow_from_financing_activities']['value']
        
        # Extract total net cash flow
        if 'net_cash_flow' in cf and 'value' in cf['net_cash_flow']:
            formatted['total']['net_cash_flow'] = cf['net_cash_flow']['value']
        
        # Return or print based on output format
        if output_format == 'dict':
            return formatted
        else:
            # Print formatted cash flow statement
            print(f"\n===== CASH FLOW STATEMENT FOR {formatted['ticker']} =====")
            print(f"Period End Date: {formatted['period_end_date']}")
            print(f"Filing Date: {formatted['filing_date']}")
            print(f"Fiscal Period: {formatted['fiscal_period']} {formatted['fiscal_year']}")
            
            print("\n=== OPERATING ACTIVITIES ===")
            for key, value in formatted['operating'].items():
                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
            
            print("\n=== INVESTING ACTIVITIES ===")
            for key, value in formatted['investing'].items():
                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
            
            print("\n=== FINANCING ACTIVITIES ===")
            for key, value in formatted['financing'].items():
                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
            
            print("\n=== TOTAL CASH FLOW ===")
            for key, value in formatted['total'].items():
                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
            
            return None
    
    def get_financial_summary(self):
        """Get a comprehensive financial summary including P/E ratio, balance sheet, and cash flow."""
        # Get stock price and P/E ratio
        price = self.get_current_price()
        pe_ratio = self.get_pe_ratio()
        
        print(f"\n===== FINANCIAL SUMMARY FOR {self.ticker} =====")
        print(f"Current Stock Price: ${price:.2f}" if price else "Current Stock Price: Not available")
        print(f"P/E Ratio: {pe_ratio:.2f}" if pe_ratio else "P/E Ratio: Not available")
        
        # Display balance sheet
        print("\n--- BALANCE SHEET ---")
        self.format_balance_sheet()
        
        # Display cash flow
        print("\n--- CASH FLOW ---")
        self.format_cash_flow()
        
        return {
            'ticker': self.ticker,
            'price': price,
            'pe_ratio': pe_ratio
        }

x = FinancialData("AAPL").get_balance_sheet()


# Replace with your API key
API_KEY = POLYGON_API_KEY
TICKER = "AAPL"  # Example: Apple Inc.

# Polygon API endpoint for financials
url = f"https://api.polygon.io/vX/reference/financials?ticker={TICKER}&limit=1&apiKey={API_KEY}"

# Send the request
response = requests.get(url)
data = response.json()

# Check if results exist

TICKER = "AAPL"  # Example: Apple Inc.

# Get latest closing price
price_url = f"https://api.polygon.io/v2/aggs/ticker/{TICKER}/prev?apiKey={API_KEY}"
price_response = requests.get(price_url).json()
latest_close_price = price_response["results"][0]["c"] if "results" in price_response and price_response["results"] else None

# Get latest EPS (Earnings Per Share)
eps_url = f"https://api.polygon.io/vX/reference/financials?ticker={TICKER}&limit=1&apiKey={API_KEY}"
eps_response = requests.get(eps_url).json()
eps = eps_response.get("results", [{}])[0].get("earnings", {}).get("basic_eps", None)

# Calculate P/E Ratio
pe_ratio = round(latest_close_price / eps, 2) if latest_close_price and eps else "N/A"

# Print result
print("Latest Close Price:", latest_close_price)
print("EPS:", eps)
print("P/E Ratio:", pe_ratio)
