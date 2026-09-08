import React from "react";

interface StreakIndicatorProps {
  currentStreak: number;
  longestStreak: number;
  totalXp: number;
  level: number;
}

export const StreakIndicator: React.FC<StreakIndicatorProps> = ({
  currentStreak,
  longestStreak,
  totalXp,
  level,
}) => {
  return (
    <div
      style={{
        background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        color: "#ffffff",
        borderRadius: "1rem",
        padding: "1.5rem",
        marginBottom: "2rem",
        boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
      }}
      aria-labelledby="progression-banner-heading"
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1.5rem",
        }}
      >
        {/* Streak details */}
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div
            style={{
              fontSize: "3rem",
              background: "rgba(255, 255, 255, 0.1)",
              borderRadius: "50%",
              width: "4.5rem",
              height: "4.5rem",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            aria-hidden="true"
          >
            🔥
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
              <span style={{ fontSize: "2rem", fontWeight: 800, color: "#f97316" }}>
                {currentStreak}
              </span>
              <span style={{ fontSize: "1.1rem", fontWeight: 600 }}>روز پیاپی</span>
            </div>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#94a3b8" }}>
              رکورد بیشترین استمرار: <strong>{longestStreak} روز</strong> (مبنا: UTC Midnight)
            </p>
          </div>
        </div>

        {/* Level and XP progress */}
        <div style={{ minWidth: "240px", flex: 1, maxWidth: "340px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.9rem", fontWeight: 600 }}>سطح {level} دانش‌آموز</span>
            <span style={{ fontSize: "0.85rem", color: "#38bdf8", fontWeight: 700 }}>
              {totalXp} امتیاز XP
            </span>
          </div>
          {/* Progress bar */}
          <div
            style={{
              width: "100%",
              height: "0.65rem",
              background: "#334155",
              borderRadius: "9999px",
              overflow: "hidden",
            }}
            role="progressbar"
            aria-valuenow={totalXp % 100}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="پیشرفت سطح دانش‌آموز"
          >
            <div
              style={{
                width: `${Math.min(100, totalXp % 100)}%`,
                height: "100%",
                background: "linear-gradient(90deg, #38bdf8 0%, #818cf8 100%)",
                borderRadius: "9999px",
                transition: "width 0.3s ease",
              }}
            />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "0.25rem", fontSize: "0.75rem", color: "#64748b" }}>
            <span>{totalXp % 100} / 100 XP تا سطح بعدی</span>
            <span>سطح بعدی: {level + 1}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
