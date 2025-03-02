"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './personal-info.module.css';

const PersonalInfo: React.FC = () => {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    riskTolerance: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, you'd save this information
    router.push('/financial-agent');
  };

  return (
    <div className={styles.container}>
      <div className={styles.formWrapper}>
        <div className={styles.logo}>FF</div>
        <form onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="age">Age</label>
            <input
              type="number"
              id="age"
              min="5"
              max="120"
              value={formData.age}
              onChange={(e) => setFormData({...formData, age: e.target.value})}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="riskTolerance">Risk Tolerance</label>
            <select
              id="riskTolerance"
              value={formData.riskTolerance}
              onChange={(e) => setFormData({...formData, riskTolerance: e.target.value})}
              required
            >
              <option value="">Select your risk tolerance</option>
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>

          <button type="submit" className={styles.submitButton}>
            Continue
          </button>
        </form>
      </div>
    </div>
  );
};

export default PersonalInfo; 