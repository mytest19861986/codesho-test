import type { HTMLAttributes } from "react";

import styles from "./foundation.module.css";

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  label?: string;
}

export function Progress({ value, max = 100, label, className, ...props }: ProgressProps) {
  const safeMax = max > 0 ? max : 100;
  const safeValue = Math.min(Math.max(value, 0), safeMax);
  const percentage = (safeValue / safeMax) * 100;
  const classes = [styles.progress, className].filter(Boolean).join(" ");

  return (
    <div className={classes} {...props}>
      {label ? <span>{label}</span> : null}
      <div
        aria-label={label}
        aria-valuemax={safeMax}
        aria-valuemin={0}
        aria-valuenow={safeValue}
        className={styles.progressTrack}
        role="progressbar"
      >
        <div className={styles.progressValue} style={{ inlineSize: `${percentage}%` }} />
      </div>
    </div>
  );
}
