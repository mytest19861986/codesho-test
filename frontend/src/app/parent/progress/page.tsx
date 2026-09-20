"use client";

import { useState } from "react";
import Link from "next/link";
import { parentAlphaContent as copy } from "@/content/fa/parent.alpha";
import {
  Badge,
  IconSparkles,
  IconClock,
  IconTrending,
  IconCheck,
  IconClose,
  IconDocument,
  IconLaptop,
  IconArrowUp,
  IconStar,
} from "@/components/ui";
import { useParentSearch } from "../ParentSearchContext";
import styles from "../../student/student.module.css";

export default function ParentProgressPage() {
  const o = copy.overview;
  const { searchQuery, selectedChild } = useParentSearch();
  const [openModal, setOpenModal] = useState(false);

  const reportModules = [
    {
      id: "mod-1",
      title: "ماژول اول: مبانی تعاملی جاوااسکریپت و DOM",
      progress: 100,
      score: "عالی (تأیید منتور)",
      timeSpent: "۱۸ ساعت",
      status: "تکمیل شده",
    },
    {
      id: "mod-2",
      title: "ماژول دوم: کامپوننت‌های مدرن و مدیریت State",
      progress: 85,
      score: "بسیار خوب",
      timeSpent: "۱۴ ساعت",
      status: "در حال مطالعه",
    },
    {
      id: "mod-3",
      title: "ماژول سوم: معماری ماژولار و پروژه‌های واقعی Clean Code",
      progress: 40,
      score: "در حال بررسی پروژه",
      timeSpent: "۸ ساعت",
      status: "در حال پیشرفت",
    },
  ];

  const filteredModules = reportModules.filter((m) =>
    m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.status.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="progress-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>گزارش پیشرفت تحصیلی</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>پایش رشد بدون رتبه‌بندی مخرب</Badge>
            </div>
            <h1 id="progress-hero-heading" className={styles.heroHeading}>
              کارنامه تحلیلی و روند یادگیری فرزند
            </h1>
            <p className={styles.heroSubtitle}>
              مشاهده دقیق استمرار مطالعه، ساعات یادگیری هفتگی، نرخ تسلط بر مفاهیم و تاییدیه‌های فنی منتور ارشد برای {selectedChild}.
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button
              type="button"
              className={styles.heroPrimaryBtn}
              onClick={() => setOpenModal(true)}
            >
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>مشاهده کارنامه جامع ماه</span>
            </button>
            <Link href="/parent" className={styles.heroSecondaryBtn} style={{ textDecoration: "none" }}>
              <IconLaptop aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>بازگشت به نمای کلی</span>
            </Link>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>«رشد پیوسته با بازخورد سازنده»</p>
            <span className={styles.heroBrandMini}>تحلیل دقیق عملکرد بر مبنای توانمندی فردی</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>تسلط بر پروژه‌های کاربردی</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>عدم اضطراب نمره‌دهی مقایسه‌ای</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. KPI Cards */}
      <section className={styles.kpiGrid} aria-label="شاخص‌های پیشرفت فرزند">
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
              <IconTrending aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconTrending aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>شاخص تسلط مفاهیم</span>
            <span className={styles.kpiValue}>۹۴٪</span>
            <span className={styles.kpiSub}>
              <IconStar aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>ارزیابی مفهومی منتور</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconStar aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Progress Details List */}
      <section className={styles.cardPanel} aria-label="سرفصل‌های آموزشی">
        <div className={styles.panelHeader}>
          <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
            <IconTrending aria-hidden="true" />
            <span>جزئیات یادگیری و ماژول‌های آموزشی {selectedChild}</span>
          </h2>
          <Badge variant="primary">{filteredModules.length} سرفصل</Badge>
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
            <span>{filteredModules.length} نتیجه</span>
          </div>
        )}

        <div className={styles.activityList}>
          {filteredModules.map((m, idx) => (
            <div key={m.id} className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${idx === 0 ? styles.kpiCircle1 : styles.kpiCircle2}`}>
                <IconCheck aria-hidden="true" />
              </div>
              <div className={styles.activityContent} style={{ inlineSize: "100%" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <p className={styles.activityDesc} style={{ fontWeight: "var(--cs-font-weight-bold)", margin: 0 }}>
                    {m.title}
                  </p>
                  <Badge variant={m.progress === 100 ? "success" : "outline"}>
                    {m.status}
                  </Badge>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBlockStart: "0.25rem" }}>
                  <span className={styles.activityTime}>مدت تمرین: {m.timeSpent} • ارزیابی: {m.score}</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--cs-color-brand-primary)", fontWeight: "bold" }}>{m.progress}٪ تکمیل</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Modal: Full Progress Summary */}
      {openModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="prog-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="prog-modal-title" className={styles.modalTitle}>
                <IconDocument aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>کارنامه جامع یادگیری فرزند</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenModal(false)}
                aria-label="بستن پنجره"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)" }}>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>دانش‌آموز:</strong> <span>{selectedChild}</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>استمرار حضور:</strong> <span>۱۲ روز بدون وقفه با استمرار عالی</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>تکالیف تحویل داده شده:</strong> <span>۲۴ تکلیف موفق، تماماً با تایید مربی ارشد</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>توصیه منتور:</strong> <span>پیشرفت علی بسیار چشمگیر است؛ پیشنهاد می‌شود ماژول بعدی را با تمرین‌های چالشی‌تر ادامه دهد.</span>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenModal(false)}
              >
                متوجه شدم
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
