# Backend

## Overview

This is the backend service for the stock analysis application. It provides AI-powered financial analysis, stock data retrieval, and news aggregation through a RESTful API.

## Setup

```bash
# Create and activate virtual environment
virtualenv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Make sure you have a .env file with the following:
# POLYGON_API_KEY=your_polygon_api_key
# ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Run

```bash
# Start the Flask server
python main.py

# The server will run on http://localhost:5001 by default
```

## API Endpoints

### Get Stock Information

```
GET /api/ticker/<ticker>
```

Returns basic information about a stock, including:
- Company name
- Description
- Industry
- Risk analysis

Example: `GET /api/ticker/AAPL`

### Get Financial Data

```
GET /api/financials/<ticker>
```

Returns comprehensive financial data for a stock, including:
- Price-to-earnings ratio
- Revenue growth
- Profit margins
- Balance sheet information
- Cash flow metrics

Example: `GET /api/financials/MSFT`

### Get News Articles

```
GET /api/news/<ticker>
```

Returns recent news articles about a stock from trusted financial sources.

Example: `GET /api/news/TSLA`

### Get AI-Powered Financial Analysis

```
GET /api/financial-analysis/<ticker>
```

Returns an in-depth AI-generated analysis of the stock's financial health and prospects.

Example: `GET /api/financial-analysis/AMZN`

## Development

The application uses:
- Flask for the web server
- Anthropic's Claude AI for financial analysis
- Polygon.io for financial data
- Web scraping for news aggregation

For more details on the Claude AI integration, see `README_CLAUDE_INTEGRATION.md`.

