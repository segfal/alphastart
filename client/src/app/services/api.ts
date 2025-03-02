/**
 * API service for making requests to the backend
 */

// Base URL for API requests
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

// Cache for API responses
interface CacheItem<T> {
  timestamp: number;
  data: T;
}

// Cache object to store API responses
const apiCache: Record<string, CacheItem<any>> = {};

// Default cache TTL (24 hours in milliseconds)
const DEFAULT_CACHE_TTL = 24 * 60 * 60 * 1000;

// Maximum number of retries for failed requests
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1000; // 1 second

/**
 * Sleep for a specified duration
 * @param ms - Duration in milliseconds
 */
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Make a GET request to the API with caching and retry logic
 * @param endpoint - API endpoint
 * @param cacheTtl - Cache time-to-live in milliseconds
 * @returns Promise with the response data and cache status
 */
async function get<T>(
  endpoint: string, 
  cacheTtl: number = DEFAULT_CACHE_TTL
): Promise<{data: T, fromCache: boolean}> {
  const cacheKey = endpoint;
  const now = Date.now();
  
  // Check if we have a cached response that's still valid
  if (apiCache[cacheKey] && now - apiCache[cacheKey].timestamp < cacheTtl) {
    console.log(`Using client-side cached response for ${endpoint}`);
    return { data: apiCache[cacheKey].data, fromCache: true };
  }
  
  let lastError: Error | null = null;
  
  // Retry loop
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      // Add exponential backoff delay for retries
      if (attempt > 0) {
        const delay = INITIAL_RETRY_DELAY * Math.pow(2, attempt - 1);
        console.log(`Retry attempt ${attempt + 1}/${MAX_RETRIES}, waiting ${delay}ms...`);
        await sleep(delay);
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      
      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = parseInt(response.headers.get('Retry-After') || '5');
        console.log(`Rate limited, waiting ${retryAfter} seconds...`);
        await sleep(retryAfter * 1000);
        continue;
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.error || 
          `API error: ${response.status} ${response.statusText}`
        );
      }
      
      const data = await response.json();
      
      // Check if the response has a cache indicator from the server
      const fromServerCache = response.headers.get('X-From-Cache') === 'true';
      
      // Cache the successful response
      apiCache[cacheKey] = {
        timestamp: now,
        data
      };
      
      return { data, fromCache: fromServerCache };
      
    } catch (error) {
      console.error(
        `API request failed for ${endpoint} (attempt ${attempt + 1}/${MAX_RETRIES}):`,
        error
      );
      lastError = error as Error;
      
      // If this was the last attempt, throw the error
      if (attempt === MAX_RETRIES - 1) {
        throw new Error(
          `Failed after ${MAX_RETRIES} attempts: ${lastError.message}`
        );
      }
    }
  }
  
  // This should never be reached due to the throw in the loop
  throw lastError || new Error('Unknown error occurred');
}

/**
 * Search for stocks by ticker or company name
 * @param query - Search query
 * @returns Promise with search results
 */
export async function searchStocks(query: string): Promise<Array<{
  ticker: string;
  name: string;
  type: string;
  market: string;
  match_score: number;
}>> {
  if (!query || query.trim().length === 0) {
    return [];
  }
  
  try {
    const { data } = await get<any[]>(`/search/${encodeURIComponent(query.trim())}`);
    return data;
  } catch (error) {
    console.error('Stock search failed:', error);
    return [];  // Return empty array instead of throwing
  }
}

/**
 * Get basic information about a stock
 * @param ticker - Stock ticker symbol
 * @param riskLevel - User's risk tolerance level
 * @returns Promise with stock information
 */
export async function getStockInfo(ticker: string, riskLevel: string = 'moderate'): Promise<any> {
  const { data } = await get(
    `/ticker/${encodeURIComponent(ticker)}?risk_level=${encodeURIComponent(riskLevel)}`
  );
  return data;
}

/**
 * Get financial data for a stock
 * @param ticker - Stock ticker symbol
 * @returns Promise with financial data and cache status
 */
export async function getFinancialData(ticker: string): Promise<{
  pe_ratio: any;
  balance_sheet: any;
  fromCache: boolean;
}> {
  const [peRatioResult, balanceSheetResult] = await Promise.all([
    getPeRatio(ticker), 
    getBalanceSheet(ticker)
  ]);
  
  // Extract data and cache status
  const pe_ratio = peRatioResult;
  const balance_sheet = balanceSheetResult;
  
  // Consider it from cache if either result is from cache
  const fromCache = peRatioResult.fromCache || balanceSheetResult.fromCache;
  
  return {
    pe_ratio,
    balance_sheet,
    fromCache
  };
}

/**
 * Get P/E ratio for a stock
 * @param ticker - Stock ticker symbol
 * @returns Promise with P/E ratio data and cache status
 */
export async function getPeRatio(ticker: string): Promise<any> {
  return await get(`/pe_ratio/${encodeURIComponent(ticker)}`);
}

/**
 * Get balance sheet data for a stock
 * @param ticker - Stock ticker symbol
 * @returns Promise with balance sheet data and cache status
 */
export async function getBalanceSheet(ticker: string): Promise<any> {
  return await get(`/balance_sheet/${encodeURIComponent(ticker)}`);
}

/**
 * Get news articles for a stock
 * @param ticker - Stock ticker symbol
 * @returns Promise with news articles
 */
export async function getStockNews(ticker: string): Promise<any> {
  const { data } = await get(`/news/${encodeURIComponent(ticker)}`);
  return data;
}

export default {
  searchStocks,
  getStockInfo,
  getFinancialData,
  getPeRatio,
  getBalanceSheet,
  getStockNews
}; 