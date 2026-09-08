"use client";

import React from "react";

export interface SupervisionAlertData {
  id: string;
  studentId: string;
  alertType: "STALLED_PROGRESS" | "FAILED_ASSESSMENTS" | "AT_RISK_DROPOUT";
  severity: "LOW" | "MEDIUM" | "HIGH";
  status: "ACTIVE" | "ACKNOWLEDGED" | "RESOLVED";
  details: Record<string, any>;
  createdAt: string;
}

interface StudentAlertTableProps {
  alerts: SupervisionAlertData[];
  onTransitionStatus: (alertId: string, targetStatus: "ACKNOWLEDGED" | "RESOLVED") => Promise<void>;
}

export const StudentAlertTable: React.FC<StudentAlertTableProps> = ({ alerts, onTransitionStatus }) => {
  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "HIGH":
        return { text: "بحرانی (High)", color: "#b91c1c", bg: "#fef2f2", border: "#fecaca" };
      case "MEDIUM":
        return { text: "متوسط (Medium)", color: "#b45309", bg: "#fffbeb", border: "#fde68a" };
      case "LOW":
      default:
        return { text: "پایین (Low)", color: "#047857", bg: "#f0fdf4", border: "#bbf7d0" };
    }
  };

  const getAlertTypeText = (type: string) => {
    switch (type) {
      case "STALLED_PROGRESS":
        return "توقف پیشرفت درسی";
      case "FAILED_ASSESSMENTS":
        return "مردودی مکرر در آزمون";
      case "AT_RISK_DROPOUT":
        return "احتمال بالای ترک دوره";
      default:
        return type;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return { text: "فعال", color: "#dc2626", bg: "#fee2e2" };
      case "ACKNOWLEDGED":
        return { text: "بررسی‌شده", color: "#d97706", bg: "#fef3c7" };
      case "RESOLVED":
        return { text: "حل‌شده", color: "#16a34a", bg: "#dcfce7" };
      default:
        return { text: status, color: "#475569", bg: "#f1f5f9" };
    }
  };

  return (
    <div
      style={{
        backgroundColor: "#ffffff",
        borderRadius: "0.875rem",
        border: "1px solid #e2e8f0",
        boxShadow: "0 1px 3px rgba(0, 0, 0, 0.05)",
        overflow: "hidden",
        direction: "rtl",
        fontFamily: "var(--cs-font-family-base, inherit)",
      }}
    >
      <div style={{ padding: "1.25rem", borderBottom: "1px solid #e2e8f0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0, fontSize: "1.125rem", fontWeight: 600, color: "#0f172a" }}>
          هشدارهای تحصیلی و ریسک آموزشی فراگیران
        </h3>
        <span style={{ fontSize: "0.875rem", color: "#64748b" }}>
          مجموع: {alerts.length} مورد
        </span>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "right" }}>
          <thead>
            <tr style={{ backgroundColor: "#f8fafc", borderBottom: "1px solid #e2e8f0" }}>
              <th style={{ padding: "0.75rem 1rem", fontSize: "0.8125rem", fontWeight: 600, color: "#475569" }}>شناسه فراگیر</th>
              <th style={{ padding: "0.75rem 1rem", fontSize: "0.8125rem", fontWeight: 600, color: "#475569" }}>نوع هشدار</th>
              <th style={{ padding: "0.75rem 1rem", fontSize: "0.8125rem", fontWeight: 600, color: "#475569" }}>شدت ریسک</th>
              <th style={{ padding: "0.75rem 1rem", fontSize: "0.8125rem", fontWeight: 600, color: "#475569" }}>وضعیت</th>
              <th style={{ padding: "0.75rem 1rem", fontSize: "0.8125rem", fontWeight: 600, color: "#475569" }}>عملیات منتور</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: "2rem", textAlign: "center", color: "#64748b", fontSize: "0.875rem" }}>
                  هیچ هشداری برای این کوهورت ثبت نشده است. عملکرد فراگیران در وضعیت مطلوب قرار دارد.
                </td>
              </tr>
            ) : (
              alerts.map((alert) => {
                const sev = getSeverityBadge(alert.severity);
                const st = getStatusBadge(alert.status);
                return (
                  <tr key={alert.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "0.875rem 1rem", fontSize: "0.875rem", color: "#1e293b" }}>
                      <bdi dir="ltr" style={{ fontFamily: "monospace", color: "#2563eb" }}>
                        {alert.studentId.slice(0, 8)}...
                      </bdi>
                    </td>
                    <td style={{ padding: "0.875rem 1rem", fontSize: "0.875rem", color: "#334155" }}>
                      {getAlertTypeText(alert.alertType)}
                    </td>
                    <td style={{ padding: "0.875rem 1rem" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "0.2rem 0.5rem",
                          borderRadius: "0.375rem",
                          fontSize: "0.75rem",
                          fontWeight: 600,
                          color: sev.color,
                          backgroundColor: sev.bg,
                          border: `1px solid ${sev.border}`,
                        }}
                      >
                        {sev.text}
                      </span>
                    </td>
                    <td style={{ padding: "0.875rem 1rem" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "0.2rem 0.5rem",
                          borderRadius: "9999px",
                          fontSize: "0.75rem",
                          fontWeight: 600,
                          color: st.color,
                          backgroundColor: st.bg,
                        }}
                      >
                        {st.text}
                      </span>
                    </td>
                    <td style={{ padding: "0.875rem 1rem" }}>
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        {alert.status === "ACTIVE" && (
                          <button
                            onClick={() => onTransitionStatus(alert.id, "ACKNOWLEDGED")}
                            style={{
                              minHeight: "44px",
                              minWidth: "44px",
                              padding: "0.375rem 0.75rem",
                              backgroundColor: "#f1f5f9",
                              border: "1px solid #cbd5e1",
                              borderRadius: "0.375rem",
                              fontSize: "0.75rem",
                              fontWeight: 600,
                              color: "#334155",
                              cursor: "pointer",
                            }}
                          >
                            ثبت در دست بررسی
                          </button>
                        )}
                        {alert.status !== "RESOLVED" && (
                          <button
                            onClick={() => onTransitionStatus(alert.id, "RESOLVED")}
                            style={{
                              minHeight: "44px",
                              minWidth: "44px",
                              padding: "0.375rem 0.75rem",
                              backgroundColor: "#10b981",
                              border: "none",
                              borderRadius: "0.375rem",
                              fontSize: "0.75rem",
                              fontWeight: 600,
                              color: "#ffffff",
                              cursor: "pointer",
                            }}
                          >
                            تأیید رفع مشکل
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
