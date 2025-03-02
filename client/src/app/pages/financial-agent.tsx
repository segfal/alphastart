"use client";
import React, { useState, useRef, useEffect } from 'react';
import styles from './financial-agent.module.css';
import { searchStocks, getPeRatio, getBalanceSheet, getFinancialData } from '../services/api';
import { motion } from 'framer-motion';
import Header from '../components/Header';

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
  const [searchResults, setSearchResults] = useState<Array<{
    ticker: string;
    name: string;
    type: string;
    market?: string;
    match_score?: number;
  }>>([]);
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  const [userRiskTolerance, setUserRiskTolerance] = useState<string>('moderate');
  const [isFromCache, setIsFromCache] = useState<boolean>(false);

  // Retrieve user's risk tolerance from localStorage on component mount
  useEffect(() => {
    const storedRiskTolerance = typeof window !== 'undefined' 
      ? localStorage.getItem('userRiskTolerance') 
      : null;
    
    if (storedRiskTolerance) {
      setUserRiskTolerance(storedRiskTolerance);
      console.log('Retrieved risk tolerance:', storedRiskTolerance);
    }
  }, []);

  // Use the static STOCK_DATA for initial trending stocks
  const trendingStocks = STOCK_DATA.filter(stock => 
    ['NVDA', 'TSLA', 'AMD', 'PLTR'].includes(stock.ticker)
  );

  // Debounce search to avoid too many API calls
  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (searchTerm.trim().length > 0) {
        setIsSearchLoading(true);
        try {
          const results = await searchStocks(searchTerm);
          setSearchResults(results);
        } catch (error) {
          console.error('Error searching stocks:', error);
          // Fallback to static data if API fails
          const filteredStocks = STOCK_DATA.filter(
            stock =>
              stock.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
              stock.name.toLowerCase().includes(searchTerm.toLowerCase())
          );
          setSearchResults(filteredStocks);
        } finally {
          setIsSearchLoading(false);
        }
      } else {
        setSearchResults([]);
      }
    }, 300); // 300ms delay

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm]);

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
      setIsFromCache(false);
      
      try {
        let data;
        
        if (selectedAnalysis === 'financials') {
          // For financial analysis, use the getFinancialData function
          console.log('Fetching financial data for', selectedStock.ticker);
          
          try {
            const financialData = await getFinancialData(selectedStock.ticker);
            console.log('Financial data:', financialData);
            
            // Use the data returned from getFinancialData
            data = {
              ticker: selectedStock.ticker,
              pe_ratio: financialData.pe_ratio.data.pe_ratio,
              balance_sheet: financialData.balance_sheet.data.balance_sheet
            };
            
            // Set the fromCache status
            setIsFromCache(financialData.fromCache);
          } catch (error) {
            console.error('Error fetching financial data:', error);
            throw error;
          }
        } else {
          // For other analysis types, use the existing endpoints
          const endpoint = ANALYSIS_OPTIONS.find(opt => opt.value === selectedAnalysis)?.endpoint;
          // Add risk_level parameter to the URL
          const url = `http://localhost:5001${endpoint}/${selectedStock.ticker}?risk_level=${userRiskTolerance}`;
          console.log('Making request to:', url);
          console.log('Analysis type:', selectedAnalysis);
          console.log('Selected stock:', selectedStock);
          console.log('User risk tolerance:', userRiskTolerance);
          
          const response = await fetch(url);
          console.log('Response status:', response.status);
          
          if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.error || `Failed to fetch data: ${response.statusText}`);
          }
          
          // Check if the response is from cache
          const fromCache = response.headers.get('X-From-Cache') === 'true';
          setIsFromCache(fromCache);
          console.log('Response from cache:', fromCache);
          
          data = await response.json();
        }
        
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

  const formatRatio = (ratio: number | undefined | null): string => {
    if (ratio === undefined || ratio === null) return 'N/A';
    return ratio.toFixed(2);
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
        // Extract the risk analysis text
        const riskText = response.risk || '';
        
        // Process the risk analysis text to remove markdown formatting
        const processRiskText = (text: string) => {
          // Remove markdown heading (#)
          let processed = text.replace(/^#\s+(.+)$/m, '$1');
          
          // Replace bold markdown (**text**) with styled spans
          processed = processed.replace(/\*\*([^*]+)\*\*/g, '<span class="highlight">$1</span>');
          
          return processed;
        };

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
              <p dangerouslySetInnerHTML={{ __html: processRiskText(riskText) }}></p>
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
        
        const formatNumber = (num: number | null | undefined) => {
          if (num === null || num === undefined) return 'N/A';
          if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
          if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
          return `$${num.toFixed(2)}`;
        };

        console.log('Balance sheet data:', response.balance_sheet);
        console.log('PE ratio:', response.pe_ratio);
        
        return (
          <div className={styles.responseCard}>
            <h2 className={styles.responseTitle}>Financial Analysis - {response.ticker}</h2>
            
            <div className={styles.responseSection}>
              <h4>Balance Sheet Metrics</h4>
              {response.balance_sheet ? (
                <>
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
                    <span>Period: {response.balance_sheet.period || 'N/A'}</span>
                    <span>End Date: {response.balance_sheet.end_date || 'N/A'}</span>
                  </div>
                </>
              ) : (
                <p>No balance sheet data available</p>
              )}
            </div>

            <div className={styles.responseSection}>
              <h4>Valuation Metrics</h4>
              {response.pe_ratio ? (
                <div className={styles.metricsGrid}>
                  <div className={styles.metric}>
                    <span className={styles.metricLabel}>P/E Ratio</span>
                    <span className={styles.metricValue}>{formatRatio(response.pe_ratio)}</span>
                  </div>
                </div>
              ) : (
                <p>No valuation metrics available</p>
              )}
            </div>

            <div className={styles.responseSection}>
              <h4>Dividend Information</h4>
              <p>{response.dividend_data?.message || 'No dividend information available'}</p>
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

  // Loading animation variants
  const loadingContainerVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.5,
        when: "beforeChildren",
        staggerChildren: 0.2
      }
    },
    exit: { 
      opacity: 0, 
      y: -20,
      transition: { duration: 0.3 }
    }
  };

  const loadingTextVariants = {
    initial: { opacity: 0, y: 10 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5 }
    }
  };

  const loadingBarVariants = {
    initial: { width: "0%" },
    animate: { 
      width: "100%",
      transition: { 
        duration: 2.5, 
        ease: "easeInOut",
        repeat: Infinity
      }
    }
  };

  const loadingIconVariants = {
    initial: { scale: 0.8, opacity: 0 },
    animate: { 
      scale: 1, 
      opacity: 1,
      transition: {
        duration: 0.5
      }
    },
    pulse: {
      scale: [1, 1.1, 1],
      opacity: [1, 0.8, 1],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        repeatType: "reverse" as const
      }
    }
  };

  const loadingStepsVariants = {
    initial: { opacity: 0, x: -10 },
    animate: (custom: number) => ({
      opacity: 1,
      x: 0,
      transition: {
        delay: custom * 0.8,
        duration: 0.5
      }
    })
  };

  // Loading steps that will appear sequentially
  const loadingSteps = [
    "Crunching stock info...",
    "Analyzing market trends...",
    "Evaluating financial metrics...",
    "Comparing industry benchmarks...",
    "Generating insights..."
  ];

  return (
    <div className={styles.container}>
      <div className={styles.chatWrapper}>
        <Header 
          title="Search for a stock to start your analysis"
          subtitle="Accurate information on 100,000+ stocks and funds, including all the companies in the S&P500 index in real time. See stock prices, news, financials, forecasts, charts and more."
        />

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
                {isSearchLoading ? (
                  <div className={styles.searchLoading}>
                    <div className={styles.searchSpinner}></div>
                    <span>Searching...</span>
                  </div>
                ) : (
                  <>
                    {searchResults.length > 0 ? (
                      searchResults.map((stock) => (
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
                      ))
                    ) : searchTerm.trim().length > 0 ? (
                      <div className={styles.noResults}>
                        No stocks found matching "{searchTerm}"
                      </div>
                    ) : null}
                    
                    <div className={styles.trendingSection}>
                      <div className={styles.trendingHeader}>Trending</div>
                      <div className={styles.trendingStocks}>
                        {trendingStocks.map((stock) => (
                          <div
                            key={stock.ticker}
                            className={styles.trendingStock}
                            onClick={() => handleStockSelect(stock)}
                          >
                            {stock.ticker}
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
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
          <motion.div 
            className={styles.loadingContainer}
            variants={loadingContainerVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <motion.div 
              className={styles.loadingIcon}
              variants={loadingIconVariants}
              animate={["animate", "pulse"]}
            >
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <motion.path 
                  d="M12 5V3M12 21v-2M5 12H3m18 0h-2m-2.5-5.5L15 8M9 15l-1.5 1.5M18.5 18.5L17 17M7 17l-1.5 1.5M16.5 7.5L15 9" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ 
                    pathLength: 1, 
                    opacity: 1,
                    transition: { 
                      duration: 1.5,
                      repeat: Infinity,
                      repeatType: "loop",
                      ease: "easeInOut"
                    }
                  }}
                />
              </svg>
            </motion.div>
            
            <motion.h3 
              className={styles.loadingTitle}
              variants={loadingTextVariants}
            >
              Analyzing {selectedStock?.ticker}
            </motion.h3>
            
            <motion.div 
              className={styles.loadingBarContainer}
              variants={loadingTextVariants}
            >
              <motion.div 
                className={styles.loadingBar}
                variants={loadingBarVariants}
              />
            </motion.div>
            
            <div className={styles.loadingSteps}>
              {loadingSteps.map((step, index) => (
                <motion.div 
                  key={index}
                  className={styles.loadingStep}
                  custom={index}
                  variants={loadingStepsVariants}
                  initial="initial"
                  animate="animate"
                >
                  <motion.div 
                    className={styles.loadingStepDot}
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.7, 1, 0.7],
                      transition: {
                        duration: 1.5,
                        repeat: Infinity,
                        repeatType: "reverse" as const,
                        delay: index * 0.2
                      }
                    }}
                  />
                  <span>{step}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {apiError && (
          <div className={styles.errorMessage}>
            {apiError}
          </div>
        )}

        {response && !isLoading && (
          <div className={styles.responseContainer}>
            {isFromCache && (
              <div className={styles.cacheIndicator}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 8V12L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M3.05493 11.0549C2.67439 11.4354 2.67439 12.0686 3.05493 12.4491L11.0549 20.4491C11.4354 20.8296 12.0686 20.8296 12.4491 20.4491L20.4491 12.4491C20.8296 12.0686 20.8296 11.4354 20.4491 11.0549L12.4491 3.05493C12.0686 2.67439 11.4354 2.67439 11.0549 3.05493L3.05493 11.0549Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>Cached result</span>
              </div>
            )}
            {renderResponse()}
          </div>
        )}
      </div>
    </div>
  );
};

export default FinancialAgentPage; 