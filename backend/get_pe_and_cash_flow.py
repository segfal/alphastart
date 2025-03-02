#!/usr/bin/env python3
"""
Get P/E Ratio and Cash Flow data from Polygon API
Can be used as a standalone script or imported as a module for Flask routes
"""
import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import jsonify
import importlib.util
import sys

# Load environment variables
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

class PolygonFinancials:
    def __init__(self, ticker, api_key=None, analyzer=None):
        self.ticker = ticker
        self.api_key = api_key or API_KEY
        self.analyzer = analyzer  # StockAnalyzer instance for getting similar companies
        
    def get_current_price(self):
        """Get the latest closing price for the ticker."""
        try:
            # Approach 1: Use previous day close data
            url = f"https://api.polygon.io/v2/aggs/ticker/{self.ticker}/prev?apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' in data and data['results']:
                return data['results'][0]['c']
                
            # Approach 2: Try getting the latest daily close
            today = datetime.now()
            yesterday = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            url = f"https://api.polygon.io/v1/open-close/{self.ticker}/{yesterday}?apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'close' in data:
                return data['close']
                
            # Approach 3: Try getting the latest quote
            url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{self.ticker}?apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'ticker' in data and 'lastQuote' in data['ticker'] and 'p' in data['ticker']['lastQuote']:
                return data['ticker']['lastQuote']['p']
                
            if 'ticker' in data and 'lastTrade' in data['ticker'] and 'p' in data['ticker']['lastTrade']:
                return data['ticker']['lastTrade']['p']
                
            # Approach 4: Try getting the latest daily bar
            url = f"https://api.polygon.io/v2/aggs/ticker/{self.ticker}/range/1/day/2023-01-01/{today.strftime('%Y-%m-%d')}?limit=1&apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' in data and data['results']:
                return data['results'][-1]['c']
                
            # If all API approaches fail, try to use Claude to get the price
            if self.analyzer:
                try:
                    price_prompt = f"What is the current stock price of {self.ticker}? Please respond with only the numeric value (e.g., 123.45)."
                    price_str = self.analyzer._get_ai_response(price_prompt)
                    # Extract just the number from the response
                    import re
                    price_match = re.search(r'\d+(\.\d+)?', price_str)
                    if price_match:
                        return float(price_match.group(0))
                except Exception as e:
                    print(f"Error getting price from Claude: {e}")
                
            return None
        except Exception as e:
            print(f"Error getting current price: {e}")
            return None
    
    def get_ticker_details(self):
        """Get basic information about the ticker."""
        try:
            # Try the v3 reference endpoint first
            url = f"https://api.polygon.io/v3/reference/tickers/{self.ticker}?apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' in data:
                return data['results']
                
            # If that fails, try the v1 ticker details endpoint
            url = f"https://api.polygon.io/v1/meta/symbols/{self.ticker}/company?apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'error' not in data:
                # Convert v1 format to match v3 format
                return {
                    'ticker': data.get('symbol'),
                    'name': data.get('name'),
                    'sic_code': data.get('sic'),
                    'industry': data.get('industry'),
                    'sector': data.get('sector'),
                    'description': data.get('description')
                }
                
            # If both API calls fail, return a minimal set of data
            return {
                'ticker': self.ticker,
                'name': self.ticker
            }
        except Exception as e:
            print(f"Error getting ticker details: {e}")
            # Return minimal data on error
            return {
                'ticker': self.ticker,
                'name': self.ticker
            }
    
    def get_latest_earnings(self):
        """Get the latest earnings data."""
        try:
            url = f"https://api.polygon.io/v2/reference/financials/{self.ticker}?limit=1&apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            if 'results' in data and data['results']:
                return data['results'][0]
            return None
        except Exception as e:
            print(f"Error getting earnings data: {e}")
            return None
    
    def get_dividend_history(self):
        """Get dividend history for the past 5 years and analyze growth."""
        try:
            # Get today's date and date 5 years ago
            today = datetime.now()
            five_years_ago = today - timedelta(days=5*365)
            
            # Format dates for API
            from_date = five_years_ago.strftime("%Y-%m-%d")
            to_date = today.strftime("%Y-%m-%d")
            
            # Make API request for dividends
            url = f"https://api.polygon.io/v3/reference/dividends?ticker={self.ticker}&limit=100&apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' not in data or not data['results']:
                return {
                    'has_dividends': False,
                    'message': "No dividend data found"
                }
            
            # Process dividend data
            dividends = data['results']
            dividends.sort(key=lambda x: x.get('pay_date', ''))
            
            # Group dividends by year
            dividends_by_year = {}
            for div in dividends:
                pay_date = div.get('pay_date')
                if not pay_date:
                    continue
                    
                year = pay_date.split('-')[0]
                cash_amount = div.get('cash_amount', 0)
                
                if year not in dividends_by_year:
                    dividends_by_year[year] = []
                    
                dividends_by_year[year].append(cash_amount)
            
            # Calculate annual dividend totals
            annual_dividends = {}
            for year, amounts in dividends_by_year.items():
                annual_dividends[year] = sum(amounts)
            
            # Sort years and check for growth
            years = sorted(annual_dividends.keys())
            if len(years) < 2:
                return {
                    'has_dividends': True,
                    'years_of_data': len(years),
                    'annual_dividends': annual_dividends,
                    'increasing': False,
                    'message': "Not enough years of dividend data to determine trend"
                }
                
            # Check if dividends have been increasing
            increasing = True
            for i in range(1, len(years)):
                if annual_dividends[years[i]] <= annual_dividends[years[i-1]]:
                    increasing = False
                    break
            
            return {
                'has_dividends': True,
                'years_of_data': len(years),
                'annual_dividends': annual_dividends,
                'increasing': increasing,
                'message': f"Dividends have {'increased' if increasing else 'not increased'} each year over the available data"
            }
            
        except Exception as e:
            print(f"Error getting dividend history: {e}")
            return {
                'has_dividends': False,
                'error': str(e),
                'message': "Error retrieving dividend data"
            }
    
    def get_pe_ratio(self):
        """Calculate P/E ratio using latest price and earnings."""
        try:
            # Try the raw calculation approach
            price = self.get_current_price()
            if not price:
                print("Could not get current price")
                return None
                
            # Request the stock's P/E ratio directly
            url = f"https://api.polygon.io/v3/reference/tickers/{self.ticker}?apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' in data and 'metrics' in data['results'] and 'pe_ratio' in data['results']['metrics']:
                return data['results']['metrics']['pe_ratio']
        except Exception as e:
            print(f"Could not get P/E ratio directly: {e}")
        
        # Manual calculation approach
        try:
            # Get latest earnings
            url = f"https://api.polygon.io/vX/reference/financials?ticker={self.ticker}&apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' in data and data['results'] and 'financials' in data['results'][0] and 'income_statement' in data['results'][0]['financials']:
                income_stmt = data['results'][0]['financials']['income_statement']
                
                # Try to find EPS
                eps = None
                
                # Try diluted EPS first
                if 'diluted_earnings_per_share' in income_stmt and income_stmt['diluted_earnings_per_share'] and 'value' in income_stmt['diluted_earnings_per_share']:
                    eps = income_stmt['diluted_earnings_per_share']['value']
                
                # If no diluted EPS, try basic EPS
                if eps is None and 'basic_earnings_per_share' in income_stmt and income_stmt['basic_earnings_per_share'] and 'value' in income_stmt['basic_earnings_per_share']:
                    eps = income_stmt['basic_earnings_per_share']['value']
                
                # Calculate P/E ratio if EPS is available
                if eps and eps > 0:
                    return price / eps
        except Exception as e:
            print(f"Error calculating P/E ratio: {e}")
            
        # If we get here, we couldn't calculate P/E
        print(f"Could not calculate P/E ratio for {self.ticker}")
        return None
    
    def get_financial_data(self):
        """Get comprehensive financial data."""
        try:
            url = f"https://api.polygon.io/vX/reference/financials?ticker={self.ticker}&apiKey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'results' in data and data['results']:
                return data['results'][0]
            return None
        except Exception as e:
            print(f"Error getting financial data: {e}")
            return None
    
    def format_balance_sheet(self, output_format='print'):
        """Format the balance sheet data for better readability.
        
        Args:
            output_format: 'print' to display or 'dict' to return as dictionary
            
        Returns:
            Formatted balance sheet data or None if error
        """
        financial_data = self.get_financial_data()
        if not financial_data or 'financials' not in financial_data or 'balance_sheet' not in financial_data['financials']:
            if output_format == 'print':
                print("Could not get balance sheet")
            return None
            
        bs = financial_data['financials']['balance_sheet']
        
        # Extract the balance sheet data
        total_assets = None
        total_liabilities = None
        total_equity = None
        debt_ratio = None
        debt_to_equity = None
        
        # Get assets data
        if 'assets' in bs and 'value' in bs['assets']:
            total_assets = bs['assets']['value']
            
        # Get liabilities data
        if 'liabilities' in bs and 'value' in bs['liabilities']:
            total_liabilities = bs['liabilities']['value']
            
        # Get equity data
        if 'equity' in bs and 'value' in bs['equity']:
            total_equity = bs['equity']['value']
        
        # Calculate ratios
        try:
            if total_assets and total_liabilities:
                debt_ratio = total_liabilities / total_assets
                
                if total_equity and total_equity > 0:
                    debt_to_equity = total_liabilities / total_equity
        except Exception as e:
            if output_format == 'print':
                print(f"Error calculating ratios: {e}")
                
        # Create formatted dictionary
        formatted = {
            'ticker': self.ticker,
            'period': financial_data.get('fiscal_period', 'N/A'),
            'year': financial_data.get('fiscal_year', 'N/A'),
            'end_date': financial_data.get('end_date', 'N/A'),
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'debt_ratio': debt_ratio,
            'debt_to_equity': debt_to_equity
        }
        
        # Print formatted data if requested
        if output_format == 'print':
            print(f"\n===== BALANCE SHEET FOR {self.ticker} =====")
            print(f"Period: {formatted['period']} {formatted['year']}")
            print(f"End Date: {formatted['end_date']}")
            
            print("\n=== ASSETS ===")
            if total_assets:
                print(f"Total Assets: ${total_assets:,.2f}")
            
            if 'current_assets' in bs and 'value' in bs['current_assets']:
                print(f"Current Assets: ${bs['current_assets']['value']:,.2f}")
                
            if 'noncurrent_assets' in bs and 'value' in bs['noncurrent_assets']:
                print(f"Non-current Assets: ${bs['noncurrent_assets']['value']:,.2f}")
                
            print("\n=== LIABILITIES ===")
            if total_liabilities:
                print(f"Total Liabilities: ${total_liabilities:,.2f}")
                
            if 'current_liabilities' in bs and 'value' in bs['current_liabilities']:
                print(f"Current Liabilities: ${bs['current_liabilities']['value']:,.2f}")
                
            if 'noncurrent_liabilities' in bs and 'value' in bs['noncurrent_liabilities']:
                print(f"Non-current Liabilities: ${bs['noncurrent_liabilities']['value']:,.2f}")
                
            print("\n=== EQUITY ===")
            if total_equity:
                print(f"Total Equity: ${total_equity:,.2f}")
            
            if debt_ratio is not None:
                print(f"\nDebt Ratio: {debt_ratio:.2f}")
                
            if debt_to_equity is not None:
                print(f"Debt-to-Equity Ratio: {debt_to_equity:.2f}")
        
        return formatted
    
    def format_cash_flow(self, output_format='print'):
        """Format the cash flow data for better readability.
        
        Args:
            output_format: 'print' to display or 'dict' to return as dictionary
            
        Returns:
            Formatted cash flow data or None if error
        """
        financial_data = self.get_financial_data()
        if not financial_data or 'financials' not in financial_data or 'cash_flow_statement' not in financial_data['financials']:
            if output_format == 'print':
                print("Could not get cash flow statement")
            return None
            
        cf = financial_data['financials']['cash_flow_statement']
        
        # Extract cash flow data
        op_cf = None
        inv_cf = None
        fin_cf = None
        net_cf = None
        cash_flow_to_revenue = None
        cash_flow_to_income = None
        
        # Get operating cash flow
        if 'net_cash_flow_from_operating_activities' in cf and 'value' in cf['net_cash_flow_from_operating_activities']:
            op_cf = cf['net_cash_flow_from_operating_activities']['value']
            
        # Get investing cash flow
        if 'net_cash_flow_from_investing_activities' in cf and 'value' in cf['net_cash_flow_from_investing_activities']:
            inv_cf = cf['net_cash_flow_from_investing_activities']['value']
            
        # Get financing cash flow
        if 'net_cash_flow_from_financing_activities' in cf and 'value' in cf['net_cash_flow_from_financing_activities']:
            fin_cf = cf['net_cash_flow_from_financing_activities']['value']
            
        # Get net cash flow
        if 'net_cash_flow' in cf and 'value' in cf['net_cash_flow']:
            net_cf = cf['net_cash_flow']['value']
        
        # Calculate cash flow ratios
        if op_cf is not None:
            if 'financials' in financial_data and 'income_statement' in financial_data['financials']:
                income_stmt = financial_data['financials']['income_statement']
                
                if 'revenues' in income_stmt and 'value' in income_stmt['revenues'] and income_stmt['revenues']['value'] > 0:
                    revenues = income_stmt['revenues']['value']
                    cash_flow_to_revenue = op_cf / revenues
                
                if 'net_income_loss' in income_stmt and 'value' in income_stmt['net_income_loss'] and income_stmt['net_income_loss']['value'] != 0:
                    net_income = income_stmt['net_income_loss']['value']
                    cash_flow_to_income = op_cf / net_income
        
        # Create formatted dictionary
        formatted = {
            'ticker': self.ticker,
            'period': financial_data.get('fiscal_period', 'N/A'),
            'year': financial_data.get('fiscal_year', 'N/A'),
            'end_date': financial_data.get('end_date', 'N/A'),
            'operating_cash_flow': op_cf,
            'investing_cash_flow': inv_cf,
            'financing_cash_flow': fin_cf,
            'net_cash_flow': net_cf,
            'cash_flow_to_revenue': cash_flow_to_revenue,
            'cash_flow_to_income': cash_flow_to_income
        }
        
        # Print formatted data if requested
        if output_format == 'print':
            print(f"\n===== CASH FLOW STATEMENT FOR {self.ticker} =====")
            print(f"Period: {formatted['period']} {formatted['year']}")
            print(f"End Date: {formatted['end_date']}")
            
            print("\n=== OPERATING ACTIVITIES ===")
            if op_cf is not None:
                print(f"Net Cash from Operations: ${op_cf:,.2f}")
                
            print("\n=== INVESTING ACTIVITIES ===")
            if inv_cf is not None:
                print(f"Net Cash from Investing: ${inv_cf:,.2f}")
                
            print("\n=== FINANCING ACTIVITIES ===")
            if fin_cf is not None:
                print(f"Net Cash from Financing: ${fin_cf:,.2f}")
                
            print("\n=== TOTAL CASH FLOW ===")
            if net_cf is not None:
                print(f"Net Cash Flow: ${net_cf:,.2f}")
            
            if cash_flow_to_revenue is not None:
                print(f"\nOperating Cash Flow to Revenue: {cash_flow_to_revenue:.2f}")
                
            if cash_flow_to_income is not None:
                print(f"Operating Cash Flow to Net Income: {cash_flow_to_income:.2f}")
        
        return formatted
    
    def get_industry_peers(self):
        """Get a list of peer companies in the same industry."""
        try:
            # First try to use the StockAnalyzer if available
            if self.analyzer:
                peers = self.analyzer.get_similar_companies(self.ticker)
                if peers:
                    return peers
            
            # If no analyzer or it returned no peers, try the API approaches
            ticker_details = self.get_ticker_details()
            
            if not ticker_details:
                print("Could not get ticker details")
                return []
            
            # Try multiple approaches to find peers
            peers = []
            
            # Approach 1: Use SIC code if available
            sic_code = ticker_details.get('sic_code')
            if sic_code:
                url = f"https://api.polygon.io/v3/reference/tickers?sic_code={sic_code}&active=true&limit=50&apiKey={self.api_key}"
                response = requests.get(url)
                data = response.json()
                
                if 'results' in data:
                    # Filter out the current ticker and collect peers
                    sic_peers = [item['ticker'] for item in data['results'] if item['ticker'] != self.ticker]
                    peers.extend(sic_peers)
            
            # Approach 2: Use industry classification if available
            industry = ticker_details.get('industry')
            if industry and not peers:
                url = f"https://api.polygon.io/v3/reference/tickers?industry={industry}&active=true&limit=50&apiKey={self.api_key}"
                response = requests.get(url)
                data = response.json()
                
                if 'results' in data:
                    # Filter out the current ticker and collect peers
                    industry_peers = [item['ticker'] for item in data['results'] if item['ticker'] != self.ticker]
                    peers.extend(industry_peers)
            
            # Approach 3: Use sector classification if available
            sector = ticker_details.get('sector')
            if sector and not peers:
                url = f"https://api.polygon.io/v3/reference/tickers?sector={sector}&active=true&limit=50&apiKey={self.api_key}"
                response = requests.get(url)
                data = response.json()
                
                if 'results' in data:
                    # Filter out the current ticker and collect peers
                    sector_peers = [item['ticker'] for item in data['results'] if item['ticker'] != self.ticker]
                    peers.extend(sector_peers)
            
            # If we still have no peers, try to dynamically import and use the StockAnalyzer
            if not peers and ANTHROPIC_API_KEY:
                try:
                    # Try to dynamically import the StockAnalyzer
                    if importlib.util.find_spec("main") is not None:
                        main_module = importlib.import_module("main")
                        if hasattr(main_module, "StockAnalyzer") and hasattr(main_module, "anthropic_client"):
                            temp_analyzer = main_module.StockAnalyzer(main_module.anthropic_client)
                            peers = temp_analyzer.get_similar_companies(self.ticker)
                except Exception as e:
                    print(f"Error dynamically importing StockAnalyzer: {e}")
            
            return peers
        except Exception as e:
            print(f"Error getting industry peers: {e}")
            return []
    
    def get_industry_pe_ratio(self):
        """Calculate the average P/E ratio for the industry peers."""
        try:
            peers = self.get_industry_peers()
            if not peers:
                print(f"No industry peers found for {self.ticker}")
                return None
                
            print(f"Found industry peers for {self.ticker}: {peers}")
            
            # Get P/E ratios for peers
            pe_ratios = []
            for peer in peers:
                if peer == self.ticker:  # Skip the original ticker
                    continue
                    
                peer_financials = PolygonFinancials(peer, self.api_key, self.analyzer)
                peer_pe = peer_financials.get_pe_ratio()
                
                if peer_pe and peer_pe > 0 and peer_pe < 200:  # Filter out unreasonable P/E ratios
                    print(f"P/E ratio for {peer}: {peer_pe}")
                    pe_ratios.append(peer_pe)
            
            # Calculate average P/E ratio if we have at least one valid peer
            if pe_ratios:
                avg_pe = sum(pe_ratios) / len(pe_ratios)
                print(f"Average industry P/E ratio: {avg_pe}")
                return avg_pe
                
            # If we couldn't get P/E ratios for peers, try using Claude to get industry P/E
            if self.analyzer:
                try:
                    # Get company details to identify the industry
                    company_details = self.get_ticker_details()
                    industry = None
                    if company_details:
                        if 'industry' in company_details:
                            industry = company_details['industry']
                        elif 'sector' in company_details:
                            industry = company_details['sector']
                    
                    if industry:
                        industry_pe_prompt = f"What is the current average P/E ratio for the {industry} industry? Please respond with only the numeric value (e.g., 15.7)."
                        pe_str = self.analyzer._get_ai_response(industry_pe_prompt)
                        # Extract just the number from the response
                        import re
                        pe_match = re.search(r'\d+(\.\d+)?', pe_str)
                        if pe_match:
                            return float(pe_match.group(0))
                except Exception as e:
                    print(f"Error getting industry P/E from Claude: {e}")
            
            return None
        except Exception as e:
            print(f"Error calculating industry P/E ratio: {e}")
            return None
    
    def get_financial_summary(self):
        """Print a comprehensive financial summary."""
        # Get company details
        company_details = self.get_ticker_details()
        company_name = company_details.get('name', self.ticker)
        
        # Get current price
        price = self.get_current_price()
        
        # Get P/E ratio
        pe_ratio = self.get_pe_ratio()
        
        # Get industry P/E ratio
        industry_pe = self.get_industry_pe_ratio()
        
        # Get dividend history
        dividend_history = self.get_dividend_history()
        
        # Print summary header
        print(f"\n===== FINANCIAL SUMMARY FOR {company_name} ({self.ticker}) =====")
        print(f"Current Stock Price: ${price:.2f}" if price else "Current Stock Price: Not available")
        print(f"P/E Ratio: {pe_ratio:.2f}" if pe_ratio else "P/E Ratio: Not available")
        print(f"Industry P/E Ratio: {industry_pe:.2f}" if industry_pe else "Industry P/E Ratio: Not available")
        
        if pe_ratio and industry_pe:
            pe_comparison = (pe_ratio / industry_pe - 1) * 100
            if pe_comparison > 0:
                print(f"P/E Comparison: {pe_ratio:.2f} is {pe_comparison:.1f}% higher than industry average of {industry_pe:.2f}")
            else:
                print(f"P/E Comparison: {pe_ratio:.2f} is {abs(pe_comparison):.1f}% lower than industry average of {industry_pe:.2f}")
        
        # Print dividend analysis
        print("\n=== DIVIDEND ANALYSIS ===")
        if dividend_history.get('has_dividends', False):
            print(f"Dividend History: {dividend_history.get('message', 'N/A')}")
            if 'annual_dividends' in dividend_history:
                print("Annual Dividends:")
                for year, amount in sorted(dividend_history['annual_dividends'].items()):
                    print(f"  {year}: ${amount:.4f} per share")
                
                years = len(dividend_history['annual_dividends'])
                increasing = dividend_history.get('increasing', False)
                print(f"5-Year Dividend Growth: {'Increasing' if increasing else 'Not consistently increasing'} over {years} years of data")
        else:
            print(f"Dividend History: {dividend_history.get('message', 'No dividend data found')}")
        
        # Get and format detailed financials
        balance_sheet_data = self.format_balance_sheet()
        cash_flow_data = self.format_cash_flow()
        
        # Highlight key requested metrics
        print("\n=== KEY FINANCIAL METRICS ===")
        if balance_sheet_data:
            if balance_sheet_data.get('total_assets'):
                print(f"Total Assets: ${balance_sheet_data['total_assets']:,.2f}")
            
            if balance_sheet_data.get('total_liabilities'):
                print(f"Total Liabilities: ${balance_sheet_data['total_liabilities']:,.2f}")
                
            if balance_sheet_data.get('debt_to_equity') is not None:
                print(f"Debt-to-Equity Ratio: {balance_sheet_data['debt_to_equity']:.2f}")
        
        if cash_flow_data and cash_flow_data.get('operating_cash_flow'):
            print(f"Total Cash from Operations: ${cash_flow_data['operating_cash_flow']:,.2f}")
        
        # Return summary data
        return {
            'ticker': self.ticker,
            'company_name': company_name,
            'price': price,
            'pe_ratio': pe_ratio,
            'industry_pe_ratio': industry_pe,
            'dividend_growth': dividend_history.get('increasing', False) if dividend_history.get('has_dividends', False) else None,
            'total_assets': balance_sheet_data.get('total_assets') if balance_sheet_data else None,
            'total_liabilities': balance_sheet_data.get('total_liabilities') if balance_sheet_data else None,
            'debt_to_equity': balance_sheet_data.get('debt_to_equity') if balance_sheet_data else None,
            'operating_cash_flow': cash_flow_data.get('operating_cash_flow') if cash_flow_data else None
        }

    def get_financial_data_for_agent(self):
        """Get financial data in a format suitable for the agent.
        Returns a dictionary with all the financial data without printing.
        """
        # Get company details
        company_details = self.get_ticker_details()
        company_name = company_details.get('name', self.ticker)
        
        # Get current price
        price = self.get_current_price()
        
        # Get P/E ratio
        pe_ratio = self.get_pe_ratio()
        
        # Get industry P/E ratio
        industry_pe = self.get_industry_pe_ratio()
        
        # Get dividend history
        dividend_history = self.get_dividend_history()
        
        # Get balance sheet and cash flow data
        balance_sheet_data = self.format_balance_sheet(output_format='dict')
        cash_flow_data = self.format_cash_flow(output_format='dict')
        
        # Create comprehensive financial data dictionary
        financial_data = {
            'ticker': self.ticker,
            'company_name': company_name,
            'price': price,
            'pe_ratio': pe_ratio,
            'industry_pe_ratio': industry_pe,
            'pe_relative_to_industry': (pe_ratio / industry_pe) if pe_ratio and industry_pe else None,
            'dividend_data': {
                'has_dividends': dividend_history.get('has_dividends', False),
                'dividend_growth': dividend_history.get('increasing', False) if dividend_history.get('has_dividends', False) else False,
                'years_of_data': dividend_history.get('years_of_data', 0) if dividend_history.get('has_dividends', False) else 0,
                'annual_dividends': dividend_history.get('annual_dividends', {}) if dividend_history.get('has_dividends', False) else {},
                'message': dividend_history.get('message', 'No dividend data available')
            },
            'balance_sheet': {
                'total_assets': balance_sheet_data.get('total_assets') if balance_sheet_data else None,
                'total_liabilities': balance_sheet_data.get('total_liabilities') if balance_sheet_data else None,
                'total_equity': balance_sheet_data.get('total_equity') if balance_sheet_data else None,
                'debt_ratio': balance_sheet_data.get('debt_ratio') if balance_sheet_data else None,
                'debt_to_equity': balance_sheet_data.get('debt_to_equity') if balance_sheet_data else None
            },
            'cash_flow': {
                'operating_cash_flow': cash_flow_data.get('operating_cash_flow') if cash_flow_data else None,
                'investing_cash_flow': cash_flow_data.get('investing_cash_flow') if cash_flow_data else None,
                'financing_cash_flow': cash_flow_data.get('financing_cash_flow') if cash_flow_data else None,
                'net_cash_flow': cash_flow_data.get('net_cash_flow') if cash_flow_data else None,
                'cash_flow_to_revenue': cash_flow_data.get('cash_flow_to_revenue') if cash_flow_data else None,
                'cash_flow_to_income': cash_flow_data.get('cash_flow_to_income') if cash_flow_data else None
            }
        }
        
        return financial_data

    def get_financial_data_for_ticker(self):
        """
        Get comprehensive financial data for a ticker.
        
        Returns:
            Dictionary containing financial metrics and analysis
        """
        try:
            # Get P/E ratio and industry comparison
            pe_ratio = self.get_pe_ratio()
            industry_pe = self.get_industry_pe_ratio()
            
            # Calculate P/E relative to industry
            pe_relative_to_industry = None
            if pe_ratio and industry_pe and industry_pe > 0:
                pe_relative_to_industry = pe_ratio / industry_pe
            
            # Get balance sheet data
            balance_sheet = self.format_balance_sheet(output_format='dict')
            
            # Get cash flow data
            cash_flow = self.format_cash_flow(output_format='dict')
            
            # Get dividend data
            dividend_data = self.get_dividend_history()
            
            # Compile all data
            financial_data = {
                'ticker': self.ticker,
                'pe_ratio': pe_ratio,
                'industry_pe_ratio': industry_pe,
                'pe_relative_to_industry': pe_relative_to_industry,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'dividend_data': dividend_data
            }
            
            return financial_data
        except Exception as e:
            print(f"Error getting financial data for {self.ticker}: {e}")
            return {
                'ticker': self.ticker,
                'error': str(e)
            }

# Function to use in Flask routes
def get_financial_data_for_ticker(ticker, analyzer=None):
    """Function to be used in Flask routes to get financial data for a ticker
    
    Args:
        ticker: The stock ticker symbol
        analyzer: Optional StockAnalyzer instance for getting similar companies
        
    Returns:
        JSON-serializable dictionary with financial data
    """
    try:
        financials = PolygonFinancials(ticker, analyzer=analyzer)
        data = financials.get_financial_data_for_ticker()
        return data
    except Exception as e:
        return {
            'error': str(e),
            'message': f"Error retrieving financial data for {ticker}"
        }

def main():
    # Get ticker from command line or prompt
    import sys
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = input("Enter ticker symbol (e.g., AAPL): ").upper()
    
    # Try to import the StockAnalyzer if available
    analyzer = None
    if ANTHROPIC_API_KEY:
        try:
            if importlib.util.find_spec("main") is not None:
                main_module = importlib.import_module("main")
                if hasattr(main_module, "StockAnalyzer") and hasattr(main_module, "anthropic_client"):
                    analyzer = main_module.StockAnalyzer(main_module.anthropic_client)
        except Exception as e:
            print(f"Error importing StockAnalyzer: {e}")
    
    # Create financial data instance and get summary
    financials = PolygonFinancials(ticker, analyzer=analyzer)
    financials.get_financial_summary()

if __name__ == "__main__":
    main() 