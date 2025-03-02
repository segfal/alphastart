"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './login.module.css';
import { motion } from 'framer-motion';

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

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        duration: 0.8,
        when: "beforeChildren",
        staggerChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { y: 40, opacity: 0 },
    visible: { 
      y: 0, 
      opacity: 1,
      transition: { 
        type: "spring", 
        stiffness: 100, 
        damping: 10,
        duration: 0.7 
      }
    }
  };

  const logoVariants = {
    hidden: { scale: 0.8, opacity: 0, rotateZ: -10 },
    visible: { 
      scale: 1, 
      opacity: 1, 
      rotateZ: 0,
      transition: { 
        type: "spring", 
        stiffness: 200, 
        damping: 15,
        duration: 1 
      }
    },
    float: {
      y: [0, -15, 0],
      rotateZ: [0, 5, 0],
      transition: {
        y: {
          repeat: Infinity,
          duration: 3,
          ease: "easeInOut"
        },
        rotateZ: {
          repeat: Infinity,
          duration: 4,
          ease: "easeInOut"
        }
      }
    }
  };

  const buttonVariants = {
    rest: { scale: 1, backgroundColor: "#4361ee" },
    hover: { 
      scale: 1.05,
      backgroundColor: "#3a56d4",
      boxShadow: "0px 8px 15px rgba(67, 97, 238, 0.4)",
      transition: { 
        duration: 0.3,
        type: "spring",
        stiffness: 400
      }
    },
    tap: { 
      scale: 0.95,
      backgroundColor: "#2b44b8"
    }
  };

  const buttonAnimation = {
    pulse: {
      scale: [1, 1.05, 1],
      transition: {
        delay: 1.5,
        duration: 1,
        repeat: 3,
        repeatType: "reverse" as const
      }
    }
  };

  const inputWrapperVariants = {
    rest: { 
      borderColor: "rgba(255, 255, 255, 0.1)",
      boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.1)"
    },
    focus: { 
      borderColor: "#4361ee",
      boxShadow: "0px 5px 15px rgba(67, 97, 238, 0.3)",
      transition: { duration: 0.3 }
    }
  };

  const inputLineVariants = {
    rest: { scaleX: 0 },
    focus: { 
      scaleX: 1,
      transition: { duration: 0.5 }
    }
  };

  const backgroundAnimation = {
    animate: {
      background: [
        "radial-gradient(circle at 20% 20%, rgba(67, 97, 238, 0.4) 0%, rgba(0, 0, 0, 0) 50%)",
        "radial-gradient(circle at 80% 30%, rgba(67, 97, 238, 0.4) 0%, rgba(0, 0, 0, 0) 50%)",
        "radial-gradient(circle at 40% 70%, rgba(67, 97, 238, 0.4) 0%, rgba(0, 0, 0, 0) 50%)",
        "radial-gradient(circle at 60% 20%, rgba(67, 97, 238, 0.4) 0%, rgba(0, 0, 0, 0) 50%)"
      ],
      opacity: [0.7, 0.9, 0.7],
      scale: [1, 1.1, 1],
      transition: { 
        duration: 15, 
        repeat: Infinity,
        repeatType: "reverse" as const
      }
    }
  };

  const [emailFocus, setEmailFocus] = useState(false);
  const [passwordFocus, setPasswordFocus] = useState(false);

  if (!mounted) {
    return null; // Prevent flash of content during hydration
  }

  return (
    <div className={styles.container}>
      <motion.div 
        className={styles.formWrapper}
        initial="hidden"
        animate="visible"
        variants={containerVariants}
      >
        <div className={styles.formContent}>
          <motion.div 
            className={styles.logoWrapper}
            variants={logoVariants}
            initial="hidden"
            animate={["visible", "float"]}
          >
            <motion.div 
              className={styles.logo}
              whileHover={{ 
                scale: 1.1, 
                rotateZ: 5,
                transition: { duration: 0.3 } 
              }}
            >
              FF
            </motion.div>
            <motion.div 
              className={styles.logoGlow}
              animate={{
                opacity: [0.5, 0.8, 0.5],
                scale: [1, 1.2, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: "reverse" as const
              }}
            />
          </motion.div>
          
          <motion.h1 
            className={styles.title} 
            variants={itemVariants}
            animate="visible"
          >
            Welcome to Fin
          </motion.h1>
          
          <motion.p 
            className={styles.subtitle} 
            variants={itemVariants}
            animate="visible"
          >
            Your personal financial companion
          </motion.p>
          
          <form onSubmit={handleSubmit} className={styles.form}>
            <motion.div 
              className={styles.inputGroup} 
              variants={itemVariants}
              animate="visible"
            >
              <motion.div 
                className={styles.inputWrapper}
                variants={inputWrapperVariants}
                initial="rest"
                animate={emailFocus ? "focus" : "rest"}
              >
                <motion.input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({...prev, email: e.target.value}))}
                  onFocus={() => setEmailFocus(true)}
                  onBlur={() => setEmailFocus(false)}
                  required
                  placeholder=" "
                  className={styles.input}
                  whileFocus={{ scale: 1.02 }}
                />
                <label htmlFor="email" className={styles.inputLabel}>Email address</label>
                <motion.div 
                  className={styles.inputLine}
                  variants={inputLineVariants}
                  initial="rest"
                  animate={emailFocus ? "focus" : "rest"}
                />
              </motion.div>
            </motion.div>

            <motion.div 
              className={styles.inputGroup} 
              variants={itemVariants}
              animate="visible"
            >
              <motion.div 
                className={styles.inputWrapper}
                variants={inputWrapperVariants}
                initial="rest"
                animate={passwordFocus ? "focus" : "rest"}
              >
                <motion.input
                  type="password"
                  id="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  onFocus={() => setPasswordFocus(true)}
                  onBlur={() => setPasswordFocus(false)}
                  required
                  placeholder=" "
                  className={styles.input}
                  whileFocus={{ scale: 1.02 }}
                />
                <label htmlFor="password" className={styles.inputLabel}>Password</label>
                <motion.div 
                  className={styles.inputLine}
                  variants={inputLineVariants}
                  initial="rest"
                  animate={passwordFocus ? "focus" : "rest"}
                />
              </motion.div>
            </motion.div>

            <motion.button 
              type="submit" 
              className={styles.submitButton}
              variants={buttonVariants}
              initial="rest"
              whileHover="hover"
              whileTap="tap"
              animate={buttonAnimation.pulse}
            >
              <motion.span 
                className={styles.buttonText}
                animate={{ 
                  x: [0, 5, 0],
                }}
                transition={{ 
                  delay: 2.5,
                  duration: 0.8, 
                  repeat: 3,
                  repeatType: "reverse" as const
                }}
              >
                Get Started
              </motion.span>
              <motion.span 
                className={styles.buttonIcon}
                animate={{ 
                  x: [0, 10, 0],
                }}
                transition={{ 
                  delay: 2.5,
                  duration: 0.8, 
                  repeat: 3,
                  repeatType: "reverse" as const
                }}
              >
                →
              </motion.span>
            </motion.button>
          </form>

          <motion.div 
            className={styles.footer} 
            variants={itemVariants}
            animate="visible"
          >
            Don't have an account? <motion.button 
              onClick={() => router.push('/signup')} 
              className={styles.link}
              whileHover={{ 
                scale: 1.05, 
                color: "#4361ee",
                transition: { duration: 0.2 } 
              }}
            >
              Sign up
            </motion.button>
          </motion.div>
        </div>
        
        <motion.div 
          className={styles.backgroundEffect}
          animate={backgroundAnimation.animate}
        />
      </motion.div>
    </div>
  );
};

export default LoginPage; 