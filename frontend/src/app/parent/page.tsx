"use client";

import { useState } from "react";
import Link from "next/link";
import { parentAlphaContent as copy } from "@/content/fa/parent.alpha";
import {
  Badge,
  IconSparkles,
  IconChat,
  IconCheck,
  IconArrowUp,
  IconClock,
  IconDocument,
  IconFire,
  IconCalendar,
  IconShield,
  IconLaptop,
  IconClose,
} from "@/components/ui";
import { useParentSearch } from "./ParentSearchContext";
import styles from "../student/student.module.css";

interface Milestone {
  id: string;
  title: string;
  date: string;
  status: string;
  type: string;
}

const initialMilestones: Milestone[] = [
  {
    id: "m-1",
    title: copy.overview.milestone1Title,
    date: copy.overview.milestone1Date,
    status: copy.overview.milestone1Status,
    type: "front-end"
  },
  {
    id: "m-2",
    title: copy.overview.milestone2Title,
    date: copy.overview.milestone2Date,
    status: copy.overview.milestone2Status,
    type: "programming"
  }
];

export default function ParentOverviewPage() {
  const o = copy.overview;
  const {
    searchQuery,
    openWeeklyReportModal,
    setOpenWeeklyReportModal,
    openMentorChatModal,
    setOpenMentorChatModal,
    openConsentModal,
    setOpenConsentModal,
    selectedChild,
    setSelectedChild,
  } = useParentSearch();

  const [consentGranted, setConsentGranted] = useState(true);
  const [chatMessage, setChatMessage] = useState("");
  const [chatSent, setChatSent] = useState(false);

  const filteredMilestones = initialMilestones.filter(m =>
    m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.status.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={styles.studentDashboard}>
      {/* 0. Multi-Child Selector Banner */}
      <div className={styles.childSelectorBanner}>
        <div className={styles.childSelectorInfo}>
          <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)", fontWeight: "var(--cs-font-weight-medium)" }}>
            {o.childSelectLabel}
          </span>
          <select
            value={selectedChild}
            onChange={(e) => setSelectedChild(e.target.value)}
            style={{
              fontSize: "var(--cs-font-size-body)",
              fontWeight: "var(--cs-font-weight-bold)",
              color: "var(--cs-color-text-primary)",
              background: "transparent",
              border: "1px solid var(--cs-color-border-subtle)",
              borderRadius: "var(--cs-radius-control)",
              padding: "0.25rem 0.5rem",
              cursor: "pointer"
            }}
            aria-label={o.childSelectLabel}
          >
            <option value="علی محمدی (پایه دهم ریاضی)">علی محمدی (پایه دهم ریاضی)</option>
            <option value="مریم محمدی (پایه هفتم)">مریم محمدی (پایه هفتم)</option>
          </select>
        </div>
        <Badge variant="primary" className={styles.childSelectorBadge}>
          {o.selectedChildBadge}
        </Badge>
      </div>

      {/* 1. Contextual Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="parent-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>{o.heroBadge}</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>حریم خصوصی تضمین‌شده</Badge>
            </div>
            <h1 id="parent-hero-heading" className={styles.heroHeading}>
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
              onClick={() => setOpenWeeklyReportModal(true)}
            >
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{o.heroActionPrimary}</span>
            </button>
            <button
              type="button"
              className={styles.heroSecondaryBtn}
              onClick={() => setOpenMentorChatModal(true)}
            >
              <IconChat aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{o.heroActionSecondary}</span>
            </button>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{o.oversightQuote}</p>
            <span className={styles.heroBrandMini}>{o.oversightNote}</span>
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

      {/* 2. 4 KPI Metrics Grid for Parent Oversight */}
      <section className={styles.kpiGrid} aria-label={o.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi1Title}</span>
            <span className={styles.kpiValue}>{o.kpi1Value}</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi1Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconClock aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
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
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi3Title}</span>
            <span className={styles.kpiValue}>{o.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <IconFire aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconCalendar aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
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

      {/* 3. Operational Workflow & Oversight Grid */}
      <section className={styles.twoColumnGrid} aria-label="روند و دستاوردها">
        {/* Recent Milestones */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconLaptop aria-hidden="true" />
              <span>{o.recentMilestonesTitle}</span>
            </h2>
            <Badge variant="success">تأییدشده</Badge>
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
              <span>{filteredMilestones.length} مورد</span>
            </div>
          )}

          <div className={styles.activityList}>
            {filteredMilestones.length > 0 ? (
              filteredMilestones.map((item, idx) => (
                <div key={item.id} className={styles.activityItem}>
                  <div className={`${styles.activityIconCircle} ${idx === 0 ? styles.kpiCircle1 : styles.kpiCircle2}`}>
                    <IconCheck aria-hidden="true" />
                  </div>
                  <div className={styles.activityContent} style={{ inlineSize: "100%" }}>
                    <p className={styles.activityDesc} style={{ fontWeight: "var(--cs-font-weight-bold)" }}>{item.title}</p>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span className={styles.activityTime}>{item.date}</span>
                      <Badge variant="outline">{item.status}</Badge>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: "center", padding: "var(--cs-space-6) var(--cs-space-4)", color: "var(--cs-color-text-muted)" }}>
                <p style={{ margin: 0, fontWeight: "var(--cs-font-weight-bold)" }}>نتیجه‌ای برای جستجو یافت نشد</p>
              </div>
            )}
          </div>
        </div>

        {/* Consent & Oversight Management */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconShield aria-hidden="true" />
              <span>{o.safetyTitle}</span>
            </h2>
            <Badge variant="primary">سیاست حاکمیتی</Badge>
          </div>
          <p className={styles.cardText}>{o.safetyDescription}</p>
          <div style={{
            background: "var(--cs-color-bg-base)",
            padding: "var(--cs-space-3) var(--cs-space-4)",
            borderRadius: "var(--cs-radius-control)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>
              {o.consentStatusLabel}
            </span>
            <span style={{
              fontSize: "var(--cs-font-size-caption)",
              fontWeight: "var(--cs-font-weight-bold)",
              color: consentGranted ? "var(--cs-color-success-foreground)" : "var(--cs-color-danger-foreground)"
            }}>
              {consentGranted ? o.consentStatusValue : "غیرفعال (محدودشده توسط والد)"}
            </span>
          </div>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <button
              className={`${styles.actionButton} ${styles.primaryActionButton}`}
              type="button"
              onClick={() => setOpenConsentModal(true)}
            >
              {o.actionManageConsent}
            </button>
          </div>
        </div>
      </section>

      {/* Modal 1: Weekly Progress Report */}
      {openWeeklyReportModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenWeeklyReportModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="report-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="report-modal-title" className={styles.modalTitle}>
                <IconDocument aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>کارنامه و گزارش تحلیلی پیشرفت هفتگی</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenWeeklyReportModal(false)}
                aria-label="بستن گزارش"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <p style={{ margin: 0, fontSize: "var(--cs-font-size-body)", color: "var(--cs-color-text-secondary)" }}>
              گزارش عملکرد فرزند گرامی شما ({selectedChild}) در هفته جاری:
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)" }}>
              <div style={{ padding: "var(--cs-space-3)", background: "var(--cs-color-bg-base)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>زمان یادگیری متمرکز:</strong> ۱۲ ساعت و ۴۵ دقیقه (افزایش ۱۵٪ نسبت به هفته قبل)
              </div>
              <div style={{ padding: "var(--cs-space-3)", background: "var(--cs-color-bg-base)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>تمرین‌های کدنویسی تکمیل‌شده:</strong> ۸ پروژه کوچک و ۱ ارزیابی میان‌دوره
              </div>
              <div style={{ padding: "var(--cs-space-3)", background: "var(--cs-color-bg-base)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>تاییدیه سلامت و اخلاق تعاملی:</strong> ۱۰۰٪ بدون هیچ‌گونه هشدار یا نقض قوانین
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenWeeklyReportModal(false)}
              >
                بستن کارنامه
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal 2: Contact Mentor */}
      {openMentorChatModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenMentorChatModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="mentor-chat-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="mentor-chat-modal-title" className={styles.modalTitle}>
                <IconChat aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>ارتباط مستقیم با منتور آموزشی</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenMentorChatModal(false)}
                aria-label="بستن پنجره پیام"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <p style={{ margin: 0, fontSize: "var(--cs-font-size-body)", color: "var(--cs-color-text-secondary)" }}>
              پیام شما مستقیماً به منتور مسئول ({selectedChild}) ارسال خواهد شد و در سامانه نظارتی ثبت می‌گردد:
            </p>

            <textarea
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
              placeholder="پرسش، نکته یا توصیه مدنظرتان در خصوص روند یادگیری را بنویسید..."
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
            />

            {chatSent && (
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
                <span>پیام شما به منتور ارسال شد و پاسخ آن از طریق پنل اعلانات دریافت خواهد شد.</span>
              </div>
            )}

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "var(--cs-space-2)", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={styles.actionButton}
                onClick={() => setOpenMentorChatModal(false)}
              >
                انصراف
              </button>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setChatSent(true)}
              >
                ارسال پیام
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal 3: Consent & Privacy Policy Management */}
      {openConsentModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenConsentModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="consent-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="consent-modal-title" className={styles.modalTitle}>
                <IconShield aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>مدیریت رضایت‌نامه و مجوزهای نظارت والد</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenConsentModal(false)}
                aria-label="بستن پنجره رضایت‌نامه"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)", fontSize: "var(--cs-font-size-body)" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-2)", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={consentGranted}
                  onChange={(e) => setConsentGranted(e.target.checked)}
                  style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }}
                />
                <span>مجوز شرکت در کلاس‌های تعاملی آنلاین و نظارت بر کدهای بارگذاری‌شده</span>
              </label>

              <p style={{ margin: 0, fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-muted)", lineHeight: 1.6 }}>
                بر اساس قوانین پلتفرم کدشو، عدم تایید این مجوز دسترسی دانش‌آموز را به بخش تعامل زنده و ارسال پروژه‌ها برای داوری محدود می‌کند.
              </p>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenConsentModal(false)}
              >
                ذخیره تنظیمات رضایت‌نامه
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
