import type { InputHTMLAttributes } from "react";

import styles from "./foundation.module.css";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  id: string;
  label: string;
  hint?: string;
  error?: string;
}

export function Input({ id, label, hint, error, className, ...props }: InputProps) {
  const descriptionId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [descriptionId, errorId].filter(Boolean).join(" ") || undefined;
  const inputClassName = [styles.input, className].filter(Boolean).join(" ");

  return (
    <label className={styles.field} htmlFor={id}>
      <span className={styles.label}>{label}</span>
      <input
        {...props}
        aria-describedby={describedBy}
        aria-errormessage={errorId}
        aria-invalid={Boolean(error)}
        className={inputClassName}
        id={id}
      />
      {hint && !error ? <span className={styles.hint} id={descriptionId}>{hint}</span> : null}
      {error ? <span className={styles.error} id={errorId} role="alert">{error}</span> : null}
    </label>
  );
}
