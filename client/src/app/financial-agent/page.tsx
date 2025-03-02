"use client";
import React, { useState } from 'react';
import styles from '../pages/financial-agent.module.css';

const FinancialAgentPage: React.FC = () => {
  const [query, setQuery] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Query submitted:', query);
  };

  return (
    <div className={styles.container}>
      <div className={styles.chatWrapper}>
        <div className={styles.logo}>FF</div>
        
        <div className={styles.welcomeMessage}>
          Welcome to the Fin financial agent. Let us know what kind of public equities you're looking for
        </div>

        <form onSubmit={handleSubmit} className={styles.inputForm}>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className={styles.queryInput}
            placeholder="Type your investment preferences..."
            rows={8}
          />
        </form>
      </div>
    </div>
  );
};

export default FinancialAgentPage; 