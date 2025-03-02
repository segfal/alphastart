"use client";
import React from 'react';
import styles from '../pages/financial-agent.module.css';
import { motion } from 'framer-motion';

interface AnalysisOption {
  value: string;
  label: string;
  endpoint: string;
  description: string;
}

interface AnalysisOptionsProps {
  options: AnalysisOption[];
  selectedAnalysis: string;
  setSelectedAnalysis: (analysis: string) => void;
  hoverOption: string;
  setHoverOption: (option: string) => void;
}

const AnalysisOptions: React.FC<AnalysisOptionsProps> = ({
  options,
  selectedAnalysis,
  setSelectedAnalysis,
  hoverOption,
  setHoverOption
}) => {
  return (
    <div className={styles.formGroup}>
      <label htmlFor="analysis-type">Analysis Type</label>
      <div className={styles.selectWrapper}>
        <select
          id="analysis-type"
          className={styles.select}
          value={selectedAnalysis}
          onChange={(e) => setSelectedAnalysis(e.target.value)}
          onMouseEnter={() => setHoverOption(selectedAnalysis)}
          onMouseLeave={() => setHoverOption('')}
        >
          <option value="">Select analysis type</option>
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              onMouseEnter={() => setHoverOption(option.value)}
            >
              {option.label}
            </option>
          ))}
        </select>
        
        {hoverOption && (
          <motion.div
            className={styles.optionDescription}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.2 }}
          >
            {options.find(opt => opt.value === hoverOption)?.description}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default AnalysisOptions; 