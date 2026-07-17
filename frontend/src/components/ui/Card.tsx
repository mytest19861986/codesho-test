import type { HTMLAttributes, ReactNode } from "react";

import styles from "./foundation.module.css";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  interactive?: boolean;
}

export function Card({ children, className, interactive = false, ...props }: CardProps) {
  const classes = [styles.card, interactive && styles.cardInteractive, className]
    .filter(Boolean)
    .join(" ");

  return <div className={classes} {...props}>{children}</div>;
}
