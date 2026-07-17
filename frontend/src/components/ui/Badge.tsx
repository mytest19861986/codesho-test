import type { HTMLAttributes, ReactNode } from "react";

import styles from "./foundation.module.css";

export type BadgeVariant = "primary" | "success" | "warning" | "danger" | "info";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  variant?: BadgeVariant;
}

export function Badge({ children, className, variant = "primary", ...props }: BadgeProps) {
  const classes = [styles.badge, styles[`badge${variant[0].toUpperCase()}${variant.slice(1)}`], className]
    .filter(Boolean)
    .join(" ");

  return <span className={classes} {...props}>{children}</span>;
}
