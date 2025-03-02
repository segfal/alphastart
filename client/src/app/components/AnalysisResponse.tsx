import React from 'react';
import styles from './AnalysisResponse.module.css';
import { motion } from 'framer-motion';

interface AnalysisResponseProps {
  response: any;
  analysisType: string;
  isFromCache: boolean;
}

const AnalysisResponse: React.FC<AnalysisResponseProps> = ({ response, analysisType, isFromCache }) => {
  if (!response) return null;

  const renderFinancialData = () => {
    if (analysisType === 'financials') {
      return (
        <div className={styles.financialData}>
          <h3>Financial Data for {response.ticker}</h3>
          
          <div className={styles.metricSection}>
            <h4>P/E Ratio</h4>
            {response.pe_ratio ? (
              <div className={styles.metric}>
                <span className={styles.metricLabel}>Current P/E Ratio:</span>
                <span className={styles.metricValue}>{response.pe_ratio.current_pe || 'N/A'}</span>
              </div>
            ) : (
              <p>P/E ratio data not available</p>
            )}
            
            {response.pe_ratio && response.pe_ratio.industry_average && (
              <div className={styles.metric}>
                <span className={styles.metricLabel}>Industry Average P/E:</span>
                <span className={styles.metricValue}>{response.pe_ratio.industry_average}</span>
              </div>
            )}
          </div>
          
          {response.balance_sheet && (
            <div className={styles.metricSection}>
              <h4>Balance Sheet</h4>
              <div className={styles.metric}>
                <span className={styles.metricLabel}>Total Assets:</span>
                <span className={styles.metricValue}>
                  {response.balance_sheet.total_assets ? 
                    `$${Number(response.balance_sheet.total_assets).toLocaleString()}` : 
                    'N/A'}
                </span>
              </div>
              <div className={styles.metric}>
                <span className={styles.metricLabel}>Total Liabilities:</span>
                <span className={styles.metricValue}>
                  {response.balance_sheet.total_liabilities ? 
                    `$${Number(response.balance_sheet.total_liabilities).toLocaleString()}` : 
                    'N/A'}
                </span>
              </div>
              <div className={styles.metric}>
                <span className={styles.metricLabel}>Debt-to-Equity Ratio:</span>
                <span className={styles.metricValue}>{response.balance_sheet.debt_to_equity || 'N/A'}</span>
              </div>
            </div>
          )}
          
          <div className={styles.analysisSection}>
            <h4>Analysis</h4>
            <p>
              {response.pe_ratio && response.pe_ratio.current_pe && response.pe_ratio.industry_average ? (
                Number(response.pe_ratio.current_pe) > Number(response.pe_ratio.industry_average) ?
                  `The P/E ratio (${response.pe_ratio.current_pe}) is higher than the industry average (${response.pe_ratio.industry_average}), which may indicate the stock is overvalued compared to its peers.` :
                  `The P/E ratio (${response.pe_ratio.current_pe}) is lower than the industry average (${response.pe_ratio.industry_average}), which may indicate the stock is undervalued compared to its peers.`
              ) : 'Unable to compare P/E ratio to industry average.'}
            </p>
            
            {response.balance_sheet && response.balance_sheet.debt_to_equity && (
              <p>
                {Number(response.balance_sheet.debt_to_equity) > 2 ?
                  `The debt-to-equity ratio of ${response.balance_sheet.debt_to_equity} is relatively high, which may indicate higher financial risk.` :
                  Number(response.balance_sheet.debt_to_equity) > 1 ?
                    `The debt-to-equity ratio of ${response.balance_sheet.debt_to_equity} is moderate, indicating a balanced financial structure.` :
                    `The debt-to-equity ratio of ${response.balance_sheet.debt_to_equity} is relatively low, which may indicate lower financial risk.`
                }
              </p>
            )}
          </div>
        </div>
      );
    }
    
    // For other analysis types, render the existing response format
    return (
      <div>
        {response.analysis && (
          <div className={styles.analysisSection}>
            <h3>Analysis</h3>
            <p>{response.analysis}</p>
          </div>
        )}
        
        {response.recommendation && (
          <div className={styles.recommendationSection}>
            <h3>Recommendation</h3>
            <p>{response.recommendation}</p>
          </div>
        )}
        
        {response.metrics && (
          <div className={styles.metricsSection}>
            <h3>Key Metrics</h3>
            <pre>{response.metrics}</pre>
          </div>
        )}
      </div>
    );
  };

  return (
    <motion.div 
      className={styles.container}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {isFromCache && (
        <div className={styles.cacheNotice}>
          <span>⚡ Loaded from cache</span>
        </div>
      )}
      
      {renderFinancialData()}
    </motion.div>
  );
};

export default AnalysisResponse; 