import os
import sys
import time
import random
import requests
import json
import anthropic as claude
import alpha_vantage as av
from polygon import RESTClient
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from stock_news import get_news_from_motley_fool
load_dotenv()


polygon_key = os.getenv("POLYGON_API_KEY")
client = RESTClient(api_key=polygon_key)

anthropic_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = claude.Anthropic(api_key=anthropic_key)


class Prompts:
    def __init__(self):
        self.anthropic_client = anthropic_client
        print(self.anthropic_client)
        pass

    def get_ticker_symbol(self, ticker: str):
        prompt = f"What is the ticker symbol of {ticker} and only return the ticker symbol"
        response = self.anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,  # Limits response length
            messages=[{"role": "user", "content": prompt}],  # Sends your input message to the AI
        )   
        return response.content[0].text

    def get_company_name(self, ticker: str):
        prompt = f"What is the name of {ticker} and only return the company name"
        response = self.anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,  # Limits response length
            messages=[{"role": "user", "content": prompt}],  # Sends your input message to the AI
        )   
        return response.content[0].text
    
    def get_company_description(self, ticker: str):
        prompt = f"What is the description of {ticker} and only return the company description"
        response = self.anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,  # Limits response length
            messages=[{"role": "user", "content": prompt}],  # Sends your input message to the AI
        )   
        return response.content[0].text
    
    def get_company_industry(self, ticker: str):
        prompt = f"What is the industry of {ticker} and only return the company industry"
        response = self.anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,  # Limits response length
            messages=[{"role": "user", "content": prompt}],  # Sends your input message to the AI
        )   
        return response.content[0].text
    
    def get_morning_star_rating(self, ticker: str):
        prompt = f"What is the Morningstar rating for {ticker}? Please only return the numerical rating (1-5) with no additional text or explanation."
        response = self.anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,  # Limits response length
            messages=[{"role": "user", "content": prompt}],  # Sends your input message to the AI
        )   
        return response.content[0].text

    def get_moody_rating(self, ticker: str):
        prompt = f"What is the Moody's credit rating for {ticker}? Please only return the numerical value or letter grade (e.g. Aaa, Aa1, A2, etc) with no additional text or explanation."
        response = self.anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,  # Limits response length
            messages=[{"role": "user", "content": prompt}],  # Sends your input message to the AI
        )   
        return response.content[0].text

    def risk_agent(self, ticker: str):
        prompt = f'''What is the risk of {ticker} and only return the risk, based on the moody rating and the morning star rating\n
        Moody Rating: {self.get_moody_rating(ticker)}
        Morning Star Rating: {self.get_morning_star_rating(ticker)}
        '''
        print(prompt)
        response = self.anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,  # Limits response length
            messages=[{"role": "user", "content": prompt}],  # Sends your input message to the AI
        )   
        if response.content[0].text == "high":
            return "high"
        elif response.content[0].text == "medium":
            return "medium"
        else:
            prompt = f"Since the risk is not high or medium, should we invest in {ticker}? and only return yes or no and explain why you think so"   
            response = self.anthropic_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1024,  # Limits response length
                messages=[{"role": "user", "content": prompt}],  # Sends your input message to the AI
            )   
            return response.content[0].text

def get_ticker_news(ticker: str):
    news = get_news_from_motley_fool(ticker)
    return news

ticker = "AAPL"
prompt = Prompts()
print(prompt.risk_agent(ticker))