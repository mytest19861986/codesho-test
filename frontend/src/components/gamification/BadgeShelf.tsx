import React from "react";

export interface BadgeItem {
  id: string;
  badge_code: string;
  badge_level: number;
  title: string;
  description: string;
  is_earned: boolean;
  awarded_at?: string;
}

interface BadgeShelfProps {
  badges: BadgeItem[];
}

export const BadgeShelf: React.FC<BadgeShelfProps> = ({ badges }) => {
  const getBadgeIcon = (code: string) => {
    switch (code) {
      case "FIRST_LESSON":
        return "🌱";
      case "STREAK_3_DAYS":
        return "⚡";
      case "STREAK_7_DAYS":
        return "🔥";
      case "SUBMISSION_STAR":
        return "⭐";
      default:
        return "🏆";
    }
  };

  return (
    <div
      style={{
        background: "var(--cs-color-bg-surface, #ffffff)",
        border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
        borderRadius: "1rem",
        padding: "1.5rem",
        marginBottom: "2rem",
      }}
      aria-labelledby="badge-shelf-heading"
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <h2 id="badge-shelf-heading" style={{ margin: 0, fontSize: "1.25rem", color: "#0f172a" }}>
          🏅 قفسه نشان‌ها و افتخارات
        </h2>
        <span
          style={{
            fontSize: "0.85rem",
            padding: "0.25rem 0.75rem",
            borderRadius: "9999px",
            background: "#eff6ff",
            color: "#1d4ed8",
            fontWeight: 700,
            border: "1px solid #bfdbfe",
          }}
        >
          {badges.filter((b) => b.is_earned).length} از {badges.length} نشان کسب شده
        </span>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: "1rem",
        }}
      >
        {badges.map((b) => (
          <div
            key={b.id}
            style={{
              padding: "1.25rem",
              borderRadius: "0.75rem",
              border: b.is_earned ? "1px solid #bbf7d0" : "1px dashed #cbd5e1",
              background: b.is_earned ? "#f0fdf4" : "#f8fafc",
              opacity: b.is_earned ? 1 : 0.65,
              transition: "transform 0.15s ease",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
            }}
          >
            <div
              style={{
                fontSize: "2.5rem",
                marginBottom: "0.5rem",
                filter: b.is_earned ? "none" : "grayscale(100%)",
              }}
              aria-hidden="true"
            >
              {getBadgeIcon(b.badge_code)}
            </div>
            <strong style={{ fontSize: "1rem", color: b.is_earned ? "#166534" : "#475569", marginBottom: "0.25rem" }}>
              {b.title}
            </strong>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#64748b", lineHeight: "1.4" }}>
              {b.description}
            </p>
            {b.is_earned ? (
              <span
                style={{
                  marginTop: "0.75rem",
                  fontSize: "0.75rem",
                  padding: "0.15rem 0.5rem",
                  borderRadius: "0.25rem",
                  background: "#dcfce7",
                  color: "#15803d",
                  fontWeight: 600,
                }}
              >
                ✓ کسب شده
              </span>
            ) : (
              <span
                style={{
                  marginTop: "0.75rem",
                  fontSize: "0.75rem",
                  padding: "0.15rem 0.5rem",
                  borderRadius: "0.25rem",
                  background: "#e2e8f0",
                  color: "#475569",
                  fontWeight: 500,
                }}
              >
                قفل شده
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
