"use client";
import React from 'react';
import styles from '../pages/financial-agent.module.css';
import { motion } from 'framer-motion';

interface TrendingStocksProps {
  stocks: Array<{ ticker: string; name: string; type: string }>;
  onSelectStock: (stock: { ticker: string; name: string; type: string }) => void;
}

const TrendingStocks: React.FC<TrendingStocksProps> = ({ stocks, onSelectStock }) => {
  return (
    <div className={styles.trendingSection}>
      <h3 className={styles.trendingTitle}>Trending Stocks</h3>
      <div className={styles.trendingTags}>
        {stocks.map((stock, index) => (
          <motion.div
            key={stock.ticker}
            className={styles.trendingTag}
            onClick={() => onSelectStock(stock)}
            whileHover={{ y: -2, boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)' }}
            whileTap={{ y: 0 }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: index * 0.05 }}
          >
            {stock.ticker}
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default TrendingStocks; 