"use client";
import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import styles from './personal-info.module.css';

const PersonalInfoPage: React.FC = () => {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    riskTolerance: ''
  });
  const [currentSection, setCurrentSection] = useState(0);

  const sectionRefs = [
    useRef<HTMLDivElement>(null),
    useRef<HTMLDivElement>(null),
    useRef<HTMLDivElement>(null),
    useRef<HTMLDivElement>(null)
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add(styles.visible);
            // Update current section based on visibility
            const index = sectionRefs.findIndex(ref => ref.current === entry.target);
            if (index !== -1) {
              setCurrentSection(index);
            }
          }
        });
      },
      {
        threshold: 0.7,
      }
    );

    sectionRefs.forEach((ref) => {
      if (ref.current) {
        observer.observe(ref.current);
      }
    });

    return () => observer.disconnect();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    router.push('/financial-agent');
  };

  const scrollToNext = (index: number) => {
    if (index < sectionRefs.length) {
      sectionRefs[index]?.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent, nextIndex: number) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      scrollToNext(nextIndex);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.progress}>
        <div 
          className={styles.progressBar} 
          style={{ width: `${(currentSection / (sectionRefs.length - 1)) * 100}%` }}
        />
      </div>
      
      <div className={styles.logo}>AlphaStart</div>
      
      <form onSubmit={handleSubmit} className={styles.form}>
        <div ref={sectionRefs[0]} className={styles.questionSection}>
          <div className={styles.questionContent}>
            <div className={styles.questionHeader}>
              <span className={styles.questionNumber}>01</span>
              <label htmlFor="name">What's your name?</label>
            </div>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              onKeyPress={(e) => handleKeyPress(e, 1)}
              required
              placeholder="Type your name..."
              autoFocus
            />
          </div>
          <button 
            type="button" 
            className={styles.nextButton}
            onClick={() => scrollToNext(1)}
          >
            Continue
          </button>
        </div>

        <div ref={sectionRefs[1]} className={styles.questionSection}>
          <div className={styles.questionContent}>
            <div className={styles.questionHeader}>
              <span className={styles.questionNumber}>02</span>
              <label htmlFor="age">How old are you?</label>
            </div>
            <input
              type="number"
              id="age"
              min="12"
              max="120"
              value={formData.age}
              onChange={(e) => setFormData({...formData, age: e.target.value})}
              onKeyPress={(e) => handleKeyPress(e, 2)}
              required
              placeholder="Enter your age..."
            />
            <p className={styles.hint}>Must be at least 12 years old</p>
          </div>
          <button 
            type="button" 
            className={styles.nextButton}
            onClick={() => scrollToNext(2)}
          >
            Continue
          </button>
        </div>

        <div ref={sectionRefs[2]} className={styles.questionSection}>
          <div className={styles.questionContent}>
            <div className={styles.questionHeader}>
              <span className={styles.questionNumber}>03</span>
              <label htmlFor="riskTolerance">What's your risk tolerance?</label>
            </div>
            <div className={styles.riskOptions}>
              <div 
                className={`${styles.riskOption} ${formData.riskTolerance === 'conservative' ? styles.selected : ''}`}
                onClick={() => {
                  setFormData({...formData, riskTolerance: 'conservative'});
                  setTimeout(() => scrollToNext(3), 500);
                }}
              >
                <h3>Conservative</h3>
                <p>I prefer stable, low-risk investments</p>
              </div>
              <div 
                className={`${styles.riskOption} ${formData.riskTolerance === 'moderate' ? styles.selected : ''}`}
                onClick={() => {
                  setFormData({...formData, riskTolerance: 'moderate'});
                  setTimeout(() => scrollToNext(3), 500);
                }}
              >
                <h3>Moderate</h3>
                <p>I can handle some market fluctuations</p>
              </div>
              <div 
                className={`${styles.riskOption} ${formData.riskTolerance === 'aggressive' ? styles.selected : ''}`}
                onClick={() => {
                  setFormData({...formData, riskTolerance: 'aggressive'});
                  setTimeout(() => scrollToNext(3), 500);
                }}
              >
                <h3>Aggressive</h3>
                <p>I'm comfortable with high-risk, high-reward</p>
              </div>
            </div>
          </div>
        </div>

        <div ref={sectionRefs[3]} className={styles.questionSection}>
          <div className={styles.questionContent}>
            <div className={styles.summary}>
              <h2>Perfect! Here's what we know about you:</h2>
              <div className={styles.summaryItem}>
                <span>Name:</span> {formData.name}
              </div>
              <div className={styles.summaryItem}>
                <span>Age:</span> {formData.age}
              </div>
              <div className={styles.summaryItem}>
                <span>Risk Profile:</span> {formData.riskTolerance.charAt(0).toUpperCase() + formData.riskTolerance.slice(1)}
              </div>
            </div>
            <button type="submit" className={styles.submitButton}>
              Continue to Financial Agent
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default PersonalInfoPage; 