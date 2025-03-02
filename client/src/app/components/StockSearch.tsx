"use client";
import React, { useState, useRef, useEffect } from 'react';
import styles from '../pages/financial-agent.module.css';
import { motion, AnimatePresence } from 'framer-motion';

interface StockSearchProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  searchResults: Array<{
    ticker: string;
    name: string;
    type: string;
    market?: string;
    match_score?: number;
  }>;
  isSearchLoading: boolean;
  selectedStock: { ticker: string; name: string; type: string } | null;
  setSelectedStock: (stock: { ticker: string; name: string; type: string } | null) => void;
  isSearchOpen: boolean;
  setIsSearchOpen: (isOpen: boolean) => void;
}

const StockSearch: React.FC<StockSearchProps> = ({
  searchTerm,
  setSearchTerm,
  searchResults,
  isSearchLoading,
  selectedStock,
  setSelectedStock,
  isSearchOpen,
  setIsSearchOpen
}) => {
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsSearchOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [setIsSearchOpen]);

  const handleStockSelect = (stock: { ticker: string; name: string; type: string }) => {
    setSelectedStock(stock);
    setSearchTerm(stock.ticker);
    setIsSearchOpen(false);
  };

  return (
    <div className={styles.formGroup}>
      <label htmlFor="stock-search">Search for a stock</label>
      <div className={styles.searchContainer} ref={searchRef}>
        <input
          id="stock-search"
          type="text"
          className={styles.searchInput}
          placeholder="Enter ticker symbol or company name..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setIsSearchOpen(true);
          }}
          onFocus={() => setIsSearchOpen(true)}
        />
        
        <AnimatePresence>
          {isSearchOpen && (searchResults.length > 0 || isSearchLoading) && (
            <motion.div
              className={styles.searchResults}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {isSearchLoading ? (
                <div className={styles.searchLoading}>
                  <div className={styles.searchSpinner}></div>
                </div>
              ) : searchResults.length > 0 ? (
                searchResults.map((result) => (
                  <motion.div
                    key={result.ticker}
                    className={styles.searchResultItem}
                    onClick={() => handleStockSelect(result)}
                    whileHover={{ backgroundColor: 'rgba(37, 99, 235, 0.1)' }}
                  >
                    <div>
                      <span className={styles.ticker}>{result.ticker}</span>
                      <span className={styles.name}> - {result.name}</span>
                    </div>
                    {result.match_score && (
                      <span className={styles.matchScore}>
                        {Math.round(result.match_score)}%
                      </span>
                    )}
                  </motion.div>
                ))
              ) : (
                <div className={styles.noResults}>No results found</div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
        
        {selectedStock && (
          <motion.div
            className={styles.selectedStock}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <span>
              {selectedStock.ticker} - {selectedStock.name}
            </span>
            <button onClick={() => setSelectedStock(null)}>×</button>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default StockSearch; 