"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './login.module.css';
import { motion, AnimatePresence } from 'framer-motion';

const Login: React.FC = () => {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailFocus, setEmailFocus] = useState(false);
  const [passwordFocus, setPasswordFocus] = useState(false);
  const [showHint, setShowHint] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // For demo purposes, allow any login or use the hint credentials
    if ((email === 'john' && password === 'john') || !email) {
      router.push('/personal-info');
    } else {
      // Show hint after first attempt
      setShowHint(true);
    }
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.6,
        when: "beforeChildren",
        staggerChildren: 0.2
      }
    }
  };

  const formVariants = {
    hidden: { 
      opacity: 0,
      y: 50,
      scale: 0.95
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 12,
        when: "beforeChildren",
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 10
      }
    }
  };

  const logoVariants = {
    hidden: { scale: 0.8, opacity: 0 },
    visible: {
      scale: 1,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 200,
        damping: 15
      }
    },
    pulse: {
      scale: [1, 1.05, 1],
      textShadow: [
        "0 0 0 rgba(0, 0, 0, 0)",
        "0 0 10px rgba(0, 122, 255, 0.5)",
        "0 0 0 rgba(0, 0, 0, 0)"
      ],
      transition: {
        duration: 2,
        repeat: Infinity,
        repeatType: "reverse" as const
      }
    }
  };

  const inputGroupVariants = {
    focus: (isFocused: boolean) => ({
      scale: isFocused ? 1.02 : 1,
      y: isFocused ? -5 : 0,
      transition: {
        type: "spring",
        stiffness: 500,
        damping: 25
      }
    })
  };

  const buttonVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 10,
        delay: 0.4
      }
    },
    hover: {
      scale: 1.05,
      backgroundColor: "#333",
      boxShadow: "0 10px 20px rgba(0, 0, 0, 0.2)",
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 10
      }
    },
    tap: {
      scale: 0.95
    },
    pulse: {
      scale: [1, 1.05, 1],
      boxShadow: [
        "0 5px 15px rgba(0, 0, 0, 0.1)",
        "0 8px 25px rgba(0, 0, 0, 0.2)",
        "0 5px 15px rgba(0, 0, 0, 0.1)"
      ],
      transition: {
        duration: 1.5,
        repeat: 3,
        repeatType: "reverse" as const,
        delay: 1
      }
    }
  };

  const hintVariants = {
    hidden: { opacity: 0, y: -10 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 10
      }
    }
  };

  return (
    <motion.div 
      className={styles.container}
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <motion.div 
        className={styles.formWrapper}
        variants={formVariants}
        initial="hidden"
        animate="visible"
        whileHover={{ boxShadow: "0 15px 30px rgba(0, 0, 0, 0.15)" }}
        transition={{ duration: 0.3 }}
      >
        <motion.div 
          className={styles.logo}
          variants={logoVariants}
          animate={["visible", "pulse"]}
          whileHover={{ 
            scale: 1.1,
            color: "#007AFF",
            transition: { duration: 0.2 }
          }}
        >
          AlphaStart
        </motion.div>
        
        <form onSubmit={handleSubmit}>
          <motion.div 
            className={styles.inputGroup}
            custom={emailFocus}
            animate="focus"
            variants={inputGroupVariants}
          >
            <motion.label 
              htmlFor="email"
              animate={{ 
                color: emailFocus ? "#007AFF" : "#666",
                x: emailFocus ? 5 : 0
              }}
              transition={{ duration: 0.2 }}
            >
              Email
            </motion.label>
            <motion.input
              type="text"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setEmailFocus(true)}
              onBlur={() => setEmailFocus(false)}
              whileFocus={{ 
                borderColor: "#007AFF",
                boxShadow: "0 0 0 3px rgba(0, 122, 255, 0.3)"
              }}
              initial={{ borderColor: "#eee" }}
              placeholder="Try 'john'"
            />
          </motion.div>

          <motion.div 
            className={styles.inputGroup}
            custom={passwordFocus}
            animate="focus"
            variants={inputGroupVariants}
          >
            <motion.label 
              htmlFor="password"
              animate={{ 
                color: passwordFocus ? "#007AFF" : "#666",
                x: passwordFocus ? 5 : 0
              }}
              transition={{ duration: 0.2 }}
            >
              Password
            </motion.label>
            <motion.input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => setPasswordFocus(true)}
              onBlur={() => setPasswordFocus(false)}
              required
              whileFocus={{ 
                borderColor: "#007AFF",
                boxShadow: "0 0 0 3px rgba(0, 122, 255, 0.3)"
              }}
              initial={{ borderColor: "#eee" }}
              placeholder="Try 'john'"
            />
          </motion.div>

          <AnimatePresence>
            {showHint && (
              <motion.div 
                key="login-hint"
                className={styles.loginHint}
                variants={hintVariants}
                initial="hidden"
                animate="visible"
                exit="hidden"
              >
                <motion.p>
                  Hint: Try using "john" for both email and password
                </motion.p>
              </motion.div>
            )}
          </AnimatePresence>

          <motion.button 
            type="submit" 
            className={styles.submitButton}
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
            animate={["visible", "pulse"]}
          >
            <motion.span
              initial={{ opacity: 1 }}
              animate={{ 
                opacity: [1, 0.8, 1],
              }}
              transition={{ 
                duration: 1.5, 
                repeat: Infinity,
                repeatType: "reverse" as const
              }}
            >
              Sign In
            </motion.span>
          </motion.button>
        </form>

        <motion.p 
          className={styles.demoNote}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
        >
          This is a demo. You can use "john/john" or leave email blank to continue.
        </motion.p>
      </motion.div>
    </motion.div>
  );
};

export default Login;
