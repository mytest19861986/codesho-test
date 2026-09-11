"use client";

import React, { useState } from "react";
import styles from "./curriculum_authoring.module.css";

export interface WorkspaceItem {
  id: string;
  courseTitle: string;
  workspaceTitle: string;
  status: "ACTIVE" | "SUBMITTED" | "ARCHIVED";
  createdAt: string;
}

export interface ChangeSetItem {
  id: string;
  title: string;
  changeSummary: string;
  status: "DRAFT" | "IN_REVIEW" | "CHANGES_REQUESTED" | "APPROVED" | "MERGED_TO_RELEASE";
  authorName: string;
  createdAt: string;
}

export interface RubricItem {
  id: string;
  rubricTitle: string;
  scaleType: string;
  status: "DRAFT" | "ACTIVE" | "SUPERSEDED" | "RETIRED";
  isAntiRankingCompliant: boolean;
  criteriaCount: number;
}

export interface ReadinessGateItem {
  id: string;
  gateName: string;
  isBlocking: boolean;
  verdict: "PENDING" | "PASSED" | "FAILED" | "WAIVED";
  evaluatedAt: string;
}

export interface RollforwardPlanItem {
  id: string;
  cohortName: string;
  targetReleaseTag: string;
  mode: "FUTURE_MODULES_ONLY" | "NEXT_COHORT_ONLY" | "EXPLICIT_APPROVAL_REQUIRED";
  status: "DRAFT" | "APPROVED" | "APPLIED" | "CANCELLED";
  scheduledDate: string;
}

interface CurriculumAuthoringWorkspaceProps {
  workspaces: WorkspaceItem[];
  changeSets: ChangeSetItem[];
  rubrics: RubricItem[];
  readinessGates: ReadinessGateItem[];
  rollforwardPlans: RollforwardPlanItem[];
  onSubmitChangeSet?: (id: string) => void;
  onApproveChangeSet?: (id: string) => void;
  onEvaluateGates?: () => void;
}

export const CurriculumAuthoringWorkspace: React.FC<CurriculumAuthoringWorkspaceProps> = ({
  workspaces,
  changeSets,
  rubrics,
  readinessGates,
  rollforwardPlans,
  onSubmitChangeSet,
  onApproveChangeSet,
  onEvaluateGates,
}) => {
  const [activeTab, setActiveTab] = useState<
    "WORKSPACES" | "CHANGESETS" | "RUBRICS" | "READINESS" | "ROLLFORWARD"
  >("WORKSPACES");

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ACTIVE":
      case "PASSED":
        return <span className={`${styles.badge} ${styles.badgePassed}`}>فعال / قبول</span>;
      case "APPROVED":
        return <span className={`${styles.badge} ${styles.badgeApproved}`}>تأیید شده</span>;
      case "IN_REVIEW":
      case "PENDING":
        return <span className={`${styles.badge} ${styles.badgePending}`}>در حال بررسی</span>;
      case "CHANGES_REQUESTED":
      case "FAILED":
        return <span className={`${styles.badge} ${styles.badgeFailed}`}>نیاز به بازبینی / رد</span>;
      case "WAIVED":
        return <span className={`${styles.badge} ${styles.badgeWaived}`}>مستثنی شده</span>;
      case "DRAFT":
      default:
        return <span className={`${styles.badge} ${styles.badgeDraft}`}>پیش‌نویس</span>;
    }
  };

  return (
    <div className={styles.container} dir="rtl">
      <header className={styles.header}>
        <h1 className={styles.title}>مرکز عملیات و تألیف سرفصل، کیفیت و انتشار (P3-Epic 23-25)</h1>
        <p className={styles.subtitle}>
          محیط حاکمیتی تألیف و ویرایش سرفصل، نقشه‌های ارزیابی و روبریک‌های بدون رتبه‌بندی، دروازه‌های آمادگی انتشار و انتقال ایمن دوره‌ها
        </p>
      </header>

      <nav className={styles.tabList} aria-label="مدیریت سرفصل و انتشار">
        <button
          className={`${styles.tabButton} ${activeTab === "WORKSPACES" ? styles.activeTab : ""}`}
          onClick={() => setActiveTab("WORKSPACES")}
          type="button"
        >
          فضاهای کاری تألیف ({workspaces.length})
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === "CHANGESETS" ? styles.activeTab : ""}`}
          onClick={() => setActiveTab("CHANGESETS")}
          type="button"
        >
          دسته‌های تغییرات و داوری ({changeSets.length})
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === "RUBRICS" ? styles.activeTab : ""}`}
          onClick={() => setActiveTab("RUBRICS")}
          type="button"
        >
          روبریک‌های ارزیابی کیفی ({rubrics.length})
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === "READINESS" ? styles.activeTab : ""}`}
          onClick={() => setActiveTab("READINESS")}
          type="button"
        >
          دروازه‌های آمادگی انتشار ({readinessGates.length})
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === "ROLLFORWARD" ? styles.activeTab : ""}`}
          onClick={() => setActiveTab("ROLLFORWARD")}
          type="button"
        >
          برنامه‌های انتقال دوره ({rollforwardPlans.length})
        </button>
      </nav>

      <main className={styles.panel}>
        {/* Tab 1: Workspaces */}
        {activeTab === "WORKSPACES" && (
          <div>
            <div className={styles.alertBox}>
              <strong>اصل استقلال مستأجر:</strong> کلیه فضاهای کاری به سرفصل کانونیکال پایه متصل بوده و تفکیک داده‌ای کامل اعمال شده است.
            </div>
            <div className={styles.grid} style={{ marginTop: "1rem" }}>
              {workspaces.map((ws) => (
                <div key={ws.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h2 className={styles.cardTitle}>{ws.workspaceTitle}</h2>
                    {getStatusBadge(ws.status)}
                  </div>
                  <div className={styles.cardMeta}>
                    <span><strong>دوره:</strong> {ws.courseTitle}</span>
                    <span><strong>شناسه:</strong> <bdi dir="ltr">{ws.id.slice(0, 8)}...</bdi></span>
                    <span><strong>تاریخ ایجاد:</strong> {ws.createdAt}</span>
                  </div>
                  <div className={styles.actions}>
                    <button className={`${styles.actionButton} ${styles.primaryAction}`} type="button">
                      ورود به ویرایشگر
                    </button>
                  </div>
                </div>
              ))}
              {workspaces.length === 0 && (
                <div className={styles.emptyState}>هیچ فضای کاری تألیفی تعریف نشده است.</div>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: ChangeSets */}
        {activeTab === "CHANGESETS" && (
          <div>
            <div className={styles.warningBox}>
              <strong>تفکیک وظایف (Separation of Duties):</strong> نویسنده بسته تغییرات مجاز به تأیید نهایی آن نمی‌باشد (AUTHOR_SELF_APPROVAL: DENY).
            </div>
            <div className={styles.grid} style={{ marginTop: "1rem" }}>
              {changeSets.map((cs) => (
                <div key={cs.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h2 className={styles.cardTitle}>{cs.title}</h2>
                    {getStatusBadge(cs.status)}
                  </div>
                  <div className={styles.cardMeta}>
                    <span><strong>خلاصه:</strong> {cs.changeSummary}</span>
                    <span><strong>نویسنده:</strong> {cs.authorName}</span>
                    <span><strong>شناسه:</strong> <bdi dir="ltr">{cs.id.slice(0, 8)}...</bdi></span>
                  </div>
                  <div className={styles.actions}>
                    {cs.status === "DRAFT" && (
                      <button
                        className={`${styles.actionButton} ${styles.primaryAction}`}
                        onClick={() => onSubmitChangeSet?.(cs.id)}
                        type="button"
                      >
                        ارسال جهت داوری همتا
                      </button>
                    )}
                    {cs.status === "IN_REVIEW" && (
                      <button
                        className={`${styles.actionButton} ${styles.primaryAction}`}
                        onClick={() => onApproveChangeSet?.(cs.id)}
                        type="button"
                      >
                        ثبت رأی هیئت تحریریه
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {changeSets.length === 0 && (
                <div className={styles.emptyState}>هیچ بسته تغییراتی ثبت نشده است.</div>
              )}
            </div>
          </div>
        )}

        {/* Tab 3: Rubrics */}
        {activeTab === "RUBRICS" && (
          <div>
            <div className={styles.alertBox}>
              <strong>اصل حاکمیتی منع رتبه‌بندی:</strong> کلیه روبریک‌ها صرفاً بر معیارهای شایستگی و یادگیری تمرکز داشته و رتبه‌بندی دانش‌آموزان صفر مطلق است.
            </div>
            <div className={styles.grid} style={{ marginTop: "1rem" }}>
              {rubrics.map((r) => (
                <div key={r.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h2 className={styles.cardTitle}>{r.rubricTitle}</h2>
                    {getStatusBadge(r.status)}
                  </div>
                  <div className={styles.cardMeta}>
                    <span><strong>نوع مقیاس:</strong> {r.scaleType}</span>
                    <span><strong>تعداد معیارها:</strong> {r.criteriaCount} معیار</span>
                    <span>
                      <strong>پایبندی به منع رتبه‌بندی:</strong>{" "}
                      {r.isAntiRankingCompliant ? "✅ منطبق ۱۰۰٪" : "❌ مغایر"}
                    </span>
                  </div>
                </div>
              ))}
              {rubrics.length === 0 && (
                <div className={styles.emptyState}>هیچ روبریک فعالی یافت نشد.</div>
              )}
            </div>
          </div>
        )}

        {/* Tab 4: Readiness Gates */}
        {activeTab === "READINESS" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <div className={styles.alertBox} style={{ margin: 0, flex: 1 }}>
                <strong>دروازه‌های مسدودکننده انتشار:</strong> انتشار نهایی نسخه سرفصل نیازمند قبولی ۱۰۰٪ کلیه گیت‌های مسدودکننده است.
              </div>
              <button
                className={`${styles.actionButton} ${styles.primaryAction}`}
                onClick={() => onEvaluateGates?.()}
                style={{ marginRight: "1rem" }}
                type="button"
              >
                ارزیابی مجدد گیت‌ها
              </button>
            </div>
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>نام دروازه آمادگی</th>
                    <th>نوع الزام</th>
                    <th>وضعیت نتیجه</th>
                    <th>زمان ارزیابی</th>
                  </tr>
                </thead>
                <tbody>
                  {readinessGates.map((gate) => (
                    <tr key={gate.id}>
                      <td><strong>{gate.gateName}</strong></td>
                      <td>{gate.isBlocking ? "مسدودکننده (الزامی)" : "هشدار / اختیاری"}</td>
                      <td>{getStatusBadge(gate.verdict)}</td>
                      <td>{gate.evaluatedAt}</td>
                    </tr>
                  ))}
                  {readinessGates.length === 0 && (
                    <tr>
                      <td colSpan={4} className={styles.emptyState}>گیت آمادگی تعریف نشده است.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 5: Rollforward */}
        {activeTab === "ROLLFORWARD" && (
          <div>
            <div className={styles.warningBox}>
              <strong>منع اتصال مجدد شواهد گذشته:</strong> انتقال به نگارش جدید صرفاً بر ماژول‌های آتی اعمال شده و کارنامه‌ها و شواهد گذشته غیرقابل‌تغییر باقی می‌مانند.
            </div>
            <div className={styles.grid} style={{ marginTop: "1rem" }}>
              {rollforwardPlans.map((plan) => (
                <div key={plan.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h2 className={styles.cardTitle}>{plan.cohortName}</h2>
                    {getStatusBadge(plan.status)}
                  </div>
                  <div className={styles.cardMeta}>
                    <span><strong>نگارش مقصد:</strong> <bdi dir="ltr">{plan.targetReleaseTag}</bdi></span>
                    <span><strong>شیوه انتقال:</strong> {plan.mode}</span>
                    <span><strong>تاریخ اعمال:</strong> {plan.scheduledDate}</span>
                  </div>
                </div>
              ))}
              {rollforwardPlans.length === 0 && (
                <div className={styles.emptyState}>برنامه انتقالی ثبت نشده است.</div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
