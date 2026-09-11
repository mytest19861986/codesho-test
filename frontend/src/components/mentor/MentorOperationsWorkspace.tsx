"use client";

import React, { useState } from "react";
import styles from "./mentor_operations.module.css";

export interface CaseloadItemData {
  id: string;
  studentName: string;
  studentId: string;
  capacityWeight: string;
  assignedAt: string;
  isActive: boolean;
  focusArea: string;
}

export interface SupportQueueItemData {
  id: string;
  studentName: string;
  urgencyLevel: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
  queueStatus: "PENDING" | "IN_REVIEW" | "RESOLVED" | "DISMISSED";
  dueDate: string;
  sourceType: string;
  details: string;
}

export interface CheckInItemData {
  id: string;
  studentName: string;
  status: "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "RESCHEDULED" | "CANCELLED";
  scheduledStart: string;
  meetingLink?: string;
  notes?: string;
  commitmentsCount: number;
}

export interface ProgramAnalyticsData {
  totalAssignedStudents: number;
  totalActiveInterventions: number;
  totalCompletedCheckins: number;
  averageResponseTimeHours: string;
  supportCoverageRatio: string;
  aggregatedAt: string;
}

interface MentorOperationsWorkspaceProps {
  caseload: CaseloadItemData[];
  supportQueue: SupportQueueItemData[];
  checkins: CheckInItemData[];
  analytics: ProgramAnalyticsData;
  onResolveQueueItem?: (id: string, notes: string) => void;
  onStartCheckin?: (id: string) => void;
  onCompleteCheckin?: (id: string, notes: string) => void;
}

export const MentorOperationsWorkspace: React.FC<MentorOperationsWorkspaceProps> = ({
  caseload,
  supportQueue,
  checkins,
  analytics,
  onResolveQueueItem,
  onStartCheckin,
  onCompleteCheckin,
}) => {
  const [activeTab, setActiveTab] = useState<"CASELOAD" | "SUPPORT_QUEUE" | "CHECKINS" | "ANALYTICS">("SUPPORT_QUEUE");
  const [resolutionNotes, setResolutionNotes] = useState<{ [key: string]: string }>({});

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency) {
      case "URGENT":
        return <span className={`${styles.badge} ${styles.badgeUrgent}`}>بسیار فوری</span>;
      case "HIGH":
        return <span className={`${styles.badge} ${styles.badgeUrgent}`}>اولویت بالا</span>;
      case "MEDIUM":
        return <span className={`${styles.badge} ${styles.badgeMedium}`}>اولویت متوسط</span>;
      case "LOW":
        return <span className={`${styles.badge} ${styles.badgeLow}`}>اولویت عادی</span>;
      default:
        return <span className={styles.badge}>{urgency}</span>;
    }
  };

  const getCheckinStatusBadge = (status: string) => {
    switch (status) {
      case "SCHEDULED":
        return <span className={`${styles.badge} ${styles.badgeScheduled}`}>برنامه‌ریزی‌شده</span>;
      case "IN_PROGRESS":
        return <span className={`${styles.badge} ${styles.badgeUrgent}`}>در حال برگزاری</span>;
      case "COMPLETED":
        return <span className={`${styles.badge} ${styles.badgeCompleted}`}>انجام شد</span>;
      default:
        return <span className={styles.badge}>{status}</span>;
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>مرکز عملیات و پشتیبانی منتور</h1>
        <p className={styles.subtitle}>
          مدیریت بار کاری، صف پیگیری‌های اولویت‌دار، جلسات بررسی پیشرفت (Check-ins) و پایش سلامت آموزشی بدون رتبه‌بندی یا نمره‌دهی رفتاری.
        </p>
      </header>

      {/* Program Operations Metrics Overview */}
      <section className={styles.statsGrid} aria-label="خلاصه شاخص‌های عملیاتی برنامه">
        <div className={styles.statCard}>
          <div className={styles.statLabel}>دانش‌آموزان تحت پوشش</div>
          <div className={styles.statValue}>
            <bdi dir="ltr">{analytics.totalAssignedStudents}</bdi>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>موارد صف در انتظار پیگیری</div>
          <div className={styles.statValue}>
            <bdi dir="ltr">{analytics.totalActiveInterventions}</bdi>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>جلسات چک‌این تکمیل‌شده</div>
          <div className={styles.statValue}>
            <bdi dir="ltr">{analytics.totalCompletedCheckins}</bdi>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>میانگین زمان پاسخ‌گویی</div>
          <div className={styles.statValue}>
            <bdi dir="ltr">{analytics.averageResponseTimeHours} ساعت</bdi>
          </div>
        </div>
      </section>

      {/* Navigation Tabs */}
      <nav className={styles.tabBar} role="tablist" aria-label="بخش‌های میز کار منتور">
        <button
          role="tab"
          aria-selected={activeTab === "SUPPORT_QUEUE"}
          className={`${styles.tabButton} ${activeTab === "SUPPORT_QUEUE" ? styles.tabButtonActive : ""}`}
          onClick={() => setActiveTab("SUPPORT_QUEUE")}
        >
          صف پشتیبانی و پیگیری ({supportQueue.length})
        </button>
        <button
          role="tab"
          aria-selected={activeTab === "CASELOAD"}
          className={`${styles.tabButton} ${activeTab === "CASELOAD" ? styles.tabButtonActive : ""}`}
          onClick={() => setActiveTab("CASELOAD")}
        >
          تخصیص بار کاری (Caseload) ({caseload.length})
        </button>
        <button
          role="tab"
          aria-selected={activeTab === "CHECKINS"}
          className={`${styles.tabButton} ${activeTab === "CHECKINS" ? styles.tabButtonActive : ""}`}
          onClick={() => setActiveTab("CHECKINS")}
        >
          جلسات چک‌این و تعهدات ({checkins.length})
        </button>
        <button
          role="tab"
          aria-selected={activeTab === "ANALYTICS"}
          className={`${styles.tabButton} ${activeTab === "ANALYTICS" ? styles.tabButtonActive : ""}`}
          onClick={() => setActiveTab("ANALYTICS")}
        >
          تحلیل اثربخشی برنامه
        </button>
      </nav>

      {/* Tab: Support Queue */}
      {activeTab === "SUPPORT_QUEUE" && (
        <section aria-labelledby="queue-heading">
          <div className={styles.sectionHeader}>
            <h2 id="queue-heading" className={styles.sectionTitle}>موارد فعال صف پشتیبانی منتور</h2>
          </div>
          {supportQueue.length === 0 ? (
            <div className={styles.emptyState}>موردی در صف پشتیبانی وجود ندارد. تمام پیگیری‌ها به‌روز هستند.</div>
          ) : (
            <div className={styles.grid}>
              {supportQueue.map((item) => (
                <article key={item.id} className={styles.card}>
                  <div>
                    <div className={styles.cardHeader}>
                      <h3 className={styles.cardTitle}>{item.studentName}</h3>
                      {getUrgencyBadge(item.urgencyLevel)}
                    </div>
                    <div className={styles.metaRow}>
                      <span>مهلت اقدام: <bdi dir="ltr">{item.dueDate}</bdi></span>
                      <span>منبع: {item.sourceType}</span>
                    </div>
                    <p className={styles.description}>{item.details}</p>
                  </div>
                  <div className={styles.actionRow}>
                    <input
                      type="text"
                      placeholder="یادداشت رفع مورد..."
                      value={resolutionNotes[item.id] || ""}
                      onChange={(e) => setResolutionNotes({ ...resolutionNotes, [item.id]: e.target.value })}
                      style={{
                        flex: 1,
                        padding: "0.5rem 0.75rem",
                        borderRadius: "0.375rem",
                        border: "1px solid #cbd5e1",
                        fontSize: "0.875rem",
                        direction: "rtl",
                      }}
                    />
                    <button
                      className={styles.btnPrimary}
                      onClick={() => onResolveQueueItem?.(item.id, resolutionNotes[item.id] || "اقدام لازم انجام شد.")}
                    >
                      تکمیل و رفع
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Tab: Caseload */}
      {activeTab === "CASELOAD" && (
        <section aria-labelledby="caseload-heading">
          <div className={styles.sectionHeader}>
            <h2 id="caseload-heading" className={styles.sectionTitle}>فهرست فراگیران تخصیص‌یافته</h2>
          </div>
          {caseload.length === 0 ? (
            <div className={styles.emptyState}>هیچ دانش‌آموزی در حال حاضر به این منتور تخصیص داده نشده است.</div>
          ) : (
            <div className={styles.grid}>
              {caseload.map((student) => (
                <article key={student.id} className={styles.card}>
                  <div>
                    <div className={styles.cardHeader}>
                      <h3 className={styles.cardTitle}>{student.studentName}</h3>
                      <span className={`${styles.badge} ${styles.badgeActive}`}>فعال</span>
                    </div>
                    <div className={styles.metaRow}>
                      <span>ضریب ظرفیت: <bdi dir="ltr">{student.capacityWeight}</bdi></span>
                      <span>تاریخ تخصیص: <bdi dir="ltr">{student.assignedAt}</bdi></span>
                    </div>
                    <p className={styles.description}>حوزه تمرکز: {student.focusArea}</p>
                  </div>
                  <div className={styles.actionRow}>
                    <button className={styles.btnSecondary}>مشاهده پرونده آموزشی</button>
                    <button className={styles.btnPrimary}>زمان‌بندی چک‌این</button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Tab: Check-ins */}
      {activeTab === "CHECKINS" && (
        <section aria-labelledby="checkins-heading">
          <div className={styles.sectionHeader}>
            <h2 id="checkins-heading" className={styles.sectionTitle}>جلسات گفت‌وگو و بررسی منظم پیشرفت</h2>
          </div>
          {checkins.length === 0 ? (
            <div className={styles.emptyState}>جلسه چک‌این برنامه‌ریزی‌شده‌ای ثبت نشده است.</div>
          ) : (
            <div className={styles.grid}>
              {checkins.map((checkin) => (
                <article key={checkin.id} className={styles.card}>
                  <div>
                    <div className={styles.cardHeader}>
                      <h3 className={styles.cardTitle}>{checkin.studentName}</h3>
                      {getCheckinStatusBadge(checkin.status)}
                    </div>
                    <div className={styles.metaRow}>
                      <span>زمان جلسه: <bdi dir="ltr">{checkin.scheduledStart}</bdi></span>
                      <span>تعهدات ثبت‌شده: <bdi dir="ltr">{checkin.commitmentsCount}</bdi></span>
                    </div>
                    {checkin.notes && <p className={styles.description}>{checkin.notes}</p>}
                  </div>
                  <div className={styles.actionRow}>
                    {checkin.status === "SCHEDULED" && (
                      <button className={styles.btnPrimary} onClick={() => onStartCheckin?.(checkin.id)}>
                        شروع جلسه
                      </button>
                    )}
                    {checkin.status === "IN_PROGRESS" && (
                      <button className={styles.btnPrimary} onClick={() => onCompleteCheckin?.(checkin.id, "جلسه با موفقیت به پایان رسید.")}>
                        تکمیل جلسه
                      </button>
                    )}
                    {checkin.meetingLink && (
                      <a
                        href={checkin.meetingLink}
                        target="_blank"
                        rel="noreferrer"
                        className={styles.btnSecondary}
                        style={{ display: "inline-flex", alignItems: "center", textDecoration: "none" }}
                      >
                        لینک جلسه
                      </a>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Tab: Analytics */}
      {activeTab === "ANALYTICS" && (
        <section aria-labelledby="analytics-heading">
          <div className={styles.sectionHeader}>
            <h2 id="analytics-heading" className={styles.sectionTitle}>گزارش تحلیلی اثربخشی پشتیبانی آموزشی</h2>
          </div>
          <div className={styles.card}>
            <h3 className={styles.cardTitle} style={{ marginBottom: "1rem" }}>
              اصل عدم اقتدار و محافظت از خودکارآمدی فراگیر (Learner Agency)
            </h3>
            <p className={styles.description}>
              این داده‌ها صرفاً وضعیت جریان کاری و کیفیت پاسخ‌دهی منتورها را اندازه‌گیری می‌کنند. هیچ‌گونه نمره انضباطی، رتبه‌بندی رقابتی، یا رده‌بندی روانی از فراگیران استخراج نمی‌شود.
            </p>
            <div className={styles.metaRow} style={{ marginTop: "1rem" }}>
              <span>نسبت پوشش پشتیبانی: <bdi dir="ltr">{(parseFloat(analytics.supportCoverageRatio) * 100).toFixed(1)}%</bdi></span>
              <span>آخرین محاسبه: <bdi dir="ltr">{analytics.aggregatedAt}</bdi></span>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};
