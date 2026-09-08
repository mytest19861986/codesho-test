"use client";

import React, { useEffect, useState } from "react";
import { CohortKpiCards, CohortKpiData } from "./CohortKpiCards";
import { StudentAlertTable, SupervisionAlertData } from "./StudentAlertTable";

interface CohortOrchestrationScreenProps {
  cohortId: string;
  mentorId: string;
}

export const CohortOrchestrationScreen: React.FC<CohortOrchestrationScreenProps> = ({
  cohortId,
  mentorId,
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [kpiData, setKpiData] = useState<CohortKpiData | null>(null);
  const [alerts, setAlerts] = useState<SupervisionAlertData[]>([]);

  const fetchCohortData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 1. Fetch KPI Analytics
      const kpiRes = await fetch(`/api/v1/learning/mentor/cohorts/${cohortId}/analytics/`, {
        headers: { "X-Mentor-Id": mentorId },
      });
      if (!kpiRes.ok) {
        if (kpiRes.status === 404) {
          throw new Error("کوهورت مورد نظر یافت نشد یا شما دسترسی نظارت بر آن را ندارید.");
        }
        throw new Error("خطا در دریافت داده‌های تحلیلی کوهورت.");
      }
      const kpiJson = await kpiRes.json();
      setKpiData({
        totalEnrolled: kpiJson.total_enrolled,
        activeStudents: kpiJson.active_students,
        completedStudents: kpiJson.completed_students,
        averageProgressPercentage: kpiJson.average_progress_percentage,
        averageAssessmentScore: kpiJson.average_assessment_score,
        completionRate: kpiJson.completion_rate,
        asOf: kpiJson.as_of,
      });

      // 2. Fetch Alerts
      const alertsRes = await fetch(`/api/v1/learning/mentor/cohorts/${cohortId}/alerts/`, {
        headers: { "X-Mentor-Id": mentorId },
      });
      if (alertsRes.ok) {
        const alertsJson = await alertsRes.json();
        setAlerts(
          (alertsJson.alerts || []).map((a: any) => ({
            id: a.id,
            studentId: a.student_id,
            alertType: a.alert_type,
            severity: a.severity,
            status: a.status,
            details: a.details,
            createdAt: a.created_at,
          }))
        );
      }
    } catch (err: any) {
      setError(err.message || "خطایی در بارگذاری داشبورد رخ داد.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCohortData();
  }, [cohortId, mentorId]);

  const handleTransitionStatus = async (alertId: string, targetStatus: "ACKNOWLEDGED" | "RESOLVED") => {
    try {
      const res = await fetch(`/api/v1/learning/mentor/cohorts/${cohortId}/alerts/${alertId}/transition/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Mentor-Id": mentorId,
        },
        body: JSON.stringify({ status: targetStatus }),
      });

      if (res.ok) {
        setAlerts((prev) =>
          prev.map((a) => (a.id === alertId ? { ...a, status: targetStatus } : a))
        );
      }
    } catch (err) {
      console.error("Failed to transition alert status:", err);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "3rem", textAlign: "center", direction: "rtl", color: "#64748b" }}>
        در حال بارگذاری شاخص‌های تحلیلی و وضعیت کوهورت...
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          padding: "1.5rem",
          margin: "1.5rem 0",
          backgroundColor: "#fef2f2",
          border: "1px solid #fecaca",
          borderRadius: "0.75rem",
          color: "#991b1b",
          direction: "rtl",
        }}
      >
        {error}
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "2rem",
        direction: "rtl",
        padding: "1.5rem 0",
        fontFamily: "var(--cs-font-family-base, inherit)",
      }}
    >
      <header style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "1rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700, color: "#0f172a" }}>
          داشبورد نظارت سازمانی و ارکستراسیون کوهورت
        </h1>
        <p style={{ margin: "0.5rem 0 0 0", color: "#64748b", fontSize: "0.875rem" }}>
          ارزیابی شاخص‌های کلیدی، هشدارهای خودکار پیشرفت و نظارت آموزشی چندمستأجری.
        </p>
      </header>

      {kpiData && <CohortKpiCards data={kpiData} />}

      <StudentAlertTable alerts={alerts} onTransitionStatus={handleTransitionStatus} />
    </div>
  );
};
