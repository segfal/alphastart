import os
from polygon import RESTClient

polygon_key = os.getenv("POLYGON_API_KEY")
client = RESTClient(api_key=polygon_key)



class FinancialData:
    def __init__(self, ticker: str):
        self.ticker = ticker

    def get_financial_data(self):
        return client.get_aggs(ticker=self.ticker, multiplier=1, timespan="minute", from_="2024-01-01", to="2024-01-02", limit=10)
    
    def get_financial_data_for_date(self, date: str):
        return client.get_aggs(ticker=self.ticker, multiplier=1, timespan="minute", from_=date, to=date, limit=10)
    
    def get_financial_data_for_date_range(self, start_date: str, end_date: str):
        return client.get_aggs(ticker=self.ticker, multiplier=1, timespan="minute", from_=start_date, to=end_date, limit=10)
    
