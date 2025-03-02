"use client";
import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import styles from './personal-info.module.css';
import { motion, AnimatePresence } from 'framer-motion';

const PersonalInfoPage: React.FC = () => {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    riskTolerance: ''
  });
  const [currentSection, setCurrentSection] = useState(0);
  const [errors, setErrors] = useState({
    name: false,
    age: false
  });

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
    
    // Store the user's risk tolerance in localStorage
    if (formData.riskTolerance) {
      localStorage.setItem('userRiskTolerance', formData.riskTolerance);
      console.log('Saved risk tolerance:', formData.riskTolerance);
    }
    
    router.push('/financial-agent');
  };

  const validateAndScrollToNext = (field: string, nextIndex: number) => {
    if (field === 'name' && !formData.name.trim()) {
      setErrors(prev => ({ ...prev, name: true }));
      return;
    }
    
    if (field === 'age' && (!formData.age || parseInt(formData.age) < 12)) {
      setErrors(prev => ({ ...prev, age: true }));
      return;
    }
    
    // Clear error if validation passes
    setErrors(prev => ({ ...prev, [field]: false }));
    
    // Proceed to next section
    if (nextIndex < sectionRefs.length) {
      sectionRefs[nextIndex]?.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollToNext = (index: number) => {
    if (index < sectionRefs.length) {
      sectionRefs[index]?.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent, field: string, nextIndex: number) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      validateAndScrollToNext(field, nextIndex);
    }
  };

  // Animation variants
  const progressVariants = {
    initial: { width: 0 },
    animate: (progress: number) => ({
      width: `${(progress / (sectionRefs.length - 1)) * 100}%`,
      transition: { duration: 0.5, ease: "easeInOut" }
    })
  };

  const sectionVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.6,
        when: "beforeChildren",
        staggerChildren: 0.2
      }
    },
    exit: { 
      opacity: 0,
      y: -50,
      transition: { duration: 0.3 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.4 }
    }
  };

  const buttonVariants = {
    rest: { scale: 1 },
    hover: { 
      scale: 1.05,
      transition: { duration: 0.2 }
    },
    tap: { scale: 0.95 }
  };

  const logoVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.5, 
        delay: 0.2,
        type: "spring",
        stiffness: 200,
        damping: 15
      }
    },
    pulse: {
      scale: [1, 1.05, 1],
      textShadow: [
        "0 0 0 rgba(0, 0, 0, 0)",
        "0 0 10px rgba(0, 0, 0, 0.2)",
        "0 0 0 rgba(0, 0, 0, 0)"
      ],
      transition: {
        duration: 2,
        repeat: Infinity,
        repeatType: "reverse" as const
      }
    }
  };

  const riskOptionVariants = {
    rest: { 
      scale: 1,
      boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)"
    },
    hover: { 
      scale: 1.03,
      boxShadow: "0px 8px 15px rgba(0, 0, 0, 0.15)",
      transition: { duration: 0.2 }
    },
    tap: { scale: 0.98 },
    selected: {
      scale: 1.05,
      boxShadow: "0px 10px 20px rgba(0, 0, 0, 0.2)",
      transition: { duration: 0.3 }
    }
  };

  return (
    <div className={styles.container}>
      <motion.div 
        className={styles.progress}
        initial="initial"
        animate="animate"
        custom={currentSection}
      >
        <motion.div 
          className={styles.progressBar} 
          variants={progressVariants}
          custom={currentSection}
        />
      </motion.div>
      
      <motion.div 
        className={styles.logoContainer}
        initial="hidden"
        animate="visible"
      >
        <motion.div 
          className={styles.logo}
          variants={logoVariants}
          animate={["visible", "pulse"]}
          whileHover={{ 
            scale: 1.1,
            transition: { duration: 0.2 }
          }}
        >
          AlphaStart
        </motion.div>
      </motion.div>
      
      <form onSubmit={handleSubmit} className={styles.form}>
        <motion.div 
          ref={sectionRefs[0]} 
          className={styles.questionSection}
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.7 }}
        >
          <motion.div className={styles.questionContent}>
            <motion.div className={styles.questionHeader} variants={itemVariants}>
              <span className={styles.questionNumber}>01</span>
              <label htmlFor="name">What's your name?</label>
            </motion.div>
            <motion.input
              variants={itemVariants}
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => {
                setFormData(prev => ({...prev, name: e.target.value}));
                if (e.target.value.trim()) {
                  setErrors(prev => ({ ...prev, name: false }));
                }
              }}
              onKeyPress={(e) => handleKeyPress(e, 'name', 1)}
              required
              placeholder="Type your name..."
              autoFocus
              className={`${styles.input} ${errors.name ? styles.inputError : ''}`}
            />
            {errors.name && (
              <motion.p 
                className={styles.errorMessage}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                Please enter your name to continue
              </motion.p>
            )}
          </motion.div>
          <motion.button 
            variants={buttonVariants}
            initial="rest"
            whileHover="hover"
            whileTap="tap"
            type="button" 
            className={styles.nextButton}
            onClick={() => validateAndScrollToNext('name', 1)}
          >
            Continue
          </motion.button>
        </motion.div>

        <motion.div 
          ref={sectionRefs[1]} 
          className={styles.questionSection}
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.7 }}
        >
          <motion.div className={styles.questionContent}>
            <motion.div className={styles.questionHeader} variants={itemVariants}>
              <span className={styles.questionNumber}>02</span>
              <label htmlFor="age">How old are you?</label>
            </motion.div>
            <motion.input
              variants={itemVariants}
              type="number"
              id="age"
              min="12"
              max="120"
              value={formData.age}
              onChange={(e) => {
                setFormData(prev => ({...prev, age: e.target.value}));
                if (e.target.value && parseInt(e.target.value) >= 12) {
                  setErrors(prev => ({ ...prev, age: false }));
                }
              }}
              onKeyPress={(e) => handleKeyPress(e, 'age', 2)}
              required
              placeholder="Enter your age..."
              className={`${styles.input} ${errors.age ? styles.inputError : ''}`}
            />
            {errors.age && (
              <motion.p 
                className={styles.errorMessage}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                Please enter a valid age (12 or above)
              </motion.p>
            )}
            <motion.p className={styles.hint} variants={itemVariants}>
              Must be at least 18 years old. If younger, you may continue with the help of a parent or guardian.
            </motion.p>
          </motion.div>
          <motion.button 
            variants={buttonVariants}
            initial="rest"
            whileHover="hover"
            whileTap="tap"
            type="button" 
            className={styles.nextButton}
            onClick={() => validateAndScrollToNext('age', 2)}
          >
            Continue
          </motion.button>
        </motion.div>

        <motion.div 
          ref={sectionRefs[2]} 
          className={styles.questionSection}
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.7 }}
        >
          <motion.div className={styles.questionContent}>
            <motion.div className={styles.questionHeader} variants={itemVariants}>
              <span className={styles.questionNumber}>03</span>
              <label htmlFor="riskTolerance">What's your risk tolerance?</label>
            </motion.div>
            <motion.div className={styles.riskOptions} variants={itemVariants}>
              <motion.div 
                className={`${styles.riskOption} ${formData.riskTolerance === 'conservative' ? styles.selected : ''}`}
                onClick={() => {
                  setFormData({...formData, riskTolerance: 'conservative'});
                  setTimeout(() => scrollToNext(3), 500);
                }}
                variants={riskOptionVariants}
                initial="rest"
                whileHover="hover"
                whileTap="tap"
                animate={formData.riskTolerance === 'conservative' ? "selected" : "rest"}
              >
                <h3>Conservative</h3>
                <p>I prefer stable, low-risk investments</p>
              </motion.div>
              <motion.div 
                className={`${styles.riskOption} ${formData.riskTolerance === 'moderate' ? styles.selected : ''}`}
                onClick={() => {
                  setFormData({...formData, riskTolerance: 'moderate'});
                  setTimeout(() => scrollToNext(3), 500);
                }}
                variants={riskOptionVariants}
                initial="rest"
                whileHover="hover"
                whileTap="tap"
                animate={formData.riskTolerance === 'moderate' ? "selected" : "rest"}
              >
                <h3>Moderate</h3>
                <p>I can handle some market fluctuations</p>
              </motion.div>
              <motion.div 
                className={`${styles.riskOption} ${formData.riskTolerance === 'aggressive' ? styles.selected : ''}`}
                onClick={() => {
                  setFormData({...formData, riskTolerance: 'aggressive'});
                  setTimeout(() => scrollToNext(3), 500);
                }}
                variants={riskOptionVariants}
                initial="rest"
                whileHover="hover"
                whileTap="tap"
                animate={formData.riskTolerance === 'aggressive' ? "selected" : "rest"}
              >
                <h3>Aggressive</h3>
                <p>I'm comfortable with high-risk, high-reward</p>
              </motion.div>
            </motion.div>
          </motion.div>
        </motion.div>

        <motion.div 
          ref={sectionRefs[3]} 
          className={styles.questionSection}
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.7 }}
        >
          <motion.div className={styles.questionContent}>
            <motion.div className={styles.summary} variants={itemVariants}>
              <motion.h2 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                Perfect! Here's what we know about you:
              </motion.h2>
              <AnimatePresence>
                {formData.name && (
                  <motion.div 
                    key="name-summary"
                    className={styles.summaryItem}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5, duration: 0.4 }}
                  >
                    <span>Name:</span> {formData.name}
                  </motion.div>
                )}
                {formData.age && (
                  <motion.div 
                    key="age-summary"
                    className={styles.summaryItem}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7, duration: 0.4 }}
                  >
                    <span>Age:</span> {formData.age}
                  </motion.div>
                )}
                {formData.riskTolerance && (
                  <motion.div 
                    key="risk-summary"
                    className={styles.summaryItem}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.9, duration: 0.4 }}
                  >
                    <span>Risk Profile:</span> {formData.riskTolerance.charAt(0).toUpperCase() + formData.riskTolerance.slice(1)}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
            <motion.button 
              type="submit" 
              className={styles.submitButton}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, duration: 0.5 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Continue to Financial Agent
            </motion.button>
          </motion.div>
        </motion.div>
      </form>
    </div>
  );
};

export default PersonalInfoPage; 