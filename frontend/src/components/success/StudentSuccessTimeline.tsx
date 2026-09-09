"use client";

import React from "react";
import styles from "./success.module.css";

export interface SuccessPlanData {
  id: string;
  title: string;
  targetPeriod: string;
  status: "ACTIVE" | "PAUSED" | "COMPLETED" | "SUPERSEDED" | "ARCHIVED";
  notes?: string;
  createdAt: string;
}

export interface ActionStepData {
  id: string;
  sequenceOrder: number;
  title: string;
  description?: string;
  status: "PENDING" | "IN_PROGRESS" | "COMPLETED" | "SKIPPED" | "CANCELLED";
  isAuthoritative: boolean;
  targetDate?: string;
}

export interface TimelineEventData {
  id: string;
  eventType: "GOAL_ANCHORED" | "INSIGHT_CONNECTED" | "REFLECTION_TIED" | "ACTION_DISPATCHED" | "MILESTONE_PROGRESSION" | "TIMELINE_EVENT_AMENDED";
  headline: string;
  detail?: string;
  createdAt: string;
  replacesEventId?: string;
}

interface StudentSuccessTimelineProps {
  studentName?: string;
  plan: SuccessPlanData;
  actionSteps: ActionStepData[];
  timelineEvents: TimelineEventData[];
  onTransitionStep?: (stepId: string, newStatus: string) => void;
}

export const StudentSuccessTimeline: React.FC<StudentSuccessTimelineProps> = ({
  studentName = "دانش‌آموز کوشای کدشو",
  plan,
  actionSteps,
  timelineEvents,
  onTransitionStep,
}) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return <span className={`${styles.badge} ${styles.badgeActive}`}>برنامه فعال در حال اجرا</span>;
      case "PAUSED":
        return <span className={`${styles.badge} ${styles.badgePaused}`}>مکث بدون قضاوت</span>;
      case "COMPLETED":
        return <span className={`${styles.badge} ${styles.badgeCompleted}`}>تکمیل با موفقیت</span>;
      default:
        return <span className={styles.badge}>{status}</span>;
    }
  };

  const getStepStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return <span className={`${styles.badge} ${styles.badgeActive}`}>تکمیل شد</span>;
      case "IN_PROGRESS":
        return <span className={`${styles.badge} ${styles.badgePaused}`}>در حال انجام</span>;
      case "SKIPPED":
        return <span className={styles.badge}>صرف‌نظر موقت</span>;
      default:
        return <span className={styles.badge}>در انتظار اقدام</span>;
    }
  };

  const getEventTypeLabel = (type: string) => {
    switch (type) {
      case "GOAL_ANCHORED":
        return "هدف تحلیلی مهارتی";
      case "INSIGHT_CONNECTED":
        return "بینش شناختی هوشمند";
      case "REFLECTION_TIED":
        return "بازنگری و تامل فردی";
      case "ACTION_DISPATCHED":
        return "گام عملیاتی تکوینی";
      case "MILESTONE_PROGRESSION":
        return "پیشرفت مایلستون";
      case "TIMELINE_EVENT_AMENDED":
        return "اصلاح تکوینی رویداد";
      default:
        return type;
    }
  };

  return (
    <div className={styles.container} data-testid="p3-vs15-success-timeline">
      <header className={styles.header}>
        <h1 className={styles.title}>تداوم یادگیری و نقشه موفقیت تحصیلی</h1>
        <p className={styles.subtitle}>
          برنامه موفقیت و هدایت فردی {studentName} بر اساس تداوم یادگیری درازمدت؛ سنجش صرفاً بر پایه تسلط شخصی و بدون رتبه‌بندی رقابتی یا نمره‌دهی مقایسه‌ای است.
        </p>
      </header>

      {/* Active Success Plan Card */}
      <section className={styles.planCard}>
        <div className={styles.planHeader}>
          <div className={styles.planTitle}>{plan.title}</div>
          {getStatusBadge(plan.status)}
        </div>
        <div className={styles.planMeta}>
          <span><strong>دوره زمانی هدف:</strong> {plan.targetPeriod}</span>
          <span><strong>تاریخ ثبت برنامه:</strong> {plan.createdAt}</span>
        </div>
        {plan.notes && (
          <p className={styles.stepDesc}>
            {plan.notes}
          </p>
        )}
        <div className={styles.nonAuthoritativeNotice}>
          <span>💡</span>
          <span>راهنمایی‌های هوشمند جنبه تکوینی و مشورتی دارند و هیچ تصمیمی به شکل قطعی و الزام‌آور بدون تایید منتور و دانش‌آموز ثبت نمی‌شود.</span>
        </div>
      </section>

      {/* Two Column Grid: Action Steps & Timeline Stream */}
      <div className={styles.gridTwoCol}>
        {/* Granular Action Steps */}
        <section className={styles.sectionCard}>
          <h2 className={styles.sectionTitle}>
            <span>گام‌های اجرایی برنامه</span>
            <span className={styles.badge}>{actionSteps.length} گام</span>
          </h2>
          <div className={styles.stepsList}>
            {actionSteps.map((step) => (
              <div key={step.id} className={styles.stepItem}>
                <div className={styles.stepOrder}>{step.sequenceOrder}</div>
                <div className={styles.stepBody}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div className={styles.stepTitle}>{step.title}</div>
                    {getStepStatusBadge(step.status)}
                  </div>
                  {step.description && <div className={styles.stepDesc}>{step.description}</div>}
                  <div className={styles.stepMeta}>
                    {step.targetDate && <span>موعد پیش‌بینی: {step.targetDate}</span>}
                    {step.status === "PENDING" && onTransitionStep && (
                      <button
                        className={styles.actionButton}
                        style={{ marginTop: "0.5rem", fontSize: "0.8rem", minHeight: "36px", padding: "0.3rem 0.75rem" }}
                        onClick={() => onTransitionStep(step.id, "IN_PROGRESS")}
                      >
                        شروع این گام
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 5-Way XOR Longitudinal Timeline Events */}
        <section className={styles.sectionCard}>
          <h2 className={styles.sectionTitle}>
            <span>روایت تداوم یادگیری (تایم‌لاین رشد)</span>
            <span className={styles.badge}>{timelineEvents.length} رویداد</span>
          </h2>
          <div className={styles.timelineStream}>
            {timelineEvents.map((evt) => (
              <div key={evt.id} className={styles.timelineNode}>
                <div className={styles.timelineMarker} />
                <div className={styles.timelineContent}>
                  <div className={styles.timelineHeader}>
                    <span className={styles.timelineHeadline}>{evt.headline}</span>
                    <span className={styles.timelineType}>{getEventTypeLabel(evt.eventType)}</span>
                  </div>
                  {evt.detail && <p className={styles.timelineDetail}>{evt.detail}</p>}
                  <time className={styles.timelineDate}>{evt.createdAt}</time>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};
