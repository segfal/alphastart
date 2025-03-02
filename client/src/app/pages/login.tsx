"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './login.module.css';

const Login: React.FC = () => {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isOver18, setIsOver18] = useState<'yes' | 'no' | ''>('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, you'd handle authentication here
    router.push('/personal-info');
  };

  return (
    <div className={styles.container}>
      <div className={styles.formWrapper}>
        <div className={styles.logo}>FF</div>
        
        <form onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label>Are you 18 or over?</label>
            <div 
              className={styles.dropdown}
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              <div className={styles.selected}>
                {isOver18 || 'Select'}
                <span className={styles.arrow}>▼</span>
              </div>
              {isDropdownOpen && (
                <div className={styles.options}>
                  <div 
                    onClick={() => setIsOver18('yes')}
                    className={styles.option}
                  >
                    Yes
                  </div>
                  <div 
                    onClick={() => setIsOver18('no')}
                    className={styles.option}
                  >
                    No
                  </div>
                </div>
              )}
            </div>
          </div>

          <button type="submit" className={styles.submitButton}>
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
