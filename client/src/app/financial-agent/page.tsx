"use client";
import React, { useState } from 'react';
import styles from '../pages/financial-agent.module.css';
import FinancialAgentPage from '../pages/financial-agent';

const FinancialAgentSite: React.FC = () => {
  const [query, setQuery] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Query submitted:', query);
  };

  return (
    <div className={styles.container}>
      <div className={styles.chatWrapper}>
        <div className={styles.logo}>AlphaStart</div>
        <FinancialAgentPage />
      </div>
    </div>
  );
};

export default FinancialAgentSite; 