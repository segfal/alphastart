"use client";
import React, { useState } from 'react';
import styles from '../pages/financial-agent.module.css';
import FinancialAgentPage from '../pages/financial-agent';
import Header from '../components/Header';

const FinancialAgentSite: React.FC = () => {
  const [query, setQuery] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Query submitted:', query);
  };

  return (
    <div className={styles.container}>
      <nav className={styles.navbar}>
        <div className={styles.navContent}>
          <div className={styles.logo}>
            <span>Alpha</span>Start
          </div>
        </div>
      </nav>
      
      <div className={styles.chatWrapper}>
        <FinancialAgentPage />
      </div>
    </div>
  );
};

export default FinancialAgentSite; 