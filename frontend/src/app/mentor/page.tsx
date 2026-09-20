"use client";

import { useState } from "react";
import Link from "next/link";
import { mentorAlphaContent as copy } from "@/content/fa/mentor.alpha";
import {
  Badge,
  IconSparkles,
  IconChat,
  IconCheck,
  IconArrowUp,
  IconClock,
  IconDocument,
  IconLaptop,
  IconShield,
  IconClose,
} from "@/components/ui";
import { useMentorSearch } from "./MentorSearchContext";
import styles from "../student/student.module.css";

interface QueueProject {
  id: string;
  title: string;
  student: string;
  branch: string;
  time: string;
  status: string;
  iconType: "laptop" | "document";
  snippet: string;
}

const initialQueue: QueueProject[] = [
  {
    id: "proj-1",
    title: copy.overview.pendingItem1Title,
    student: "علی محمدی",
    branch: "learning/calc",
    time: "۳۵ دقیقه پیش",
    status: copy.overview.pendingItem1Status,
    iconType: "laptop",
    snippet: `// ماشین‌حساب ماژولار با جاوااسکریپت\nfunction calculate(op, a, b) {\n  switch(op) {\n    case '+': return a + b;\n    case '-': return a - b;\n    case '*': return a * b;\n    case '/': return b !== 0 ? a / b : 'خطای تقسیم بر صفر';\n    default: throw new Error('عملگر نامعتبر');\n  }\n}`
  },
  {
    id: "proj-2",
    title: copy.overview.pendingItem2Title,
    student: "سارا احمدی",
    branch: "auth/token-store",
    time: "۲ ساعت پیش",
    status: copy.overview.pendingItem2Status,
    iconType: "document",
    snippet: `// مدیریت نشست امن با توکن موقت\nexport function saveSession(token) {\n  if (!token) return false;\n  sessionStorage.setItem('cs_demo_token', token);\n  return true;\n}`
  }
];

export default function MentorOverviewPage() {
  const o = copy.overview;
  const {
    searchQuery,
    openSessionModal,
    setOpenSessionModal,
    openReviewModal,
    setOpenReviewModal,
    openGuideModal,
    setOpenGuideModal
  } = useMentorSearch();

  const [activeProject, setActiveProject] = useState<QueueProject>(initialQueue[0]);
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  // Filter projects based on live searchQuery
  const filteredQueue = initialQueue.filter(p => 
    p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.student.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.branch.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.status.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleStartReview = (project?: QueueProject) => {
    setActiveProject(project || initialQueue[0]);
    setFeedbackSubmitted(false);
    setFeedbackText("");
    setOpenReviewModal(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setOpenReviewModal(false);
      setOpenSessionModal(false);
      setOpenGuideModal(false);
    }
  };

  return (
    <div className={styles.studentDashboard} onKeyDown={handleKeyDown} tabIndex={-1}>
      {/* 1. Contextual Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="mentor-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>{o.heroBadge}</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>{o.heroBadgeSecondary}</Badge>
            </div>
            <h1 id="mentor-hero-heading" className={styles.heroHeading}>
              {o.heroHeading}
            </h1>
            <p className={styles.heroSubtitle}>
              {o.heroSubtitle}
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button
              type="button"
              className={styles.heroPrimaryBtn}
              onClick={() => handleStartReview(initialQueue[0])}
            >
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{o.heroActionPrimary}</span>
            </button>
            <button
              type="button"
              className={styles.heroSecondaryBtn}
              onClick={() => setOpenSessionModal(true)}
            >
              <IconChat aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{o.heroActionSecondary}</span>
            </button>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{o.reviewConsoleTitle}</p>
            <span className={styles.heroBrandMini}>{o.reviewConsoleSubtitle}</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{o.check1}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{o.check2}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{o.check3}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{o.check4}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. 4 KPI Metrics Grid for Mentor Review Workload */}
      <section className={styles.kpiGrid} aria-label={o.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi1Title}</span>
            <span className={styles.kpiValue}>{filteredQueue.length} پروژه</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi1Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi2Title}</span>
            <span className={styles.kpiValue}>{o.kpi2Value}</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi2Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <IconClock aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi3Title}</span>
            <span className={styles.kpiValue}>{o.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconLaptop aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi4Title}</span>
            <span className={styles.kpiValue}>{o.kpi4Value}</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi4Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconShield aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Operational Workflow & Review Queue Grid */}
      <section className={styles.twoColumnGrid} aria-label="صف بررسی و تعهدات مربیگری">
        {/* Pending Reviews Queue with Live Filter */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconDocument aria-hidden="true" />
              <span>{o.pendingQueueTitle}</span>
            </h2>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-2)" }}>
              <Badge variant="warning">{filteredQueue.length} مورد فعال</Badge>
              <Link
                href="/mentor/reviews"
                className={styles.actionButton}
                style={{ fontSize: "var(--cs-font-size-caption)", padding: "0.25rem 0.5rem", textDecoration: "none" }}
              >
                صف کامل بررسی
              </Link>
            </div>
          </div>

          {searchQuery && (
            <div style={{
              padding: "var(--cs-space-2) var(--cs-space-3)",
              background: "var(--cs-color-bg-base)",
              borderRadius: "var(--cs-radius-control)",
              fontSize: "var(--cs-font-size-caption)",
              color: "var(--cs-color-text-secondary)",
              display: "flex",
              justifyContent: "space-between"
            }}>
              <span>فیلتر شده بر اساس: «{searchQuery}»</span>
              <span>{filteredQueue.length} نتیجه</span>
            </div>
          )}

          <div className={styles.activityList}>
            {filteredQueue.length > 0 ? (
              filteredQueue.map((item, idx) => (
                <div
                  key={item.id}
                  className={styles.activityItem}
                  style={{ cursor: "pointer", transition: "background var(--cs-motion-fast)" }}
                  onClick={() => handleStartReview(item)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") handleStartReview(item); }}
                  aria-label={`بررسی کد ${item.title}`}
                >
                  <div className={`${styles.activityIconCircle} ${idx === 0 ? styles.kpiCircle1 : styles.kpiCircle2}`}>
                    {item.iconType === "laptop" ? <IconLaptop aria-hidden="true" /> : <IconDocument aria-hidden="true" />}
                  </div>
                  <div className={styles.activityContent} style={{ inlineSize: "100%" }}>
                    <p className={styles.activityDesc} style={{ fontWeight: "var(--cs-font-weight-bold)" }}>{item.title}</p>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBlockStart: "0.25rem" }}>
                      <span className={styles.activityTime}>{item.student} — {item.branch} • {item.time}</span>
                      <Badge variant="outline">{item.status}</Badge>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div style={{
                textAlign: "center",
                padding: "var(--cs-space-8) var(--cs-space-4)",
                color: "var(--cs-color-text-muted)"
              }}>
                <IconDocument aria-hidden="true" style={{ inlineSize: "2rem", blockSize: "2rem", margin: "0 auto var(--cs-space-2)" }} />
                <p style={{ margin: 0, fontWeight: "var(--cs-font-weight-bold)" }}>نتیجه‌ای برای جستجوی شما یافت نشد</p>
                <p style={{ margin: "var(--cs-space-1) 0 0", fontSize: "var(--cs-font-size-caption)" }}>عبارت دیگری را جستجو کنید یا فیلتر را پاک نمایید.</p>
              </div>
            )}
          </div>
        </div>

        {/* Mentor Governance & Review Environment Focus */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconShield aria-hidden="true" />
              <span>{o.feedbackFocusTitle}</span>
            </h2>
            <Badge variant="primary">استاندارد راهبری</Badge>
          </div>
          <p className={styles.cardText}>{o.feedbackFocusDesc}</p>
          <div style={{
            background: "var(--cs-color-bg-base)",
            padding: "var(--cs-space-3) var(--cs-space-4)",
            borderRadius: "var(--cs-radius-control)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>
              {o.feedbackComplianceLabel}
            </span>
            <span style={{ fontSize: "var(--cs-font-size-caption)", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-success-foreground)" }}>
              {o.feedbackComplianceValue}
            </span>
          </div>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <button
              className={`${styles.actionButton} ${styles.primaryActionButton}`}
              type="button"
              onClick={() => handleStartReview(initialQueue[0])}
            >
              {o.actionStartReview}
            </button>
          </div>
        </div>
      </section>

      {/* 4. Interactive Modal 1: Code Review Environment */}
      {openReviewModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenReviewModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="review-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="review-modal-title" className={styles.modalTitle}>
                <IconLaptop aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>محیط ارزیابی کد: {activeProject.title}</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenReviewModal(false)}
                aria-label="بستن پنجره بازبینی"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "var(--cs-font-size-caption)" }}>
              <span>کارآموز: <strong>{activeProject.student}</strong></span>
              <span>شاخه گیت: <code>{activeProject.branch}</code></span>
              <Badge variant="warning">{activeProject.status}</Badge>
            </div>

            <div style={{
              background: "#0f172a",
              color: "#e2e8f0",
              padding: "var(--cs-space-4)",
              borderRadius: "var(--cs-radius-control)",
              fontFamily: "monospace",
              direction: "ltr",
              fontSize: "0.8125rem",
              lineHeight: 1.5,
              overflowX: "auto"
            }}>
              <pre style={{ margin: 0 }}>{activeProject.snippet}</pre>
            </div>

            <div>
              <label htmlFor="mentor-feedback-input" style={{ display: "block", fontSize: "var(--cs-font-size-caption)", fontWeight: "var(--cs-font-weight-bold)", marginBlockEnd: "var(--cs-space-2)" }}>
                بازخورد مهندسی و راهنمایی فنی منتور:
              </label>
              <textarea
                id="mentor-feedback-input"
                style={{
                  inlineSize: "100%",
                  minBlockSize: "5rem",
                  padding: "var(--cs-space-3)",
                  borderRadius: "var(--cs-radius-control)",
                  border: "var(--cs-border-width) solid var(--cs-color-border-subtle)",
                  background: "var(--cs-color-bg-base)",
                  color: "var(--cs-color-text-primary)",
                  fontFamily: "inherit",
                  fontSize: "var(--cs-font-size-body)",
                  resize: "vertical"
                }}
                placeholder="نقاط قوت کد، موارد نیازمند بازنویسی بر مبنای استانداردهای Clean Code و راهنمایی گام بعدی را ثبت نمایید..."
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
              />
            </div>

            {feedbackSubmitted && (
              <div style={{
                background: "rgba(16, 185, 129, 0.12)",
                color: "var(--cs-color-success)",
                border: "1px solid rgba(16, 185, 129, 0.25)",
                borderRadius: "var(--cs-radius-control)",
                padding: "var(--cs-space-3)",
                fontSize: "var(--cs-font-size-caption)",
                display: "flex",
                alignItems: "center",
                gap: "var(--cs-space-2)"
              }}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "1rem", blockSize: "1rem" }} />
                <span>بازخورد شما با موفقیت ثبت شد و وضعیت پروژه به «بررسی‌شده» تغییر یافت.</span>
              </div>
            )}

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "var(--cs-space-3)", marginBlockStart: "var(--cs-space-2)" }}>
              <button
                type="button"
                className={styles.actionButton}
                onClick={() => setOpenReviewModal(false)}
              >
                انصراف
              </button>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setFeedbackSubmitted(true)}
              >
                ثبت بازخورد و تایید گام
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. Interactive Modal 2: Today's Online Mentoring Sessions */}
      {openSessionModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenSessionModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="session-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="session-modal-title" className={styles.modalTitle}>
                <IconClock aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>برنامه جلسات رفع اشکال آنلاین امروز</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenSessionModal(false)}
                aria-label="بستن پنجره جلسات"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <p style={{ margin: 0, fontSize: "var(--cs-font-size-body)", color: "var(--cs-color-text-secondary)" }}>
              جلسات هماهنگ‌شده با کارآموزان جهت رفع گره‌های فنی و مرور معماری پروژه‌ها:
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)" }}>
              <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "var(--cs-space-3) var(--cs-space-4)",
                background: "var(--cs-color-bg-base)",
                borderRadius: "var(--cs-radius-control)",
                border: "var(--cs-border-width) solid var(--cs-color-border-subtle)"
              }}>
                <div>
                  <strong style={{ display: "block" }}>جلسه رفع اشکال معماری کامپوننت‌ها</strong>
                  <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-muted)" }}>کارآموز: رضا حسینی • ساعت ۱۷:۰۰ الی ۱۷:۴۵</span>
                </div>
                <Badge variant="primary">آماده برگزاری</Badge>
              </div>

              <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "var(--cs-space-3) var(--cs-space-4)",
                background: "var(--cs-color-bg-base)",
                borderRadius: "var(--cs-radius-control)",
                border: "var(--cs-border-width) solid var(--cs-color-border-subtle)"
              }}>
                <div>
                  <strong style={{ display: "block" }}>بررسی نهایی پروژه پورتفولیو و استقرار</strong>
                  <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-muted)" }}>کارآموز: مریم کاظمی • ساعت ۱۹:۱۵ الی ۲۰:۰۰</span>
                </div>
                <Badge variant="outline">برنامه‌ریزی‌شده</Badge>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenSessionModal(false)}
              >
                متوجه شدم
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 6. Interactive Modal 3: Mentor Governance Guidelines */}
      {openGuideModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenGuideModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="guide-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="guide-modal-title" className={styles.modalTitle}>
                <IconShield aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>شیوه‌نامه منتوری و اصول بازخورد سازنده</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenGuideModal(false)}
                aria-label="بستن شیوه‌نامه"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)", fontSize: "var(--cs-font-size-body)", lineHeight: 1.6 }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--cs-space-2)" }}>
                <IconCheck aria-hidden="true" style={{ color: "var(--cs-color-success)", marginBlockStart: "0.25rem" }} />
                <span><strong>هدایت به‌جای تحمیل پاسخ:</strong> منتور نباید کد نهایی را مستقیماً بنویسد؛ راهنمایی با طرح سوال و اشاره به مستندات رسمی انجام می‌شود.</span>
              </div>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--cs-space-2)" }}>
                <IconCheck aria-hidden="true" style={{ color: "var(--cs-color-success)", marginBlockStart: "0.25rem" }} />
                <span><strong>لحن سازنده و محترمانه:</strong> مقایسه کارآموزان با یکدیگر یا تحقیر اشتباهات کدنویسی مطلقاً ممنوع است.</span>
              </div>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--cs-space-2)" }}>
                <IconCheck aria-hidden="true" style={{ color: "var(--cs-color-success)", marginBlockStart: "0.25rem" }} />
                <span><strong>حفظ حریم خصوصی:</strong> کلیه مکاتبات و تبادل کد در بستر کنترل‌شده CodeSho نگهداری می‌شود.</span>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenGuideModal(false)}
              >
                تایید و بستن
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
