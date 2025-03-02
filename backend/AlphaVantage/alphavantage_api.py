
import os
# get balance sheet, income statement, and cash flow statement
from alpha_vantage.fundamentaldata import FundamentalData
from dotenv import load_dotenv
import json
import pandas as pd
load_dotenv()

class AlphaVantage:
    def __init__(self):
        self.fd = FundamentalData(key=os.getenv("ALPHA_VANTAGE_API_KEY"))

    def get_balance_sheet(self, symbol: str):
        data, meta_data = self.fd.get_balance_sheet_annual(symbol=symbol)
 
        count = 0
        for year in data:
            print(data[year][0])
            count += 1
            if count == 5:
                break
    
    

AlphaVantage = AlphaVantage()
print(AlphaVantage.get_balance_sheet("AAPL"))


#save the data to a csv file
df = pd.DataFrame(AlphaVantage.get_balance_sheet("AAPL"))
df.to_csv("balance_sheet.csv", index=False)

df.to_excel("balance_sheet.xlsx", index=False)
