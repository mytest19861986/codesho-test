import type { ButtonHTMLAttributes, ReactNode } from "react";

import styles from "./foundation.module.css";
import type { ButtonVariant } from "./Button";

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  "aria-label": string;
  children: ReactNode;
  variant?: ButtonVariant;
}

export function IconButton({
  "aria-label": ariaLabel,
  children,
  className,
  type = "button",
  variant = "ghost",
  ...props
}: IconButtonProps) {
  const classes = [styles.iconButton, styles[variant], className].filter(Boolean).join(" ");

  return (
    <button aria-label={ariaLabel} className={classes} type={type} {...props}>
      {children}
    </button>
  );
}
