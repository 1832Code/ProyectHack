"use client";

import React from "react";
import styles from "./animated-mascot.module.css";

/*
  Use the user's file from frontend/svs/pikachu.svg — we'll copy it to public
  and reference it as a normal image to keep things simple and avoid re-parsing
  the large inline SVG. The animation layers will be applied to the image container.
*/

export function AnimatedMascot({ size = 220 }: { size?: number }) {
  return (
    <div className={styles.mascotWrap} style={{ width: size, height: size }} aria-hidden title="Mascota animada">
      <div className={styles.svgContainer}>
        <img src="/pikachu.svg" alt="Mascota Pikachu" className={styles.mascotImage} />
      </div>

      {/* Decorative sparks (pure CSS animations layered on top) */}
      <div className={styles.spark} />
      <div className={styles.sparkTwo} />

      <div className={styles.shadow} />
    </div>
  );
}

export default AnimatedMascot;
