"use client";

import React, { useState } from "react";
import styles from "./coaching.module.css";

export interface CoachingSessionData {
  id: string;
  title: string;
  status: "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
  scheduledAt: string;
  startedAt?: string;
  completedAt?: string;
  summary?: string;
  notes?: CoachingNoteData[];
}

export interface CoachingNoteData {
  id: string;
  noteType: "OBSERVATION" | "STRENGTH" | "GROWTH_OPPORTUNITY" | "ACTION_ITEM" | "SUMMARY";
  content: string;
  createdAt: string;
}

export interface SupportInterventionData {
  id: string;
  title: string;
  category: "ACADEMIC_SCAFFOLDING" | "RESOURCE_RECOMMENDATION" | "STUDY_STRATEGY" | "PACING_ADJUSTMENT" | "PEER_STUDY_CONNECTION";
  status: "PROPOSED" | "ACCEPTED" | "DECLINED" | "ACTIVE" | "PAUSED" | "COMPLETED";
  isAuthoritative: boolean;
  rationale: string;
  studentFeedback?: string;
  proposedAt: string;
}

export interface FollowUpActionData {
  id: string;
  title: string;
  status: "PENDING" | "IN_PROGRESS" | "COMPLETED" | "SKIPPED";
  dueDate: string;
  skipReason?: string;
}

interface StudentCoachingDashboardProps {
  sessions: CoachingSessionData[];
  interventions: SupportInterventionData[];
  actions: FollowUpActionData[];
  onAcceptIntervention?: (id: string, feedback?: string) => void;
  onDeclineIntervention?: (id: string, feedback?: string) => void;
  onCompleteAction?: (id: string) => void;
  onSkipAction?: (id: string, reason: string) => void;
}

export const StudentCoachingDashboard: React.FC<StudentCoachingDashboardProps> = ({
  sessions,
  interventions,
  actions,
  onAcceptIntervention,
  onDeclineIntervention,
  onCompleteAction,
  onSkipAction,
}) => {
  const [activeTab, setActiveTab] = useState<"INTERVENTIONS" | "SESSIONS" | "ACTIONS">("INTERVENTIONS");
  const [feedbackText, setFeedbackText] = useState<{ [key: string]: string }>({});

  const getCategoryTitle = (cat: string) => {
    switch (cat) {
      case "ACADEMIC_SCAFFOLDING":
        return "داربست آموزشی و تقویت مفاهیم پایه‌ای";
      case "RESOURCE_RECOMMENDATION":
        return "پیشنهاد منابع مکمل یادگیری";
      case "STUDY_STRATEGY":
        return "راهبردهای مطالعه و حل مسئله";
      case "PACING_ADJUSTMENT":
        return "تنظیم سرعت و گام‌بندی یادگیری";
      case "PEER_STUDY_CONNECTION":
        return "ارتباط همتایاری و یادگیری تیمی";
      default:
        return cat;
    }
  };

  const getInterventionBadge = (status: string) => {
    switch (status) {
      case "PROPOSED":
        return <span className={`${styles.badge} ${styles.badgeProposed}`}>پیشنهاد منتور (در انتظار تصمیم شما)</span>;
      case "ACCEPTED":
        return <span className={`${styles.badge} ${styles.badgeAccepted}`}>پذیرفته‌شده توسط شما</span>;
      case "DECLINED":
        return <span className={`${styles.badge} ${styles.badgeDeclined}`}>رد شده با احترام به نظر شما</span>;
      case "ACTIVE":
        return <span className={`${styles.badge} ${styles.badgeActive}`}>در حال اجرای برنامه حمایتی</span>;
      case "COMPLETED":
        return <span className={`${styles.badge} ${styles.badgeCompleted}`}>با موفقیت پایان یافت</span>;
      default:
        return <span className={styles.badge}>{status}</span>;
    }
  };

  const getSessionBadge = (status: string) => {
    switch (status) {
      case "SCHEDULED":
        return <span className={`${styles.badge} ${styles.badgeScheduled}`}>برنامه‌ریزی‌شده</span>;
      case "IN_PROGRESS":
        return <span className={`${styles.badge} ${styles.badgeInProgress}`}>جلسه هم‌اکنون فعال است</span>;
      case "COMPLETED":
        return <span className={`${styles.badge} ${styles.badgeCompleted}`}>برگزار و تکمیل شد</span>;
      case "CANCELLED":
        return <span className={`${styles.badge} ${styles.badgeCancelled}`}>لغو شده</span>;
      default:
        return <span className={styles.badge}>{status}</span>;
    }
  };

  return (
    <div className={styles.container} role="main" aria-label="داشبورد هدایت و مربی‌گری تحصیلی">
      <header className={styles.header}>
        <h1 className={styles.title}>مرکز مربی‌گری و مداخلات حمایتی موفقیت تحصیلی</h1>
        <p className={styles.subtitle}>
          در کُدشو، شما عاملیت کامل مسیر یادگیری خود را در دست دارید. پیشنهادات منتورها صرفاً راهنما و تسهیل‌کننده هستند و هیچ تصمیم تحمیلی یا رتبه‌بندی مقایسه‌ای در این فضا وجود ندارد.
        </p>
      </header>

      <div className={styles.agencyNotice} role="status">
        <span aria-hidden="true">💡</span>
        <span>
          <strong>اصل عاملیت یادگیرنده (Learner Agency First):</strong> هیچ مداخله یا برنامه‌ای بدون تأیید صریح شما فعال نخواهد شد و عدم پذیرش یک پیشنهاد هرگز اثری منفی بر سابقه تحصیلی شما نخواهد داشت.
        </span>
      </div>

      {/* Tabs */}
      <div className={styles.buttonGroup} role="tablist" aria-label="بخش‌های داشبورد مربی‌گری">
        <button
          role="tab"
          aria-selected={activeTab === "INTERVENTIONS"}
          className={activeTab === "INTERVENTIONS" ? styles.buttonPrimary : styles.buttonSecondary}
          onClick={() => setActiveTab("INTERVENTIONS")}
        >
          مداخلات حمایتی منتور ({interventions.length})
        </button>
        <button
          role="tab"
          aria-selected={activeTab === "SESSIONS"}
          className={activeTab === "SESSIONS" ? styles.buttonPrimary : styles.buttonSecondary}
          onClick={() => setActiveTab("SESSIONS")}
        >
          جلسات کوچینگ ({sessions.length})
        </button>
        <button
          role="tab"
          aria-selected={activeTab === "ACTIONS"}
          className={activeTab === "ACTIONS" ? styles.buttonPrimary : styles.buttonSecondary}
          onClick={() => setActiveTab("ACTIONS")}
        >
          اقدامات عملیاتی پیگیری ({actions.length})
        </button>
      </div>

      <div style={{ marginTop: "2rem" }}>
        {/* INTERVENTIONS TAB */}
        {activeTab === "INTERVENTIONS" && (
          <section aria-label="فهرست مداخلات حمایتی">
            <h2 className={styles.sectionTitle}>پیشنهادات حمایتی و داربست‌های آموزشی</h2>
            {interventions.length === 0 ? (
              <p className={styles.subtitle}>در حال حاضر هیچ مداخله حمایتی جدیدی ثبت نشده است.</p>
            ) : (
              interventions.map((item) => (
                <article key={item.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <div>
                      <h3 className={styles.cardTitle}>{item.title}</h3>
                      <span className={styles.subtitle} style={{ fontSize: "0.85rem" }}>
                        دسته‌بندی: {getCategoryTitle(item.category)}
                      </span>
                    </div>
                    {getInterventionBadge(item.status)}
                  </div>

                  <div className={styles.metaRow}>
                    <span className={styles.metaItem}>
                      تاریخ پیشنهاد: <bdi dir="ltr" className={styles.bdiIsolation}>{item.proposedAt}</bdi>
                    </span>
                    <span className={styles.metaItem}>
                      سطح عاملیت: <strong>۱۰۰٪ اختیاری و تحت کنترل دانش‌آموز</strong>
                    </span>
                  </div>

                  <div className={styles.rationaleBox}>
                    <strong>دلایل منتور برای پیشنهاد این برنامه:</strong>
                    <p style={{ marginTop: "0.4rem", margin: 0 }}>{item.rationale}</p>
                  </div>

                  {item.studentFeedback && (
                    <div style={{ marginTop: "0.75rem", fontSize: "0.9rem", color: "#1e40af" }}>
                      <strong>بازخورد ثبت‌شده شما:</strong> {item.studentFeedback}
                    </div>
                  )}

                  {item.status === "PROPOSED" && (
                    <div style={{ marginTop: "1rem" }}>
                      <input
                        type="text"
                        placeholder="نظر یا بازخورد شما (اختیاری)..."
                        value={feedbackText[item.id] || ""}
                        onChange={(e) => setFeedbackText({ ...feedbackText, [item.id]: e.target.value })}
                        style={{
                          width: "100%",
                          padding: "0.5rem 0.75rem",
                          borderRadius: "0.5rem",
                          border: "1px solid #cbd5e1",
                          marginBottom: "0.75rem",
                          fontSize: "0.875rem",
                        }}
                      />
                      <div className={styles.buttonGroup}>
                        <button
                          className={styles.buttonSuccess}
                          onClick={() => onAcceptIntervention && onAcceptIntervention(item.id, feedbackText[item.id])}
                        >
                          ✓ پذیرش و آغاز برنامه حمایتی
                        </button>
                        <button
                          className={styles.buttonDanger}
                          onClick={() => onDeclineIntervention && onDeclineIntervention(item.id, feedbackText[item.id])}
                        >
                          ✕ رد محترمانه این پیشنهاد
                        </button>
                      </div>
                    </div>
                  )}
                </article>
              ))
            )}
          </section>
        )}

        {/* SESSIONS TAB */}
        {activeTab === "SESSIONS" && (
          <section aria-label="فهرست جلسات کوچینگ">
            <h2 className={styles.sectionTitle}>جلسات گفت‌وگو و هدایت مربی‌گری</h2>
            {sessions.length === 0 ? (
              <p className={styles.subtitle}>هیچ جلسه کوچینگی برنامه‌ریزی نشده است.</p>
            ) : (
              sessions.map((session) => (
                <article key={session.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>{session.title}</h3>
                    {getSessionBadge(session.status)}
                  </div>

                  <div className={styles.metaRow}>
                    <span className={styles.metaItem}>
                      زمان برنامه‌ریزی: <bdi dir="ltr" className={styles.bdiIsolation}>{session.scheduledAt}</bdi>
                    </span>
                  </div>

                  {session.summary && (
                    <div className={styles.rationaleBox}>
                      <strong>خلاصه مباحث جلسه:</strong>
                      <p style={{ marginTop: "0.4rem", margin: 0 }}>{session.summary}</p>
                    </div>
                  )}

                  {session.notes && session.notes.length > 0 && (
                    <div className={styles.notesList}>
                      <h4 style={{ fontSize: "0.95rem", fontWeight: 700, margin: 0 }}>یادداشت‌های به اشتراک گذاشته‌شده منتور:</h4>
                      {session.notes.map((note) => (
                        <div key={note.id} className={styles.noteItem}>
                          <div className={styles.noteHeader}>
                            <span>نوع یادداشت: {note.noteType}</span>
                            <bdi dir="ltr" className={styles.bdiIsolation}>{note.createdAt}</bdi>
                          </div>
                          <p className={styles.noteContent}>{note.content}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              ))
            )}
          </section>
        )}

        {/* ACTIONS TAB */}
        {activeTab === "ACTIONS" && (
          <section aria-label="فهرست اقدامات عملیاتی پیگیری">
            <h2 className={styles.sectionTitle}>اقدامات تکوینی و تمرین‌های پیگیری</h2>
            {actions.length === 0 ? (
              <p className={styles.subtitle}>در حال حاضر اقدام پیگیری فعالی وجود ندارد.</p>
            ) : (
              actions.map((act) => (
                <article key={act.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>{act.title}</h3>
                    <span className={`${styles.badge} ${act.status === "COMPLETED" ? styles.badgeCompleted : act.status === "SKIPPED" ? styles.badgeSkipped : styles.badgePending}`}>
                      {act.status === "COMPLETED" ? "انجام شد" : act.status === "SKIPPED" ? "صرف‌نظر بدون جریمه" : "در انتظار انجام"}
                    </span>
                  </div>

                  <div className={styles.metaRow}>
                    <span className={styles.metaItem}>
                      مهلت پیشنهادی: <bdi dir="ltr" className={styles.bdiIsolation}>{act.dueDate}</bdi>
                    </span>
                  </div>

                  {act.skipReason && (
                    <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0.5rem 0" }}>
                      دلیل صرف‌نظر: {act.skipReason}
                    </p>
                  )}

                  {act.status === "PENDING" && (
                    <div className={styles.buttonGroup}>
                      <button
                        className={styles.buttonSuccess}
                        onClick={() => onCompleteAction && onCompleteAction(act.id)}
                      >
                        ✓ علامت‌گذاری به عنوان انجام‌شده
                      </button>
                      <button
                        className={styles.buttonSecondary}
                        onClick={() => {
                          const reason = prompt("لطفاً دلیل صرف‌نظر از این گام را بنویسید (بدون هرگونه نمره منفی):");
                          if (reason && onSkipAction) onSkipAction(act.id, reason);
                        }}
                      >
                        صرف‌نظر از این تمرین
                      </button>
                    </div>
                  )}
                </article>
              ))
            )}
          </section>
        )}
      </div>
    </div>
  );
};
