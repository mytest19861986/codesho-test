"use client";

import { useState } from "react";
import Link from "next/link";
import { mentorAlphaContent as copy } from "@/content/fa/mentor.alpha";
import {
  Badge,
  IconSparkles,
  IconDocument,
  IconLaptop,
  IconCheck,
  IconClock,
  IconShield,
  IconClose,
  IconArrowUp,
} from "@/components/ui";
import { useMentorSearch } from "../MentorSearchContext";
import styles from "../../student/student.module.css";

interface QueueProject {
  id: string;
  title: string;
  student: string;
  branch: string;
  time: string;
  status: string;
  iconType: "laptop" | "document";
  priority: "high" | "normal";
  snippet: string;
}

const detailedQueue: QueueProject[] = [
  {
    id: "proj-1",
    title: copy.overview.pendingItem1Title,
    student: "علی محمدی",
    branch: "learning/calc",
    time: "۳۵ دقیقه پیش",
    status: copy.overview.pendingItem1Status,
    iconType: "laptop",
    priority: "high",
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
    priority: "normal",
    snippet: `// مدیریت نشست امن با توکن موقت\nexport function saveSession(token) {\n  if (!token) return false;\n  sessionStorage.setItem('cs_demo_token', token);\n  return true;\n}`
  },
  {
    id: "proj-3",
    title: "پیاده‌سازی کامپوننت مودال بدون نشت رویداد در DOM",
    student: "رضا اکبری",
    branch: "ui/accessible-modal",
    time: "۳ ساعت پیش",
    status: "در انتظار بازخورد منتور",
    iconType: "laptop",
    priority: "normal",
    snippet: `// مدیریت فوکوس و Escape در مودال\nuseEffect(() => {\n  const onKey = (e) => { if (e.key === 'Escape') onClose(); };\n  window.addEventListener('keydown', onKey);\n  return () => window.removeEventListener('keydown', onKey);\n}, [onClose]);`
  },
  {
    id: "proj-4",
    title: "اعتبارسنجی فرم با رعایت استانداردهای دسترسی‌پذیری (a11y)",
    student: "مهسا کریمی",
    branch: "forms/aria-validation",
    time: "۵ ساعت پیش",
    status: "در انتظار تایید نهایی",
    iconType: "document",
    priority: "normal",
    snippet: `// اعتبارسنجی فیلد ایمیل با خروجی صوتی و متنی\nexport function validateEmail(val) {\n  const valid = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(val);\n  return { valid, error: valid ? null : 'فرمت ایمیل نامعتبر است' };\n}`
  }
];

export default function MentorReviewsPage() {
  const o = copy.overview;
  const { searchQuery, openReviewModal, setOpenReviewModal } = useMentorSearch();

  const [activeProject, setActiveProject] = useState<QueueProject>(detailedQueue[0]);
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [activeFilter, setActiveFilter] = useState<"all" | "high" | "normal">("all");

  const filteredQueue = detailedQueue.filter((p) => {
    const matchesSearch =
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.student.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.branch.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.status.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = activeFilter === "all" || p.priority === activeFilter;
    return matchesSearch && matchesFilter;
  });

  const handleStartReview = (project: QueueProject) => {
    setActiveProject(project);
    setFeedbackSubmitted(false);
    setFeedbackText("");
    setOpenReviewModal(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setOpenReviewModal(false);
    }
  };

  return (
    <div className={styles.studentDashboard} onKeyDown={handleKeyDown} tabIndex={-1}>
      {/* 1. Contextual Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="reviews-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>صف تخصصی بازخورد</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>استاندارد Clean Code</Badge>
            </div>
            <h1 id="reviews-hero-heading" className={styles.heroHeading}>
              صف بازخورد و ارزیابی پروژه‌های کارآموزان
            </h1>
            <p className={styles.heroSubtitle}>
              کدهای تحویلی کارآموزان را بررسی کنید، ساختار فایل‌ها را محک بزنید و رهنمودهای فنی مبتنی بر Clean Architecture ارائه دهید.
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button
              type="button"
              className={styles.heroPrimaryBtn}
              onClick={() => handleStartReview(detailedQueue[0])}
            >
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>شروع بررسی اولین پروژه صف ({detailedQueue[0].student})</span>
            </button>
            <Link href="/mentor" className={styles.heroSecondaryBtn}>
              <span>بازگشت به میز کار اصلی</span>
            </Link>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{o.reviewConsoleTitle}</p>
            <span className={styles.heroBrandMini}>{o.reviewConsoleSubtitle}</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>بررسی عمیق منطق و الگوریتم‌ها</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>رعایت اصول نام‌گذاری و ماژولار بودن</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>پرهیز از نمره‌دهی مقایسه‌ای مخرب</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. 4 KPI Metrics Grid */}
      <section className={styles.kpiGrid} aria-label="شاخص‌های صف ارزیابی">
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>کل موارد در صف بازخورد</span>
            <span className={styles.kpiValue}>{detailedQueue.length} پروژه</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>۲ مورد با اولویت بالا</span>
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
            <span className={styles.kpiLabel}>میانگین زمان بررسی کد</span>
            <span className={styles.kpiValue}>۱۸ دقیقه</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>پوشش کامل تست و بازنویسی</span>
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
            <span className={styles.kpiLabel}>نرخ تایید در گام اول</span>
            <span className={styles.kpiValue}>۷۶٪</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>کیفیت بالای پروژه‌ها</span>
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
            <span className={styles.kpiLabel}>شاخص هدایت کیفی</span>
            <span className={styles.kpiValue}>۹۹٪</span>
            <span className={styles.kpiSub}>
              <IconShield aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>مطابق منشور ارزیابی</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconShield aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Filter Controls & Detailed Reviews Table/Queue */}
      <section className={styles.cardPanel} aria-label="فهرست و صف کامل پروژه‌ها">
        <div className={styles.panelHeader}>
          <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
            <IconDocument aria-hidden="true" />
            <span>پروژه‌های منتظر دریافت بازخورد ({filteredQueue.length} پروژه)</span>
          </h2>
          <div style={{ display: "flex", gap: "var(--cs-space-2)" }}>
            <button
              type="button"
              onClick={() => setActiveFilter("all")}
              className={styles.panelFilter}
              style={{
                cursor: "pointer",
                background: activeFilter === "all" ? "var(--cs-color-brand-primary)" : "var(--cs-color-bg-base)",
                color: activeFilter === "all" ? "var(--cs-color-text-inverse)" : "var(--cs-color-text-secondary)"
              }}
            >
              همه پروژه‌ها
            </button>
            <button
              type="button"
              onClick={() => setActiveFilter("high")}
              className={styles.panelFilter}
              style={{
                cursor: "pointer",
                background: activeFilter === "high" ? "var(--cs-color-brand-primary)" : "var(--cs-color-bg-base)",
                color: activeFilter === "high" ? "var(--cs-color-text-inverse)" : "var(--cs-color-text-secondary)"
              }}
            >
              اولویت بالا
            </button>
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
            <span>فیلتر جستجو: «{searchQuery}»</span>
            <span>{filteredQueue.length} نتیجه</span>
          </div>
        )}

        <div className={styles.activityList}>
          {filteredQueue.length > 0 ? (
            filteredQueue.map((item, idx) => (
              <div
                key={item.id}
                className={styles.activityItem}
                style={{
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--cs-space-3) var(--cs-space-4)",
                  border: "var(--cs-border-width) solid var(--cs-color-border-subtle)"
                }}
                onClick={() => handleStartReview(item)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") handleStartReview(item);
                }}
                aria-label={`بررسی کد ${item.title}`}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-3)" }}>
                  <div className={`${styles.activityIconCircle} ${item.priority === "high" ? styles.kpiCircle1 : styles.kpiCircle3}`}>
                    {item.iconType === "laptop" ? <IconLaptop aria-hidden="true" /> : <IconDocument aria-hidden="true" />}
                  </div>
                  <div className={styles.activityContent}>
                    <p className={styles.activityDesc} style={{ fontWeight: "var(--cs-font-weight-bold)", fontSize: "var(--cs-font-size-body)" }}>
                      {item.title}
                    </p>
                    <span className={styles.activityTime}>
                      {item.student} • شاخه: <code>{item.branch}</code> • زمان تحویل: {item.time}
                    </span>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-3)" }}>
                  <Badge variant={item.priority === "high" ? "warning" : "outline"}>{item.status}</Badge>
                  <button
                    type="button"
                    className={`${styles.actionButton} ${styles.primaryActionButton}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleStartReview(item);
                    }}
                  >
                    شروع بررسی
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: "center", padding: "var(--cs-space-8) var(--cs-space-4)", color: "var(--cs-color-text-muted)" }}>
              <IconDocument aria-hidden="true" style={{ inlineSize: "2rem", blockSize: "2rem", margin: "0 auto var(--cs-space-2)" }} />
              <p style={{ margin: 0, fontWeight: "var(--cs-font-weight-bold)" }}>موردی مطابق با جستجوی شما یافت نشد</p>
            </div>
          )}
        </div>
      </section>

      {/* 4. Interactive Modal: Code Review Environment */}
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
    </div>
  );
}
