"use client";

import React from "react";

export interface CohortKpiData {
  totalEnrolled: number;
  activeStudents: number;
  completedStudents: number;
  averageProgressPercentage: string;
  averageAssessmentScore: string;
  completionRate: string;
  asOf: string;
}

interface CohortKpiCardsProps {
  data: CohortKpiData;
}

export const CohortKpiCards: React.FC<CohortKpiCardsProps> = ({ data }) => {
  const cards = [
    {
      id: "kpi-enrolled",
      title: "تعداد فراگیران ثبت‌نامی",
      value: data.totalEnrolled,
      suffix: "نفر",
      icon: "👥",
      badge: `${data.activeStudents} فعال`,
      badgeColor: "#059669",
      badgeBg: "#ecfdf5",
    },
    {
      id: "kpi-progress",
      title: "میانگین پیشرفت آموزشی",
      value: data.averageProgressPercentage,
      suffix: "٪",
      icon: "📈",
      badge: "تجمعی",
      badgeColor: "#2563eb",
      badgeBg: "#eff6ff",
    },
    {
      id: "kpi-score",
      title: "میانگین نمرات آزمون‌ها",
      value: data.averageAssessmentScore,
      suffix: "از ۱۰۰",
      icon: "🎯",
      badge: "ارزیابی نهایی",
      badgeColor: "#7c3aed",
      badgeBg: "#f5f3ff",
    },
    {
      id: "kpi-completion",
      title: "نرخ تکمیل دوره",
      value: data.completionRate,
      suffix: "٪",
      icon: "🎓",
      badge: `${data.completedStudents} فارغ‌التحصیل`,
      badgeColor: "#d97706",
      badgeBg: "#fffbeb",
    },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: "1.25rem",
        direction: "rtl",
        fontFamily: "var(--cs-font-family-base, inherit)",
      }}
      role="region"
      aria-label="شاخص‌های عملکرد کلیدی کوهورت"
    >
      {cards.map((card) => (
        <div
          key={card.id}
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "0.875rem",
            padding: "1.25rem",
            boxShadow: "0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03)",
            border: "1px solid #e2e8f0",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            minHeight: "130px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "0.875rem", color: "#64748b", fontWeight: 500 }}>
              {card.title}
            </span>
            <span style={{ fontSize: "1.25rem" }} aria-hidden="true">
              {card.icon}
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
            <span
              style={{
                fontSize: "1.875rem",
                fontWeight: 700,
                color: "#0f172a",
                fontVariantNumeric: "tabular-nums",
              }}
            >
              <bdi dir="ltr">{card.value}</bdi>
            </span>
            <span style={{ fontSize: "0.875rem", color: "#64748b" }}>
              {card.suffix}
            </span>
          </div>

          <div style={{ marginTop: "0.75rem" }}>
            <span
              style={{
                display: "inline-block",
                padding: "0.2rem 0.5rem",
                borderRadius: "9999px",
                fontSize: "0.75rem",
                fontWeight: 600,
                color: card.badgeColor,
                backgroundColor: card.badgeBg,
              }}
            >
              {card.badge}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
