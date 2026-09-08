import React from "react";
import { CohortBadge } from "./CohortBadge";

export interface EnrollmentItem {
  id: string;
  courseTitle: string;
  courseCode: string;
  cohortTitle?: string;
  cohortCode?: string;
  currentCount?: number;
  maxCapacity?: number;
  status: "enrolled" | "active" | "suspended" | "completed";
  enrolledAt: string;
  prerequisites?: string[];
}

export interface EnrollmentCardProps {
  enrollments: EnrollmentItem[];
  availableCourses?: Array<{
    id: string;
    title: string;
    code: string;
    cohorts: Array<{
      code: string;
      title: string;
      currentCount: number;
      maxCapacity: number;
    }>;
  }>;
}

const statusMap: Record<string, { label: string; bg: string; color: string }> = {
  enrolled: { label: "ثبت‌نام شده", bg: "#eff6ff", color: "#1d4ed8" },
  active: { label: "در حال یادگیری (فعال)", bg: "#f0fdf4", color: "#15803d" },
  suspended: { label: "معلق (ظرفیت آزاد)", bg: "#fffbeb", color: "#b45309" },
  completed: { label: "تکمیل شده (نهایی)", bg: "#faf5ff", color: "#7e22ce" },
};

export const EnrollmentCard: React.FC<EnrollmentCardProps> = ({
  enrollments,
}) => {
  return (
    <div
      style={{
        background: "var(--cs-color-bg-surface, #ffffff)",
        border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
        borderRadius: "1rem",
        padding: "1.5rem",
        direction: "rtl",
      }}
      role="region"
      aria-labelledby="student-enrollments-heading"
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.25rem",
        }}
      >
        <h2
          id="student-enrollments-heading"
          style={{ margin: 0, fontSize: "1.25rem", fontWeight: 700 }}
        >
          🎓 دوره‌های ثبت‌نامی و وضعیت کوهورت‌ها
        </h2>
        <span
          style={{
            fontSize: "0.8rem",
            color: "#64748b",
            background: "#f1f5f9",
            padding: "0.25rem 0.6rem",
            borderRadius: "0.5rem",
          }}
        >
          P3-VS5 Authoritative State
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {enrollments.map((item) => {
          const st = statusMap[item.status] || statusMap.enrolled;
          return (
            <div
              key={item.id}
              style={{
                display: "flex",
                flexWrap: "wrap",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "1rem 1.25rem",
                borderRadius: "0.75rem",
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                gap: "1rem",
              }}
            >
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span style={{ fontSize: "1.1rem", fontWeight: 600, color: "#1e293b" }}>
                    {item.courseTitle}
                  </span>
                  <span
                    style={{
                      fontSize: "0.75rem",
                      padding: "0.15rem 0.5rem",
                      borderRadius: "0.25rem",
                      background: st.bg,
                      color: st.color,
                      fontWeight: 600,
                    }}
                  >
                    {st.label}
                  </span>
                </div>
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                  شناسه دوره: {item.courseCode} | تاریخ ثبت‌نام: {item.enrolledAt}
                </div>
              </div>

              {item.cohortTitle && item.cohortCode && (
                <CohortBadge
                  title={item.cohortTitle}
                  code={item.cohortCode}
                  currentCount={item.currentCount ?? 15}
                  maxCapacity={item.maxCapacity ?? 30}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
