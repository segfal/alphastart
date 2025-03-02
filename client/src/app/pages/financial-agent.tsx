"use client";
import React, { useState, useRef, useEffect } from 'react';
import styles from './financial-agent.module.css';

// Expanded stock data with more details
const STOCK_DATA = [
  { ticker: 'NVDA', name: 'NVIDIA Corporation', type: 'Stock' },
  { ticker: 'TSLA', name: 'Tesla, Inc.', type: 'Stock' },
  { ticker: 'AMD', name: 'Advanced Micro Devices, Inc.', type: 'Stock' },
  { ticker: 'PLTR', name: 'Palantir Technologies Inc.', type: 'Stock' },
  { ticker: 'MSFT', name: 'Microsoft Corporation', type: 'Stock' },
  { ticker: 'SMCI', name: 'Super Micro Computer, Inc.', type: 'Stock' },
  { ticker: 'AAPL', name: 'Apple Inc.', type: 'Stock' },
  { ticker: 'GOOGL', name: 'Alphabet Inc.', type: 'Stock' },
  { ticker: 'AMZN', name: 'Amazon.com Inc.', type: 'Stock' },
  { ticker: 'META', name: 'Meta Platforms Inc.', type: 'Stock' },
];

const ANALYSIS_OPTIONS = [
  { 
    value: 'basic', 
    label: 'Basic Stock Information',
    endpoint: '/api/ticker',
    description: 'Company overview, description, industry, and risk analysis'
  },
  { 
    value: 'financials', 
    label: 'Financial Data & Metrics',
    endpoint: '/api/financials',
    description: 'P/E ratio, revenue growth, margins, balance sheet, and cash flow metrics'
  },
  { 
    value: 'news', 
    label: 'Latest News & Updates',
    endpoint: '/api/news',
    description: 'Recent news articles from trusted financial sources'
  },
  { 
    value: 'ai-analysis', 
    label: 'AI-Powered Financial Analysis',
    endpoint: '/api/financial-analysis',
    description: 'In-depth AI analysis of financial health and prospects'
  }
];

interface ApiResponse {
  company_name?: string;
  description?: string;
  industry?: string;
  risk?: string;
  balance_sheet?: {
    debt_ratio: number;
    debt_to_equity: number;
    end_date: string;
    period: string;
    ticker: string;
    total_assets: number;
    total_equity: number;
    total_liabilities: number;
    year: string;
  };
  cash_flow?: any;
  dividend_data?: {
    has_dividends: boolean;
    message: string;
  };
  industry_pe_ratio?: number;
  pe_ratio?: number;
  pe_relative_to_industry?: number;
  ticker?: string;
  news?: Array<{
    link: string;
    source: string;
    title: string;
  }>;
}

const FinancialAgentPage: React.FC = () => {
  const [selectedAnalysis, setSelectedAnalysis] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [selectedStock, setSelectedStock] = useState<{ ticker: string; name: string; type: string } | null>(null);
  const [hoverOption, setHoverOption] = useState('');
  const searchRef = useRef<HTMLDivElement>(null);
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [streamingResponse, setStreamingResponse] = useState<string[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const filteredStocks = searchTerm
    ? STOCK_DATA.filter(
        stock =>
          stock.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
          stock.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : STOCK_DATA;

  const handleStockSelect = (stock: { ticker: string; name: string; type: string }) => {
      setSelectedStock(stock);
      setSearchTerm(stock.ticker);
      setIsSearchOpen(false);
  };
  
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsSearchOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const simulateStreaming = (text: string) => {
    setIsStreaming(true);
    const words = text.split(' ');
    let currentIndex = 0;

    const streamInterval = setInterval(() => {
      if (currentIndex < words.length) {
        setStreamingResponse(prev => [...prev, words[currentIndex]]);
        currentIndex++;
      } else {
        clearInterval(streamInterval);
        setIsStreaming(false);
      }
    }, 50);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedStock && selectedAnalysis) {
      setIsLoading(true);
      setApiError(null);
      
      try {
        const endpoint = ANALYSIS_OPTIONS.find(opt => opt.value === selectedAnalysis)?.endpoint;
        const url = `http://localhost:5001${endpoint}/${selectedStock.ticker}`;
        console.log('Making request to:', url);
        console.log('Analysis type:', selectedAnalysis);
        console.log('Selected stock:', selectedStock);
        
        const response = await fetch(url);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          throw new Error(errorData?.error || `Failed to fetch data: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Raw API Response:', data);
        setResponse(data);
      } catch (error: any) {
        console.error('Detailed error:', error);
        setApiError(error.message || 'Failed to fetch data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const renderResponse = () => {
    if (!response) {
      console.log('No response data available');
      return null;
    }

    console.log('Rendering response for analysis type:', selectedAnalysis);
    console.log('Full response object:', response);

    switch (selectedAnalysis) {
      case 'basic':
        return (
          <div className={styles.responseCard}>
            <h2 className={styles.responseTitle}>{response.company_name}</h2>
            
            <div className={styles.responseSection}>
              <h4>Description</h4>
              <p>{response.description}</p>
            </div>

            <div className={styles.responseSection}>
              <h4>Industry</h4>
              <p>{response.industry}</p>
            </div>

            <div className={styles.responseSection}>
              <h4>Risk Analysis</h4>
              <p>{response.risk}</p>
            </div>
          </div>
        );
      
      case 'financials':
        console.log('Financial data:', response);
        
        if (!response.balance_sheet) {
          console.log('No financial data in response');
          return (
            <div className={styles.responseCard}>
              <div className={styles.responseSection}>
                <p>No financial data available</p>
              </div>
            </div>
          );
        }
        
        const formatNumber = (num: number) => {
          if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
          if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
          return `$${num.toFixed(2)}`;
        };

        const formatRatio = (ratio: number) => ratio.toFixed(2);
        
        console.log('Balance sheet data:', response.balance_sheet);
        console.log('PE ratio:', response.pe_ratio);
        
        return (
          <div className={styles.responseCard}>
            <h2 className={styles.responseTitle}>Financial Analysis - {response.ticker}</h2>
            
            <div className={styles.responseSection}>
              <h4>Balance Sheet Metrics</h4>
              <div className={styles.metricsGrid}>
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Total Assets</span>
                  <span className={styles.metricValue}>{formatNumber(response.balance_sheet.total_assets)}</span>
                </div>
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Total Equity</span>
                  <span className={styles.metricValue}>{formatNumber(response.balance_sheet.total_equity)}</span>
                </div>
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Total Liabilities</span>
                  <span className={styles.metricValue}>{formatNumber(response.balance_sheet.total_liabilities)}</span>
                </div>
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Debt Ratio</span>
                  <span className={styles.metricValue}>{formatRatio(response.balance_sheet.debt_ratio)}</span>
                </div>
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Debt to Equity</span>
                  <span className={styles.metricValue}>{formatRatio(response.balance_sheet.debt_to_equity)}</span>
                </div>
              </div>
              <div className={styles.periodInfo}>
                <span>Period: {response.balance_sheet.period}</span>
                <span>End Date: {response.balance_sheet.end_date}</span>
              </div>
            </div>

            <div className={styles.responseSection}>
              <h4>Valuation Metrics</h4>
              <div className={styles.metricsGrid}>
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>P/E Ratio</span>
                  <span className={styles.metricValue}>{formatRatio(response.pe_ratio)}</span>
                </div>
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Industry P/E</span>
                  <span className={styles.metricValue}>{formatRatio(response.industry_pe_ratio)}</span>
                </div>
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>P/E vs Industry</span>
                  <span className={styles.metricValue}>{formatRatio(response.pe_relative_to_industry)}</span>
                </div>
              </div>
            </div>

            <div className={styles.responseSection}>
              <h4>Dividend Information</h4>
              <p>{response.dividend_data.message}</p>
            </div>
          </div>
        );
      
      case 'news':
        console.log('Rendering news section');
        // Check if response is an array
        const newsArticles = Array.isArray(response) ? response : response.news;
        console.log('News articles:', newsArticles);
        
        if (!newsArticles || newsArticles.length === 0) {
          console.log('No news articles found in response');
          return (
            <div className={styles.responseCard}>
              <div className={styles.responseSection}>
                <p>No news articles available</p>
              </div>
            </div>
          );
        }

        console.log('Number of news articles:', newsArticles.length);
        return (
          <div className={styles.responseCard}>
            <h2 className={styles.responseTitle}>Latest News Articles</h2>
            <div className={styles.newsGrid}>
              {newsArticles.map((article, index) => {
                console.log('Rendering article:', article);
                return (
                  <a 
                    key={index}
                    href={article.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.newsArticle}
                  >
                    <div className={styles.articleContent}>
                      <h3 className={styles.articleTitle}>{article.title}</h3>
                      <span className={styles.articleSource}>{article.source}</span>
                    </div>
                  </a>
                );
              })}
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.chatWrapper}>
        <h1 className={styles.searchTitle}>Search for a stock to start your analysis</h1>
        
        <p className={styles.searchDescription}>
          Accurate information on 100,000+ stocks and funds, including all the companies in the
          S&P500 index in real time. See stock prices, news, financials, forecasts, charts and more.
        </p>

        <div className={styles.searchSection} ref={searchRef}>
          <div className={styles.searchContainer}>
            <div className={styles.searchInputWrapper}>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setIsSearchOpen(true);
                }}
                onFocus={() => setIsSearchOpen(true)}
                placeholder="Search stocks..."
                className={styles.searchInput}
              />
              {searchTerm && (
                <button 
                  className={styles.clearButton}
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedStock(null);
                  }}
                >
                  ×
                </button>
              )}
            </div>
            
            {isSearchOpen && (
              <div className={styles.searchResults}>
                {filteredStocks.map((stock) => (
                  <div
                    key={stock.ticker}
                    className={styles.searchResult}
                    onClick={() => handleStockSelect(stock)}
                  >
                    <div className={styles.stockInfo}>
                      <span className={styles.ticker}>{stock.ticker}</span>
                      <span className={styles.companyName}>{stock.name}</span>
                    </div>
                    <span className={styles.stockType}>{stock.type}</span>
                  </div>
                ))}
                <div className={styles.trendingSection}>
                  <div className={styles.trendingHeader}>Trending</div>
                  <div className={styles.trendingStocks}>
                    {['NVDA', 'TSLA', 'AMD', 'PLTR'].map((ticker) => {
                      const stock = STOCK_DATA.find(s => s.ticker === ticker);
                      if (!stock) return null;
                      return (
                        <div
                          key={stock.ticker}
                          className={styles.trendingStock}
                          onClick={() => handleStockSelect(stock)}
                        >
                          {stock.ticker}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>

          {selectedStock && (
            <form onSubmit={handleSubmit} className={styles.inputForm}>
              <div className={styles.questionSelect}>
                <select
                  value={selectedAnalysis}
                  onChange={(e) => setSelectedAnalysis(e.target.value)}
                  className={styles.selectInput}
                  onMouseOver={(e) => {
                    const option = e.target as HTMLSelectElement;
                    setHoverOption(option.value);
                  }}
                  onMouseLeave={() => setHoverOption('')}
                  required
                >
                  <option value="">Select the type of analysis you need</option>
                  {ANALYSIS_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {selectedAnalysis && (
                  <div className={styles.endpointInfo}>
                    {ANALYSIS_OPTIONS.find(opt => opt.value === selectedAnalysis)?.description}
                  </div>
                )}
              </div>
              <button 
                type="submit" 
                className={styles.submitButton}
                disabled={!selectedAnalysis}
              >
                Get Analysis
              </button>
            </form>
          )}
        </div>

        {isLoading && (
          <div className={styles.loadingContainer}>
            <div className={styles.loadingSpinner}></div>
            <p>Analyzing {selectedStock?.ticker}...</p>
          </div>
        )}

        {apiError && (
          <div className={styles.errorMessage}>
            {apiError}
          </div>
        )}

        {response && !isLoading && (
          <div className={styles.responseContainer}>
            {renderResponse()}
          </div>
        )}
      </div>
    </div>
  );
};

export default FinancialAgentPage; 