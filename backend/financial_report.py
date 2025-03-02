#!/usr/bin/env python3
import sys
from Polygon.polygon_api import FinancialData
import pandas as pd

def main():
    # Check if ticker symbol was provided
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = input("Enter a ticker symbol (e.g., AAPL): ").upper()
    
    # Create a FinancialData instance for the ticker
    company = FinancialData(ticker)
    
    # Print the options menu
    print(f"\n--- Financial Data Options for {ticker} ---")
    print("1. Get Balance Sheet")
    print("2. Get P/E Ratio")
    print("3. Get Full Financial Summary")
    print("4. Export Balance Sheet to CSV")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == '1':
        # Display formatted balance sheet
        company.format_balance_sheet(output_format='print')
    
    elif choice == '2':
        # Get and display P/E ratio
        pe_ratio = company.get_pe_ratio()
        if pe_ratio:
            print(f"\nP/E Ratio for {ticker}: {pe_ratio:.2f}")
        else:
            print(f"\nCould not calculate P/E Ratio for {ticker}")
    
    elif choice == '3':
        # Get and display comprehensive financial summary
        company.get_financial_summary()
    
    elif choice == '4':
        # Export balance sheet to CSV
        try:
            df = company.format_balance_sheet(output_format='df')
            if df is not None:
                filename = f"{ticker}_balance_sheet.csv"
                df.to_csv(filename, index=False)
                print(f"\nBalance sheet exported to {filename}")
            else:
                print("\nNo balance sheet data available to export")
        except Exception as e:
            print(f"\nError exporting to CSV: {e}")
    
    elif choice == '5':
        print("\nExiting program.")
        sys.exit(0)
    
    else:
        print("\nInvalid choice. Please select a number between 1 and 5.")

if __name__ == "__main__":
    main() 