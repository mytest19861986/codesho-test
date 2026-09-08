import React from "react";

export interface CohortBadgeProps {
  code: string;
  title: string;
  currentCount: number;
  maxCapacity: number;
  isActive?: boolean;
}

export const CohortBadge: React.FC<CohortBadgeProps> = ({
  code,
  title,
  currentCount,
  maxCapacity,
  isActive = true,
}) => {
  const isFull = currentCount >= maxCapacity;
  const remainingSeats = Math.max(0, maxCapacity - currentCount);

  let bg = "#f0fdf4";
  let border = "#bbf7d0";
  let text = "#15803d";
  let statusLabel = `ظرفیت باقی‌مانده: ${remainingSeats} از ${maxCapacity}`;

  if (!isActive) {
    bg = "#f1f5f9";
    border = "#cbd5e1";
    text = "#64748b";
    statusLabel = "غیرفعال";
  } else if (isFull) {
    bg = "#fef2f2";
    border = "#fecaca";
    text = "#b91c1c";
    statusLabel = "ظرفیت تکمیل";
  }

  return (
    <div
      role="group"
      aria-label={`اطلاعات گروه کلاسی ${title}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.5rem",
        padding: "0.35rem 0.75rem",
        borderRadius: "9999px",
        background: bg,
        border: `1px solid ${border}`,
        color: text,
        fontSize: "0.8rem",
        fontWeight: 500,
        direction: "rtl",
      }}
    >
      <span aria-hidden="true">👥</span>
      <span>
        {title} ({code})
      </span>
      <span
        style={{
          fontSize: "0.75rem",
          padding: "0.1rem 0.4rem",
          borderRadius: "0.25rem",
          background: "rgba(255, 255, 255, 0.7)",
          fontWeight: 600,
        }}
      >
        {statusLabel}
      </span>
    </div>
  );
};
