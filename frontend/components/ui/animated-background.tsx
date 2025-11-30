"use client";

import React from "react";
import styles from "./animated-background.module.css";

/**
 * AnimatedBackground
 * Lightweight, accessible animated background using SVG blobs and CSS keyframes.
 * Respects prefers-reduced-motion.
 */
export function AnimatedBackground({ className = "" }: { className?: string }) {
  return (
    <div className={`${styles.bgWrap} ${className}`} aria-hidden>
      <div className={styles.gradient} />

      <svg
        className={styles.blobs}
        viewBox="0 0 800 600"
        preserveAspectRatio="xMidYMid meet"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="g1" x1="0" x2="1">
            <stop offset="0%" stopColor="#7C3AED" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#06B6D4" stopOpacity="0.85" />
          </linearGradient>
        </defs>

        <g transform="translate(0,-30)">
          <path className={`${styles.blob} ${styles.b1}`} fill="url(#g1)" d="M150 50C200 0 320 0 380 40C480 100 540 180 520 260C500 340 420 380 320 400C220 420 120 380 80 300C30 200 100 100 150 50Z" />
          <path className={`${styles.blob} ${styles.b2}`} fill="#ff7ab6" d="M700 180C720 90 640 20 560 30C480 40 440 130 420 190C400 250 430 320 500 340C570 360 660 330 700 260C740 190 705 270 700 180Z" />
          <path className={`${styles.blob} ${styles.b3}`} fill="#FFB86B" d="M380 320C420 290 520 280 580 320C650 370 700 430 670 490C630 560 540 560 460 520C380 480 320 420 300 360C280 300 340 350 380 320Z" />
        </g>
      </svg>

      <div className={styles.particles} />
    </div>
  );
}

export default AnimatedBackground;
