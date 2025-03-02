"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './login.module.css';

const LoginPage: React.FC = () => {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  // Ensure hydration completes before rendering
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    router.push('/personal-info');
  };

  if (!mounted) {
    return null; // Prevent flash of content during hydration
  }

  return (
    <div className={styles.container}>
      <div className={styles.formWrapper}>
        <div className={styles.formContent}>
          <div className={styles.logoWrapper}>
            <div className={styles.logo}>FF</div>
            <div className={styles.logoGlow} />
          </div>
          
          <h1 className={styles.title}>Welcome to Fin</h1>
          <p className={styles.subtitle}>Your personal financial companion</p>
          
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.inputGroup}>
              <div className={styles.inputWrapper}>
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({...prev, email: e.target.value}))}
                  required
                  placeholder=" "
                  className={styles.input}
                />
                <label htmlFor="email" className={styles.inputLabel}>Email address</label>
                <div className={styles.inputLine} />
              </div>
            </div>

            <div className={styles.inputGroup}>
              <div className={styles.inputWrapper}>
                <input
                  type="password"
                  id="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                  placeholder=" "
                  className={styles.input}
                />
                <label htmlFor="password" className={styles.inputLabel}>Password</label>
                <div className={styles.inputLine} />
              </div>
            </div>

            <button type="submit" className={styles.submitButton}>
              <span className={styles.buttonText}>Get Started</span>
              <span className={styles.buttonIcon}>→</span>
            </button>
          </form>

          <div className={styles.footer}>
            Don't have an account? <button onClick={() => router.push('/signup')} className={styles.link}>Sign up</button>
          </div>
        </div>
        
        <div className={styles.backgroundEffect} />
      </div>
    </div>
  );
};

export default LoginPage; 