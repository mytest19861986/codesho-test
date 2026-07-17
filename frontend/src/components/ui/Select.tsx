import type { SelectHTMLAttributes } from "react";

import styles from "./foundation.module.css";

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  id: string;
  label: string;
  hint?: string;
  error?: string;
}

export function Select({ id, label, hint, error, className, children, ...props }: SelectProps) {
  const descriptionId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [descriptionId, errorId].filter(Boolean).join(" ") || undefined;
  const selectClassName = [styles.select, className].filter(Boolean).join(" ");

  return (
    <label className={styles.field} htmlFor={id}>
      <span className={styles.label}>{label}</span>
      <select
        {...props}
        aria-describedby={describedBy}
        aria-errormessage={errorId}
        aria-invalid={Boolean(error)}
        className={selectClassName}
        id={id}
      >
        {children}
      </select>
      {hint && !error ? <span className={styles.hint} id={descriptionId}>{hint}</span> : null}
      {error ? <span className={styles.error} id={errorId} role="alert">{error}</span> : null}
    </label>
  );
}
